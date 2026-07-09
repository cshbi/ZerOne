"""
[곁다리·고장난 버전] client_broken.py  :  받을 때도 recv() 하나로
------------------------------------------------------------------------
윗 폴더의 진짜 client.py 와 딱 한 가지가 다릅니다.
  - 받기(receive)에서 makefile / readline 을 안 쓰고 recv(1024) 로 받는다.

그래서 큰 파일을 받으면 base64 가 recv 경계에서 '잘린 채' 도착하고,
그 잘린 데이터를 저장하면 downloads_broken/ 안에 '열리지 않는 깨진 이미지'가 생긴다.
작은 파일은 어쩌다 한 번에 다 와서 멀쩡히 저장된다 — 이 차이가 이번 실습의 핵심.

사용법:
  - 그냥 입력          → 텍스트 메시지
  - /file small.png    → 작은 파일 (대개 멀쩡히 도착)
  - /file big.png      → 큰 파일   (거의 확실히 깨져서 도착)

실행:  python client_broken.py   (server_broken.py 를 먼저 켠 뒤 실행)
------------------------------------------------------------------------
"""

import sys
import socket
import threading
import base64
import os

# 윈도우 기본 콘솔(cp949)에서도 이모지·한글이 안 깨지도록.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HOST = "127.0.0.1"
PORT = 5001                        # server_broken.py 와 같은 포트
DOWNLOAD_DIR = "downloads_broken"


def receive(sock):
    while True:
        # ❌ 고장의 핵심: '\n 까지'가 아니라 'recv 로 온 만큼'만 받는다.
        chunk = sock.recv(1024)
        if not chunk:
            print("\n[연결 종료] 서버와의 연결이 끊겼습니다.")
            break
        line = chunk.decode("utf-8", errors="replace").rstrip("\n")

        if line.startswith("TEXT|"):
            parts = line.split("|", 2)
            if len(parts) < 3:
                continue
            _, sender, text = parts
            print(text if sender == "시스템" else f"{sender}: {text}")

        elif line.startswith("FILE|"):
            parts = line.split("|", 3)
            if len(parts) < 4:
                print(f"📎 [깨진 파일 조각 도착] {line[:40]}...")
                continue
            _, sender, filename, b64 = parts
            # 잘려서 base64 길이가 4의 배수가 아니면 디코딩이 실패한다.
            # 그래도 '그나마 되는 데까지' 저장해 '깨진 파일'을 눈으로 보게 한다.
            usable = b64[: len(b64) // 4 * 4]
            try:
                data = base64.b64decode(usable)
            except Exception as e:
                print(f"📎 [{sender}] 파일 복원 실패: {e}")
                continue
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            save_as = os.path.join(DOWNLOAD_DIR, f"{sender}_{filename}")
            with open(save_as, "wb") as f:
                f.write(data)
            print(f"📎 [{sender}]님의 파일 저장 → {save_as} ({len(data)} bytes) "
                  f"— 열어서 멀쩡한지 확인해 보세요")

        else:
            print(f"[알 수 없는 메시지 = 잘린 뒷토막?] {line[:40]}...")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    nickname = input("닉네임을 입력하세요: ").strip()
    sock.sendall((nickname + "\n").encode("utf-8"))

    threading.Thread(target=receive, args=(sock,), daemon=True).start()
    print("대화 시작!  (작은 파일: /file small.png,  큰 파일: /file big.png,  종료: Ctrl+C)\n")

    try:
        while True:
            text = input()
            if not text:
                continue

            if text.startswith("/file "):
                path = text[len("/file "):].strip()
                try:
                    with open(path, "rb") as f:
                        raw = f.read()
                except OSError:
                    print(f"[오류] 파일을 열 수 없습니다: {path}")
                    continue
                b64 = base64.b64encode(raw).decode("ascii")
                filename = os.path.basename(path)
                # 보낼 때는 진짜 client.py 와 똑같이 한 줄로 보낸다.
                # 문제는 '보내기'가 아니라 '받기'가 recv 라 잘린다는 것.
                sock.sendall(f"FILE|{filename}|{b64}\n".encode("utf-8"))
                print(f"(파일 보냄: {filename}, {len(raw)} bytes / base64 {len(b64)}글자)")
            else:
                sock.sendall(f"TEXT|{text}\n".encode("utf-8"))

    except (EOFError, KeyboardInterrupt):
        print("\n[클라이언트] 대화를 종료합니다.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
