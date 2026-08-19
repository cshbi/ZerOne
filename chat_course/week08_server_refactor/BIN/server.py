"""
Week 8 - server.py  :  작은 객체들이 협력하는 서버
------------------------------------------------------------
기능이 늘면서 서버가 다시 커졌습니다. 책임을 객체로 나눕니다.

  - ConnectionManager : 접속(Session) 관리        (session.py)
  - CommandHandler    : 명령(/create 등) 해석      (command.py)
  - RoomRepository    : 방 저장/조회               (repository.py)
  - Room              : 방의 멤버·기록·전송         (room.py)
  - ChatServer        : 위를 '조립'하고 흐름만 지휘 (이 파일)

ChatServer 는 직접 일하지 않습니다. 부품들에게 시키고 흐름만 잇습니다.
새 명령 추가? command.py 의 표에 한 줄. 서버 본체는 그대로.
------------------------------------------------------------
명령: /create 방, /join 방, /leave, /rooms, /who, /rename 이름, /w 닉 메시지
"""

import socket
import threading

from codec import AesGcmCodec
from messages import TextMessage, SystemMessage
from repository import InMemoryRoomRepository, FileRoomRepository
from session import ConnectionManager
from command import CommandHandler

HOST = "127.0.0.1"
PORT = 5000

HELP = "명령: /create 방, /join 방, /leave, /rooms, /who, /rename 이름, /w 닉 메시지"


class ChatServer:
    """부품을 조립하고 흐름만 지휘한다 (직접 일하지 않는다)."""

    def __init__(self, codec, rooms, connections):
        self.codec = codec                       # 주입
        self.rooms = rooms                       # 주입 (RoomRepository)
        self.connections = connections           # 주입 (ConnectionManager)
        self.commands = CommandHandler(self)     # 명령 해석기

    # ── 전송 도우미 ──
    def raw_send(self, conn, message):
        try:
            conn.sendall(self.codec.encode(message))
        except OSError:
            pass

    def send_to(self, session, message):
        self.raw_send(session.conn, message)

    # ── 공통 동작 ──
    def leave_room(self, session):
        room = session.room
        if not room:
            return
        room.leave(session.conn)
        self.rooms.save(room)
        room.deliver(SystemMessage(f"*** {session.nickname}님이 방을 나갔습니다 ***"), self.raw_send)
        session.room = None

    # ── 연결 수명주기 ──
    def on_connect(self, conn, nickname):
        session = self.connections.add(conn, nickname)
        self.send_to(session, SystemMessage(HELP))
        print(f"[서버] {nickname} 접속 (현재 {len(self.connections.all())}명)")
        return session

    def on_line(self, session, line):
        try:
            msg = self.codec.decode(line)      # 암호 해독 (다른 키·손상된 줄이면 예외)
        except Exception:
            # 해독 실패한 줄은 무시하고 연결은 살려 둔다 (한 줄 때문에 죽지 않게)
            print(f"[경고] 해독 실패한 메시지 무시 ({session.nickname})")
            return
        # 명령이면 명령 해석기에 위임
        if isinstance(msg, TextMessage) and msg.text.startswith("/"):
            self.commands.handle(session, msg.text)
            return
        # 일반 메시지는 현재 방에 전달
        if not session.room:
            self.send_to(session, SystemMessage("먼저 /join 으로 방에 들어가세요."))
            return
        msg.sender = session.nickname
        session.room.post(msg, self.raw_send)
        self.rooms.save(session.room)

    def on_disconnect(self, session):
        self.leave_room(session)
        self.connections.remove(session.conn)
        print(f"[서버] {session.nickname} 퇴장")


# ============================================================
# 조립(Composition Root): 부품을 만들어 ChatServer 에 주입
# ============================================================
def build_server():
    codec = AesGcmCodec()                # AES-256-GCM (6주차부터 평문 제거)
    rooms = InMemoryRoomRepository()     # FileRoomRepository("rooms.json") 로 교체 가능
    connections = ConnectionManager()
    return ChatServer(codec, rooms, connections)


def main():
    server = build_server()
    print(f"[조립] Codec={server.codec.name}, 저장소={type(server.rooms).__name__}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[서버] {HOST}:{PORT} 대기 중... (Ctrl+C 종료)")

    def handle(conn, addr):
        reader = conn.makefile("r", encoding="utf-8")
        nickname = (reader.readline() or "").strip()
        if not nickname:
            conn.close()
            return
        session = server.on_connect(conn, nickname)
        try:
            while True:
                line = reader.readline()
                if not line:
                    break
                server.on_line(session, line.rstrip("\n"))
        except OSError:
            pass
        finally:
            server.on_disconnect(session)
            conn.close()

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
