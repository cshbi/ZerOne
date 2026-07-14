"""
Week 3 - 클라이언트 (client.py)  :  텍스트도, 파일도
------------------------------------------------------------
보내기와 받기 '양쪽 모두'에 종류별 if/elif 분기가 생깁니다.

사용법:
  - 그냥 입력          → 텍스트 메시지로 전송
  - /file <파일경로>   → 그 파일을 전송 (base64 로 실어서)
  받은 파일은 downloads/ 폴더에 저장됩니다.
------------------------------------------------------------
실행:  python client.py   (서버를 먼저 켠 뒤 실행)
"""

import socket
import threading
import base64
import os

HOST = "127.0.0.1"
PORT = 5000
DOWNLOAD_DIR = "downloads"


def receive(sock):
    """서버에서 오는 줄을 받아 종류별로 처리 (받기 전용 스레드)."""
    reader = sock.makefile("r", encoding="utf-8")
    while True:
        line = reader.readline()
        if not line:
            print("\n[연결 종료] 서버와의 연결이 끊겼습니다.")
            break
        line = line.rstrip("\n")

        # ========== 분기 지옥 (클라이언트 받기) ==========
        if line.startswith("TEXT|"):
            _, sender, text = line.split("|", 2)
            if sender == "시스템":
                print(text)                  # 입퇴장 알림 등
            else:
                print(f"{sender}: {text}")

        elif line.startswith("FILE|"):
            _, sender, filename, b64 = line.split("|", 3)
            data = base64.b64decode(b64)     # base64 문자열 → 원래 바이트
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            save_as = os.path.join(DOWNLOAD_DIR, f"{sender}_{filename}")
            with open(save_as, "wb") as f:
                f.write(data)
            print(f"📎 [{sender}]님이 파일을 보냈습니다 → 저장: {save_as} ({len(data)} bytes)")

        else:
            print(f"[알 수 없는 메시지] {line[:30]}")
        # ================================================


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    nickname = input("닉네임을 입력하세요: ").strip()
    sock.sendall((nickname + "\n").encode("utf-8"))

    threading.Thread(target=receive, args=(sock,), daemon=True).start()
    print("대화를 시작하세요!  (파일 전송: /file 경로,  종료: Ctrl+C)\n")

    try:
        while True:
            text = input()
            if not text:
                continue

            # ========== 분기 지옥 (클라이언트 보내기) ==========
            if text.startswith("/file "):
                path = text[len("/file "):].strip()
                try:
                    with open(path, "rb") as f:
                        raw = f.read()
                except OSError:
                    print(f"[오류] 파일을 열 수 없습니다: {path}")
                    continue
                b64 = base64.b64encode(raw).decode("ascii")   # 바이트 → base64 문자열
                filename = os.path.basename(path)
                sock.sendall(f"FILE|{filename}|{b64}\n".encode("utf-8"))
                print(f"(파일 보냄: {filename}, {len(raw)} bytes)")
            else:
                sock.sendall(f"TEXT|{text}\n".encode("utf-8"))
            # ==================================================

    except (EOFError, KeyboardInterrupt):
        print("\n[클라이언트] 대화를 종료합니다.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
