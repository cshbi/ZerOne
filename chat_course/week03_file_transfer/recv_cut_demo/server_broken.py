"""
[곁다리·고장난 버전] server_broken.py  :  recv() 하나로 받으면 무슨 일이?
------------------------------------------------------------------------
윗 폴더의 진짜 server.py 와 딱 두 가지만 다릅니다.
  (1) makefile / readline 을 안 쓰고, recv(1024) 로 '받은 만큼' 그냥 처리한다.
  (2) 파일 크기 제한(MAX_FILE_BYTES)이 없다 — '무조건 허용'.

그래서 이 버전은:
  - 작은 파일(small.png) → 어쩌다 한 recv 에 다 들어와서 '되는 것처럼' 보인다.
  - 큰 파일(big.png)   → 한 줄이 recv 경계에서 '잘려' 깨진 파일이 저장된다.
  - 게다가 크기 제한이 없어, 누가 거대한 파일을 보내도 서버가 그대로 중계한다.

실행:  python server_broken.py   (그다음 client_broken.py 를 2개 띄운다)
------------------------------------------------------------------------
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 5001                        # 진짜 server.py(5000)와 겹치지 않게 다른 포트

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
    # ❌ 여기가 고장의 핵심.
    #    진짜 server.py 는 conn.makefile("r") 로 '\n 까지' 모아 한 줄을 완성한다.
    #    이 버전은 그냥 recv(1024) 로 '그 순간 도착한 만큼'만 받는다.
    first = conn.recv(1024)                    # 첫 recv = 닉네임 (짧으니 대개 한 번에 옴)
    nickname = first.decode("utf-8", errors="replace").strip()
    if not nickname:
        conn.close()
        return

    with clients_lock:
        clients[conn] = nickname
        count = len(clients)
    print(f"[서버] {nickname} 접속 (현재 {count}명)")
    broadcast(f"TEXT|시스템|*** {nickname}님이 들어왔습니다 (현재 {count}명) ***")

    while True:
        chunk = conn.recv(1024)                # ← 한 줄이 아니라 '1024 바이트까지'만 받는다
        if not chunk:                          # 연결 종료
            break
        line = chunk.decode("utf-8", errors="replace").rstrip("\n")

        # (진짜 server.py 와 같은 분기 — 크기 검사만 빠졌다)
        if line.startswith("TEXT|"):
            _, text = line.split("|", 1)
            print(f"[서버] (텍스트) {nickname}: {text}")
            broadcast(f"TEXT|{nickname}|{text}")

        elif line.startswith("FILE|"):
            # ❗ 크기 제한 없음 = 무조건 허용. 잘린 조각이든, 수십 MB든 그대로 중계.
            parts = line.split("|", 2)
            if len(parts) < 3:                 # recv 경계에서 헤더조차 잘렸을 수도
                print(f"[서버] (깨진 조각?) {line[:40]}...")
                continue
            _, filename, b64 = parts
            print(f"[서버] (파일) {nickname} → {filename} (받은 base64 {len(b64)}글자)")
            broadcast(f"FILE|{nickname}|{filename}|{b64}")

        else:
            # recv 경계에서 잘려나온 '뒷토막'은 TEXT|/FILE| 로 시작하지 않아 여기로 온다.
            print(f"[서버] (알 수 없는 종류 = 잘린 뒷토막?) {line[:40]}...")

    with clients_lock:
        clients.pop(conn, None)
        count = len(clients)
    conn.close()
    print(f"[서버] {nickname} 퇴장 (현재 {count}명)")
    broadcast(f"TEXT|시스템|*** {nickname}님이 나갔습니다 (현재 {count}명) ***")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[고장난 서버] {HOST}:{PORT} 대기 중... (recv 방식·크기 무제한, Ctrl+C 종료)")
    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[고장난 서버] 종료합니다.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
