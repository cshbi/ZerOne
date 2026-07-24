"""
Week 5(통합) - client.py  :  클라이언트도 같은 부품(Codec)을 끼운다
------------------------------------------------------------
서버의 USE_SECRET 과 같은 값으로 맞추세요. 값이 다르면 서로 못 알아봅니다.
사용법: 그냥 입력=텍스트, /emoji smile=이모티콘, /file 경로=파일

접속 포트는 늘 5000 입니다. 도청 데모 때도 그대로 5000 으로 접속하면 되는데,
그 5000 번을 이번엔 서버가 아니라 sniffer(도청자)가 받습니다. (README 참고)
"""

import socket
import threading

from messages import TextMessage, EmojiMessage, FileMessage
from codec import PlainCodec, SecretCodec

HOST = "127.0.0.1"
PORT = 5000

# ★ 서버와 같은 값으로 맞추세요 ★
USE_SECRET = False
CODEC = SecretCodec() if USE_SECRET else PlainCodec()


def receive(sock):
    reader = sock.makefile("r", encoding="utf-8")
    while True:
        line = reader.readline()
        if not line:
            print("\n[연결 종료] 서버와의 연결이 끊겼습니다.")
            break
        print(CODEC.decode(line.rstrip("\n")).display())   # 주입된 부품이 해석


# ── 팩토리(factory): 재료를 넣으면 알맞은 '제품 객체'를 찍어내는 곳 ──
#   이 강의에는 팩토리가 세 종류 있습니다. 셋 다 "생성 결정을 한곳에 몰아,
#   부르는 쪽은 '무엇을 만들지' 신경 안 쓰게" 한다는 정신은 같습니다.
#
#   ① make_message      (아래, 보내는 쪽) : 사람 입력 → 알맞은 Message 객체
#                        └ 사람이 친 명령(/emoji, /file)을 해석해야 해서 if 가 남는다
#   ② Message.from_wire (messages.py, 받는 쪽) : 네트워크 줄 → 알맞은 Message 객체
#                        └ 기계 꼬리표(TEXT|·EMOJI|)라서 '등록표(@register)'로 if 를 없앰
#   ③ FileMessage.from_path / .parse : '다른 재료로부터' 객체를 만드는 팩토리 메서드
#                        └ 4주차 step05 의 @classmethod('객체를 만드는 또 다른 문')
#
#   ①과 ②의 비대칭이 포인트: 보내는 쪽은 '사람 입력 해석', 받는 쪽은 '기계 프로토콜'.
def make_message(text, nickname):
    """사용자가 친 한 줄(text) -> 알맞은 메시지 객체. (보내는 쪽 팩토리)"""
    if text.startswith("/emoji "):                              # "/emoji smile" 형태면
        return EmojiMessage(text[len("/emoji "):].strip(), sender=nickname)   # 이모티콘 제품
    if text.startswith("/file "):                               # "/file 경로" 형태면
        return FileMessage.from_path(text[len("/file "):].strip(), sender=nickname)  # ③ 팩토리 메서드로
    return TextMessage(text, sender=nickname)                   # 그 외에는 평범한 텍스트 제품


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    nickname = input("닉네임을 입력하세요: ").strip()
    sock.sendall((nickname + "\n").encode("utf-8"))     # 닉네임은 평문 핸드셰이크

    threading.Thread(target=receive, args=(sock,), daemon=True).start()
    print(f"대화 시작!  (Codec = {CODEC.name},  종료: Ctrl+C)\n")

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
            sock.sendall(CODEC.encode(msg))             # 주입된 부품이 인코딩
    except (EOFError, KeyboardInterrupt):
        print("\n[클라이언트] 대화를 종료합니다.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
