"""
Week 4 - 서버 (server.py)  :  분기가 사라진 서버
------------------------------------------------------------
3주차 서버는 종류마다 if/elif 로 갈라졌습니다.
이제 서버는 종류를 묻지 않습니다.

  msg = Message.from_wire(line)   # 알맞은 객체로 (해석은 한 곳)
  broadcast(msg.to_wire())        # 어떤 종류든 똑같이 처리

종류가 늘어도 이 서버 코드는 한 줄도 바뀌지 않습니다.
------------------------------------------------------------
"""

import socket
import threading

from messages import Message, SystemMessage

HOST = "127.0.0.1"
PORT = 5000

clients = {}                       # conn -> nickname
clients_lock = threading.Lock()


def broadcast(line):
    data = (line + "\n").encode("utf-8")
    with clients_lock:
        targets = list(clients.keys())
    for sock in targets:
        try:
            sock.sendall(data)
        except OSError:
            pass


def handle(conn, addr):
    reader = conn.makefile("r", encoding="utf-8")
    nickname = (reader.readline() or "").strip()
    if not nickname:
        conn.close()
        return

    with clients_lock:
        clients[conn] = nickname
        count = len(clients)
    print(f"[서버] {nickname} 접속 (현재 {count}명)")
    broadcast(SystemMessage(f"*** {nickname}님이 들어왔습니다 (현재 {count}명) ***").to_wire())

    try:
        while True:
            line = reader.readline()
            if not line:
                break
            line = line.rstrip("\n")

            # ★ 분기 없음 ★  어떤 종류가 와도 아래 세 줄로 끝.
            msg = Message.from_wire(line)
            msg.sender = nickname          # 서버가 아는 닉네임으로 보정(신뢰)
            print(f"[서버] ({msg.kind}) {nickname}")
            broadcast(msg.to_wire())
    except OSError:
        pass                               # 상대가 갑자기 끊어도 조용히 정리

    with clients_lock:
        clients.pop(conn, None)
        count = len(clients)
    conn.close()
    print(f"[서버] {nickname} 퇴장 (현재 {count}명)")
    broadcast(SystemMessage(f"*** {nickname}님이 나갔습니다 (현재 {count}명) ***").to_wire())


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[서버] {HOST}:{PORT} 에서 손님을 기다립니다... (Ctrl+C 로 종료)")
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
