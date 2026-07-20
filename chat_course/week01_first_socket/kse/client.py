"""
Week 1 - 클라이언트 (client.py)
------------------------------------------------------------
"말을 거는 쪽"이 클라이언트입니다.
서버가 먼저 켜져 있어야(기다리고 있어야) 연결할 수 있습니다.

이 파일도 클래스 없이 함수와 절차(순서)만으로 짠
'가장 단순한 클라이언트'입니다.
------------------------------------------------------------
실행 방법:  python client.py   (서버를 먼저 켠 뒤 실행)
"""

import socket

HOST = "127.0.0.1"   # 접속할 서버의 IP. 같은 PC면 localhost(127.0.0.1)
PORT = 5000          # 서버가 열어 둔 내선번호와 똑같아야 한다

# 1) 소켓을 만든다 (= 수화기를 든다)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2) 서버에게 전화를 건다 (연결 시도)
client_socket.connect((HOST, PORT))
print(f"[클라이언트] {HOST}:{PORT} 서버에 연결했습니다!\n")

# 3) 반복문으로 계속 주고받는다 (내가 먼저 말하고, 서버 답을 듣는다)
#    Ctrl+C(중단)나 Ctrl+D(입력 끝)로 빠져나오면 깔끔히 종료되도록 감싼다.
try:
    while True:
        # 보낼 말을 입력받아, 글자를 바이트로 바꿔(encode) 서버로 보낸다
        message = input("[나(클라이언트)] ")
        client_socket.sendall(message.encode("utf-8"))

        # 서버의 답을 바이트로 받아서(recv), 글자로 되돌린다(decode)
        data = client_socket.recv(1024)
        if not data:
            print("[클라이언트] 서버가 연결을 끊었습니다.")
            break

        reply = data.decode("utf-8")
        print(f"[서버] {reply}")
except (EOFError, KeyboardInterrupt):
    print("\n[클라이언트] 대화를 종료합니다.")

# 4) 통화 종료
client_socket.close()
