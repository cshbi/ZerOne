"""
Week 4 - 클라이언트 (client.py)  :  분기가 사라진 받기
------------------------------------------------------------
받는 쪽도 종류를 묻지 않습니다.

  msg = Message.from_wire(line)
  print(msg.display())            # 텍스트든 이모티콘이든 파일이든 똑같이

보낼 때는 '무엇을 만들지' 한 번만 고릅니다(객체 생성).
그 뒤로는 모두 같은 방식으로 흘러갑니다.

사용법:
  그냥 입력          → 텍스트
  /emoji smile       → 이모티콘 (smile/heart/thumbsup/cry/wow)
  /file <파일경로>   → 파일
------------------------------------------------------------
"""

import socket
import threading

from messages import Message, TextMessage, EmojiMessage, FileMessage

HOST = "127.0.0.1"
PORT = 5000


def receive(sock):
    reader = sock.makefile("r", encoding="utf-8")
    while True:
        line = reader.readline()
        if not line:
            print("\n[연결 종료] 서버와의 연결이 끊겼습니다.")
            break
        line = line.rstrip("\n")

        # ★ 분기 없음 ★  종류가 무엇이든 display() 한 줄.
        msg = Message.from_wire(line)
        print(msg.display())


def make_message(text, nickname):
    """사용자 입력 -> 메시지 객체. '무엇을 만들지'만 여기서 고른다."""
    if text.startswith("/emoji "):
        name = text[len("/emoji "):].strip()
        return EmojiMessage(name, sender=nickname)
    if text.startswith("/file "):
        path = text[len("/file "):].strip()
        return FileMessage.from_path(path, sender=nickname)
    return TextMessage(text, sender=nickname)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    nickname = input("닉네임을 입력하세요: ").strip()
    sock.sendall((nickname + "\n").encode("utf-8"))

    threading.Thread(target=receive, args=(sock,), daemon=True).start()
    print("대화 시작!  (이모티콘: /emoji smile,  파일: /file 경로,  종료: Ctrl+C)\n")

    try:
        while True:
            text = input()
            if not text:
                continue
            try:
                msg = make_message(text, nickname)
            except OSError:
                print("[오류] 파일을 열 수 없습니다.")
                continue
            sock.sendall((msg.to_wire() + "\n").encode("utf-8"))   # 종류 상관없이 동일
    except (EOFError, KeyboardInterrupt):
        print("\n[클라이언트] 대화를 종료합니다.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
