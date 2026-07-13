"""
Week 2 - 클라이언트 (client.py)  :  보내기와 받기를 동시에
------------------------------------------------------------
단체 채팅에서는 '내가 입력하는 동안에도' 남이 보낸 말이 도착합니다.
그래서 한 가지 일만 하면 안 됩니다. 두 가지를 동시에 해야 합니다.

  - 보내기 : input() 으로 내가 친 말을 서버로 보낸다  (메인 흐름)
  - 받기   : 서버에서 오는 말을 계속 화면에 띄운다     (받기 전용 스레드)

이 두 가지를 threading 으로 동시에 돌립니다.
------------------------------------------------------------
실행:  python client.py   (서버를 먼저 켠 뒤 실행)
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 5000


def receive(sock):
    """서버에서 오는 메시지를 계속 받아 화면에 출력 (받기 전용 스레드)."""
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break
        if not data:
            print("\n[연결 종료] 서버와의 연결이 끊겼습니다.")
            break
        print(data.decode("utf-8"))


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # 접속하면 가장 먼저 닉네임을 보낸다 (서버가 첫 줄을 닉네임으로 읽는다)
    nickname = input("닉네임을 입력하세요: ").strip()
    sock.sendall(nickname.encode("utf-8"))

    # 받기 전용 스레드를 띄운다 → 입력을 기다리는 중에도 메시지가 도착한다
    threading.Thread(target=receive, args=(sock,), daemon=True).start()
    #받는 역할의 스레드 생성

    print("대화를 시작하세요!  (종료: Ctrl+C)\n")

    # 메인 흐름은 '보내기'를 담당
    try:
        while True:
            message = input()
            if message:
                sock.sendall(message.encode("utf-8"))
    except (EOFError, KeyboardInterrupt):
        print("\n[클라이언트] 대화를 종료합니다.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
