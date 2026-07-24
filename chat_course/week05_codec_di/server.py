"""
Week 5(통합) - server.py  :  부품을 '주입'해 조립한 서버
------------------------------------------------------------
이 주는 두 가지를 한 번에 합쳤습니다.
  (1) 변환(직렬화·암호화)을 Codec 부품으로 떼어내기          → codec.py
  (2) 그 부품들을 서버 두뇌에 '밖에서 끼워 넣기'(의존성 주입) → 이 파일

핵심 아이디어: 서버의 두뇌(ChatServer)는 부품을 '직접 만들지' 않는다.
            밖에서 '받아서(주입)' 쓴다.   →   ChatServer(codec, store)

비유: 게임기는 카트리지(부품)를 직접 만들지 않는다. 꽂아주는 대로 실행한다.
     (4주차 class_basics 의 Phone(ringtone) 과 똑같은 구조!)

이 파일의 ChatServer 는 소켓을 모른다(그래서 test_server.py 로 테스트된다).
소켓 연결은 아래 SocketTransport 와 main() 이 '바깥에서' 담당한다.

▶ 평문 탈취 데모는 sniffer.py 를 보세요. (README 의 '해킹 데모')
"""

import socket
import threading

from interfaces import MessageStore, Transport
from codec import PlainCodec, SecretCodec
from messages import SystemMessage

HOST = "127.0.0.1"
PORT = 5000

# ★ 부품 갈아끼우기 ★  True 로 바꾸면 오가는 메시지가 암호화된다.
#   (client.py 도 같은 값으로 맞춰야 서로 통합니다.)
USE_SECRET = False


# ============================================================
# 두뇌: 소켓을 모른다. 부품(codec, store)을 주입받아 쓴다.
# ============================================================
class ChatServer:
    def __init__(self, codec, store):
        self.codec = codec          # 주입된 부품 (변환)
        self.store = store          # 주입된 부품 (저장)
        self.clients = {}           # Transport -> nickname
        self._lock = threading.Lock()

    def join(self, transport, nickname):
        with self._lock:
            self.clients[transport] = nickname
            count = len(self.clients)
        self._broadcast(SystemMessage(f"*** {nickname}님이 들어왔습니다 (현재 {count}명) ***"))
        return count

    def leave(self, transport):
        with self._lock:
            nickname = self.clients.pop(transport, None)
            count = len(self.clients)
        if nickname:
            self._broadcast(SystemMessage(f"*** {nickname}님이 나갔습니다 (현재 {count}명) ***"))

    def on_line(self, transport, line):
        """받은 한 줄을 처리: 해석 → 저장 → 전원에게. (소켓 없이도 호출 가능)"""
        msg = self.codec.decode(line)            # 주입된 Codec 이 해석
        with self._lock:
            msg.sender = self.clients.get(transport, "?")
        try:
            self.store.save(msg)                 # 주입된 Store 에 저장 위임
        except Exception as e:                   # 저장이 실패해도 채팅은 계속
            print(f"[경고] 저장 실패: {e}")
        self._broadcast(msg)
        return msg

    def _broadcast(self, message):
        data = self.codec.encode(message)        # 주입된 Codec 이 인코딩
        with self._lock:
            targets = list(self.clients.keys())
        for t in targets:
            t.send(data)


# ============================================================
# 저장 부품들 (MessageStore 계약을 지킨다)
# ============================================================
class InMemoryStore(MessageStore):
    """메모리에만 저장. 서버를 끄면 사라진다."""
    def __init__(self):
        self._items = []

    def save(self, message):
        self._items.append(message)

    def all(self):
        return list(self._items)


class FileStore(MessageStore):
    """파일에 한 줄씩 남긴다. 서버를 껐다 켜도 기록이 남는다."""
    def __init__(self, path="chat_log.txt"):
        self.path = path

    def save(self, message):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(message.to_wire() + "\n")

    def all(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return [line.rstrip("\n") for line in f]
        except FileNotFoundError:
            return []


# ============================================================
# 전송 부품: 진짜 소켓을 Transport 계약에 맞춘다
# ============================================================
class SocketTransport(Transport):
    def __init__(self, conn):
        self.conn = conn

    def send(self, data):
        try:
            self.conn.sendall(data)
        except OSError:
            pass


# ============================================================
# 조립(Composition Root): 여기서 부품을 만들어 '주입'한다
# ============================================================
def build_server():
    codec = SecretCodec() if USE_SECRET else PlainCodec()
    store = InMemoryStore()         # ← FileStore("chat_log.txt") 로 바꿔 끼우면 파일 저장
    return ChatServer(codec, store)


def main():
    server = build_server()
    print(f"[조립] Codec={server.codec.name}, Store={type(server.store).__name__}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[서버] {HOST}:{PORT} 대기 중... (Ctrl+C 종료)")

    def handle(conn, addr):
        reader = conn.makefile("r", encoding="utf-8")
        transport = SocketTransport(conn)
        nickname = (reader.readline() or "").strip()
        if not nickname:
            conn.close()
            return
        count = server.join(transport, nickname)
        print(f"[서버] {nickname} 접속 (현재 {count}명)")
        try:
            while True:
                line = reader.readline()
                if not line:
                    break
                server.on_line(transport, line.rstrip("\n"))
        except OSError:
            pass
        finally:
            server.leave(transport)
            conn.close()
            print(f"[서버] {nickname} 퇴장")

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
