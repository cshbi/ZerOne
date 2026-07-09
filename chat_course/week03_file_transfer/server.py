"""
Week 3 - 서버 (server.py)  :  파일도 보내고 싶다 → 분기 지옥의 시작
------------------------------------------------------------
지난주 메시지는 그냥 '한 줄 문자열'이었습니다.
그런데 파일은 이름·크기·바이너리 내용이 필요합니다.
그래서 메시지에 '종류(type)'가 생깁니다: 일반 글(TEXT) / 파일(FILE).

해결책으로 (일부러) 절차적으로 욱여넣습니다:
  - 메시지 앞에 꼬리표를 붙인다:  "TEXT|안녕",  "FILE|cat.png|<base64>"
  - 받는 쪽은 꼬리표를 보고 if / elif 로 갈라서 처리한다.

⚠️ 이렇게 하면 '종류'가 하나 늘 때마다 보내기·받기·서버 곳곳의
   if/elif 를 전부 찾아 고쳐야 합니다. 이 고통이 다음 주(객체)의 동기입니다.
------------------------------------------------------------
프로토콜(이번 주 약속):
  클라이언트 → 서버 :  TEXT|<메시지>            또는  FILE|<파일이름>|<base64>
  서버 → 클라이언트 :  TEXT|<닉네임>|<메시지>   또는  FILE|<닉네임>|<파일이름>|<base64>
  (한 메시지 = 한 줄, 끝에 '\\n'. 닉네임은 서버가 알고 있으니 서버가 붙인다.)
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 5000
MAX_FILE_BYTES = 5 * 1024 * 1024   # 교육용 파일 크기 제한 (5MB)

clients = {}                       # conn -> nickname
clients_lock = threading.Lock()


def broadcast(line):
    """한 줄(개행 포함)을 접속자 전원에게 보낸다."""
    data = (line + "\n").encode("utf-8")
    with clients_lock:
        targets = list(clients.keys())
    for sock in targets:
        try:
            sock.sendall(data)
        except OSError:
            pass


def handle(conn, addr):
    # 줄 단위로 읽는 장치.
    # ⚠️ recv(1024) 하나로는 base64 가 긴 파일이 '중간에 잘린다'.
    #    그래서 줄(\n) 단위로 모아 읽도록 makefile 을 끼웠다 — 이것도 새로 늘어난 부담.
    reader = conn.makefile("r", encoding="utf-8")

    nickname = (reader.readline() or "").strip()   # 첫 줄 = 닉네임
    if not nickname:
        conn.close()
        return

    with clients_lock:
        clients[conn] = nickname
        count = len(clients)
    print(f"[서버] {nickname} 접속 (현재 {count}명)")
    broadcast(f"TEXT|시스템|*** {nickname}님이 들어왔습니다 (현재 {count}명) ***")

    while True:
        line = reader.readline()
        if not line:                  # 빈 줄 = 연결 종료
            break
        line = line.rstrip("\n")

        # ========== 분기 지옥 (서버) : 종류에 따라 처리가 갈린다 ==========
        if line.startswith("TEXT|"):
            _, text = line.split("|", 1)
            print(f"[서버] (텍스트) {nickname}: {text}")
            broadcast(f"TEXT|{nickname}|{text}")

        elif line.startswith("FILE|"):
            _, filename, b64 = line.split("|", 2)
            approx = len(b64) * 3 // 4          # base64 길이로 원본 크기 추정
            if approx > MAX_FILE_BYTES:
                print(f"[서버] (파일 거부) {filename} 이 너무 큽니다")
                conn.sendall("TEXT|시스템|파일이 너무 큽니다(5MB 제한)\n".encode("utf-8"))
            else:
                print(f"[서버] (파일) {nickname} → {filename} (약 {approx} bytes)")
                broadcast(f"FILE|{nickname}|{filename}|{b64}")

        else:
            print(f"[서버] (알 수 없는 종류) {line[:30]}")
        # ================================================================

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
