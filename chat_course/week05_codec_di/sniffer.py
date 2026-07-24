"""
Week 5(통합) - sniffer.py  :  평문 탈취 데모 (중간자 / 도청자)
============================================================
"내 메시지가 중간에 그대로 보이는 거 아냐?" — 직접 보여 줍니다.

인터넷에서 내 메시지는 여러 중계 지점(공유기·카페 와이파이·통신사)을
거쳐 서버에 갑니다. 그 중 한 곳에 도청자가 있다면 어떻게 될까요?

이 프로그램이 바로 그 '중간 지점'입니다.
  클라이언트 → [sniffer(나, 도청자)] → 진짜 서버
  - 오가는 바이트를 '그대로 흘려보내(중계)' 채팅은 멀쩡히 되게 하고,
  - 지나가는 내용을 몰래 '엿본다(탈취)'.

핵심 대비:
  · 평문(PlainCodec)   → 내용이 그대로 읽힌다.      "탈취 성공" 😱
  · 암호화(SecretCodec) → 알아볼 수 없는 글자만 보인다. "탈취 실패" 🔒

⚠️ 이 프로그램은 '수업용 도청 시연'입니다. 남의 통신을 실제로 엿보는 것은
   불법입니다. 반드시 내 PC 안(localhost)에서, 내가 띄운 서버로만 실습하세요.

────────────────────────────────────────────────────────────
실행 순서 (터미널 4개):
  1) python server.py 5001        # 진짜 서버는 5001 에
  2) python sniffer.py            # 도청자는 5000 에서 받아 5001 로 중계
  3) python client.py             # 평소처럼 5000 으로 접속 (사실은 도청자에게!)
  4) client 에서 "비밀번호는 1234야" 같은 말을 쳐 보고 sniffer 창을 보라
────────────────────────────────────────────────────────────
"""

import socket
import threading

# 클라이언트가 접속하는 곳(도청 지점) → 진짜 서버로 중계
LISTEN_HOST, LISTEN_PORT = "127.0.0.1", 5000
SERVER_HOST, SERVER_PORT = "127.0.0.1", 5001

# (심화) True 로 켜면, 코드에 '박혀 있는' 열쇠로 XOR 암호를 풀어 본다.
#   → "열쇠가 코드에 있으면 암호도 뚫린다 = 이건 진짜 보안이 아니다" 를 보여 줌.
SHOW_CRACK = False
XOR_KEY = 42            # codec.py 의 SECRET_KEY 와 같은 값(도청자가 알아냈다고 가정)


_BASE64_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")


def looks_readable(text):
    """사람이 읽을 수 있는 평문 같은가?

    암호화된 줄은 base64(영문·숫자·+/=)로만 이뤄진다. 반대로 평문(닉네임 '철수',
    프로토콜 'TEXT|철수|안녕')에는 한글·'|'·공백 등 base64 밖 글자가 섞인다.
    → base64 밖 글자가 하나라도 있으면 '읽을 수 있는 평문'으로 본다.
    (수업용 어림짐작입니다. 영어 단어 하나만 평문으로 보내는 극단적 경우는 예외.)
    """
    return any(ch not in _BASE64_CHARS for ch in text)


def try_crack(text):
    """base64 + XOR 을 되돌려 본다. 성공하면 복호화된 평문을 돌려준다."""
    import base64
    try:
        raw = base64.b64decode(text)
        plain = bytes(b ^ XOR_KEY for b in raw).decode("utf-8")
        return plain if "|" in plain else None
    except Exception:
        return None


def steal(direction, text):
    """지나가는 한 줄을 엿본다(탈취)."""
    if not text:
        return
    arrow = "클라 → 서버" if direction == "up" else "서버 → 클라"
    if looks_readable(text):
        print(f"  😱 [탈취 성공] {arrow}  |  {text}")
    else:
        print(f"  🔒 [탈취 실패] {arrow}  |  {text}   ← 알아볼 수 없음")
        if SHOW_CRACK:
            cracked = try_crack(text)
            if cracked:
                print(f"      └ (박힌 열쇠 {XOR_KEY} 로 복호화) {cracked}   ← 그래서 진짜 보안이 아니다!")


def pump(src, dst, direction):
    """src 에서 온 줄을 dst 로 그대로 흘려보내며(중계), 동시에 엿본다(탈취)."""
    reader = src.makefile("rb")
    try:
        for raw in reader:                       # raw: 끝에 \n 붙은 bytes 한 줄
            dst.sendall(raw)                     # ① 그대로 중계 → 채팅은 멀쩡
            text = raw.decode("utf-8", "replace").rstrip("\n")
            steal(direction, text)               # ② 몰래 엿보기 → 탈취
    except OSError:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)         # 한쪽이 끊기면 상대에게도 알림
        except OSError:
            pass


def handle(client_conn):
    """클라이언트 한 명 ↔ 진짜 서버를 이어 준다(사이에 도청자가 낀다)."""
    server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_conn.connect((SERVER_HOST, SERVER_PORT))
    # 두 방향을 각각 중계·도청
    threading.Thread(target=pump, args=(client_conn, server_conn, "up"), daemon=True).start()
    pump(server_conn, client_conn, "down")       # 이 스레드가 끝나면 연결 종료
    client_conn.close()
    server_conn.close()


def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((LISTEN_HOST, LISTEN_PORT))
    listener.listen()
    print(f"[도청자] {LISTEN_HOST}:{LISTEN_PORT} 에서 대기 → 진짜 서버 {SERVER_HOST}:{SERVER_PORT} 로 중계")
    print("[도청자] 지나가는 모든 줄을 엿봅니다. (Ctrl+C 종료)\n")
    try:
        while True:
            client_conn, addr = listener.accept()
            print(f"[도청자] 새 연결 낚음: {addr}")
            threading.Thread(target=handle, args=(client_conn,), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[도청자] 종료합니다.")
    finally:
        listener.close()


if __name__ == "__main__":
    main()
