"""
Week 7 - server.py  :  Room 객체 + 저장소(Repository) 주입
------------------------------------------------------------
6주차의 전역 딕셔너리 세 개가 사라졌습니다.
  - 방의 멤버·기록은 Room 객체가 스스로 책임진다
  - 방을 어디에 저장할지는 RoomRepository 부품에 맡긴다(주입)

저장소를 InMemory ↔ File 로 바꿔 끼우면,
서버 코드를 안 고치고도 '재시작 후 방 유지'를 켜고 끌 수 있다.
------------------------------------------------------------
명령: /create 방, /join 방, /leave, /rooms, /who
"""

import socket
import threading

from codec import AesGcmCodec
from messages import TextMessage, SystemMessage
from repository import InMemoryRoomRepository, FileRoomRepository

HOST = "127.0.0.1"
PORT = 5000
CODEC = AesGcmCodec()   # AES-256-GCM (6주차부터 평문 제거). 클라이언트도 같은 codec/암호여야 통함

# ── 조립(Composition Root): 저장소를 골라 '주입' ──
#   FileRoomRepository("rooms.json") 로 바꾸면 재시작해도 방이 남는다.
# REPO = InMemoryRoomRepository()
REPO = FileRoomRepository()


# 접속별 가벼운 정보 (8주차에 Session 객체로 정리 예정)
nickname_of = {}        # conn -> nickname
room_of = {}            # conn -> Room (없으면 None)
lock = threading.Lock()


def send_to(conn, message):
    try:
        conn.sendall(CODEC.encode(message))
    except OSError:
        pass


def handle_command(conn, text):
    parts = text.split(" ", 1)
    cmd = parts[0]
    arg = parts[1].strip() if len(parts) > 1 else ""
    nickname = nickname_of[conn]

    # 방 이름이 필요한 명령인데 이름을 안 적었으면 막는다 (빈 이름 방 생성 방지)
    if cmd in ("/create", "/join") and not arg:
        send_to(conn, SystemMessage(f"방 이름을 함께 적어주세요:  {cmd} 방이름"))
        return

    if cmd == "/create":
        with lock:
            if REPO.find(arg):
                send_to(conn, SystemMessage(f"이미 있는 방입니다: {arg}"))
                return
            REPO.create(arg)
        send_to(conn, SystemMessage(f"방을 만들었습니다: {arg}  (/join {arg})"))

    elif cmd == "/join":
        with lock:
            room = REPO.find(arg)
            if room is None:
                send_to(conn, SystemMessage(f"없는 방입니다: {arg}  (/create {arg} 먼저)"))
                return
            old = room_of.get(conn)
            if old:                         # 이전 방에서 나가기 (Room 이 알아서)
                old.leave(conn)
                REPO.save(old)
            room.join(conn, nickname)       # 새 방 입장 (Room 이 알아서)
            room_of[conn] = room
            REPO.save(room)
        if old:
            old.deliver(SystemMessage(f"*** {nickname}님이 방을 나갔습니다 ***"), send_to)
        room.deliver(SystemMessage(f"*** {nickname}님이 입장했습니다 ***"), send_to)

    elif cmd == "/leave":
        with lock:
            room = room_of.get(conn)
            if room:
                room.leave(conn)
                REPO.save(room)
                room_of[conn] = None
        if room:
            room.deliver(SystemMessage(f"*** {nickname}님이 방을 나갔습니다 ***"), send_to)
            send_to(conn, SystemMessage(f"방에서 나왔습니다: {room.name}"))

    elif cmd == "/rooms":
        with lock:
            entries = [f"{r.name}({len(r.members)}명)" for r in REPO.all()]
        send_to(conn, SystemMessage("방 목록: " + (", ".join(entries) if entries else "(없음)")))

    elif cmd == "/who":
        room = room_of.get(conn)
        if room:
            send_to(conn, SystemMessage(f"[{room.name}] 멤버: " + ", ".join(room.member_names())))
        else:
            send_to(conn, SystemMessage("아직 방에 없습니다. /join 방이름"))

    else:
        send_to(conn, SystemMessage(f"알 수 없는 명령: {cmd}"))


def handle(conn, addr):
    reader = conn.makefile("r", encoding="utf-8")
    nickname = (reader.readline() or "").strip()
    if not nickname:
        conn.close()
        return

    with lock:
        nickname_of[conn] = nickname
        room_of[conn] = None
    print(f"[서버] {nickname} 접속")
    send_to(conn, SystemMessage("명령: /create 방, /join 방, /leave, /rooms, /who"))

    try:
        while True:
            line = reader.readline()
            if not line:
                break
            try:
                msg = CODEC.decode(line.rstrip("\n"))   # 해독 (다른 키·손상된 줄이면 예외)
            except Exception:
                continue                                # 해독 실패한 줄은 무시, 연결은 유지

            if isinstance(msg, TextMessage) and msg.text.startswith("/"):
                handle_command(conn, msg.text)
                continue

            room = room_of.get(conn)
            if not room:
                send_to(conn, SystemMessage("먼저 /join 으로 방에 들어가세요."))
                continue
            msg.sender = nickname_of[conn]
            room.post(msg, send_to)           # Room 이 기록 + 멤버에게 전송
            REPO.save(room)
    except OSError:
        pass

    # 퇴장: Room 에게 맡기면 끝 (전역 세 군데 청소가 사라졌다)
    with lock:
        room = room_of.pop(conn, None)
        if room:
            room.leave(conn)
            REPO.save(room)
        name = nickname_of.pop(conn, "?")
    if room:
        room.deliver(SystemMessage(f"*** {name}님이 나갔습니다 ***"), send_to)
    conn.close()
    print(f"[서버] {name} 퇴장")


def main():
    print(f"[조립] 저장소 = {type(REPO).__name__}")
    existing = [r.name for r in REPO.all()]
    if existing:
        print(f"[조립] 복원된 방: {', '.join(existing)}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[서버] {HOST}:{PORT} 대기 중... (Ctrl+C 종료)")
    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[서버] 종료합니다.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
