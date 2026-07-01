"""
Week 1 - 서버 (server.py)
------------------------------------------------------------
"항상 받을 준비를 하고 기다리는 쪽"이 서버입니다.

전화 비유로 보면:
  - IP   = 전화번호 (어느 컴퓨터인가)
  - PORT = 내선번호 (그 컴퓨터의 어느 프로그램인가)
  - 소켓 = 통화 중인 수화기

이 파일에는 클래스가 없습니다. 함수와 절차(순서)만으로 짠
'가장 단순한 서버'입니다. 1주차에는 일부러 이렇게 시작합니다.
------------------------------------------------------------
실행 방법:  python server.py   (먼저 켜 두세요)
"""

import socket

HOST = "127.168.0.27"   # 내 컴퓨터 자신(localhost). 같은 PC 안에서 연습할 때 사용
PORT = 5000          # 약속한 내선번호. 클라이언트도 같은 번호로 접속해야 한다

# 1) 소켓을 만든다 (= 수화기를 든다)
#    AF_INET  : IPv4 주소를 쓰겠다
#    SOCK_STREAM : TCP(끊기지 않고 순서대로 도착하는 통신)를 쓰겠다
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# (편의) 프로그램을 껐다 켰을 때 "주소가 이미 사용 중" 오류를 피한다
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 2) 이 전화번호+내선번호를 내 것으로 등록한다
server_socket.bind((HOST, PORT))

# 3) 이제 전화를 받겠다고 선언한다 (대기 시작)
server_socket.listen(1)
print(f"[서버] {HOST}:{PORT} 에서 손님을 기다립니다...  (Ctrl+C 로 종료)")

# 4) 손님이 올 때까지 여기서 멈춰 기다린다. 한 명이 오면 통화 연결!
#    conn : 그 손님과 이야기할 '전용 수화기'
#    addr : 손님의 주소 (IP, 포트)
conn, addr = server_socket.accept()
print(f"[서버] {addr} 손님이 연결되었습니다! 대화를 시작하세요.\n")

# 5) 반복문으로 계속 주고받는다 (한 명 <-> 서버, 번갈아 대화)
#    Ctrl+C(중단)나 Ctrl+D(입력 끝)로 빠져나오면 깔끔히 종료되도록 감싼다.
try:
    while True:
        # recv : 상대가 보낸 바이트(bytes)를 받는다. 1024는 한 번에 받을 최대 크기
        data = conn.recv(1024)

        # 받은 데이터가 비어 있으면(b"") 상대가 연결을 끊었다는 뜻
        if not data:
            print("[서버] 상대가 연결을 끊었습니다.")
            break

        # 네트워크로는 '글자'가 아니라 '바이트'가 오간다.
        # 그래서 받은 바이트를 글자로 되돌리려면 decode 가 필요하다.
        message = data.decode("utf-8")
        print(f"[손님] {message}")

        # 내 답장을 입력받아서, 글자를 바이트로 바꿔(encode) 보낸다.
        reply = message.upper()
        conn.sendall(reply.encode("utf-8"))
except (EOFError, KeyboardInterrupt):
    print("\n[서버] 대화를 종료합니다.")

# 6) 통화 종료: 수화기를 내려놓는다
conn.close()
server_socket.close()


# ------------------------------------------------------------
# [실습/과제 힌트] 에코 변형
# 위 5)의 입력 부분을 지우고, 받은 문장을 대문자로 바꿔 그대로 돌려보내 보세요.
#     reply = message.upper()
#     conn.sendall(reply.encode("utf-8"))
# ------------------------------------------------------------
