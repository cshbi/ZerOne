"""
Week 8 - client.py  :  명령이 늘어난 클라이언트
------------------------------------------------------------
명령:
  /create 방   /join 방   /leave   /rooms   /who
  /rename 이름            이름 바꾸기
  /w 닉네임 메시지        귓속말
그 외 입력 → 현재 방에 메시지 전송
------------------------------------------------------------
"""

import socket
import threading
import os

from messages import TextMessage, EmojiMessage, FileMessage
from codec import AesGcmCodec

HOST = "127.0.0.1"
PORT = 5000
CODEC = AesGcmCodec()   # 서버와 같은 codec/암호(passphrase)여야 서로 알아봄


def receive(sock):
    reader = sock.makefile("r", encoding="utf-8")
    while True:
        line = reader.readline()
        if not line:
            print("\n[연결 종료] 서버와의 연결이 끊겼습니다.")
            break
        print(CODEC.decode(line.rstrip("\n")).display())


def make_message(text, nickname):
    if text.startswith("/emoji "):
        return EmojiMessage(text[len("/emoji "):].strip(), sender=nickname)
    if text.startswith("/file "):
        return FileMessage.from_path(text[len("/file "):].strip(), sender=nickname)
    return TextMessage(text, sender=nickname)   # 명령도 텍스트로 전송


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    nickname = input("닉네임을 입력하세요: ").strip()
    sock.sendall((nickname + "\n").encode("utf-8"))

    threading.Thread(target=receive, args=(sock,), daemon=True).start()
    print("명령: /create /join /leave /rooms /who /rename /w  (종료: Ctrl+C)\n")

    try:
        while True:
            text = input()
            if not text:
                continue
            if text == "/clear":
                os.system("cls" if os.name =="nt" else "clear")
                continue
            try:
                msg = make_message(text, nickname)
            except OSError:
                print("[오류] 파일을 열 수 없습니다.")
                continue
            sock.sendall(CODEC.encode(msg))
    except (EOFError, KeyboardInterrupt):
        print("\n[클라이언트] 대화를 종료합니다.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
