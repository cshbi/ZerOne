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
from message import Message, TextMessage, FileMessage, LocMessage

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
        msg = Message.parse_from_server(line)
        if msg is None:
            print(f"[알 수 없는 메시지] {line[:30]}")
            continue
        msg.display() # TEXT/FILE/LOC 각자 알아서 자기 방식대로 출력
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
                    msg, size = FileMessage.from_path(path) #msg는 FileMessage 클래스의 인스턴스
                except OSError:
                    print(f"[오류] 파일을 열 수 없습니다: {path}")
                    continue
                sock.sendall((msg.to_client_line() + "\n").encode("utf-8"))
                print(f"(파일 보냄: {msg.filename}, {size} bytes)")
 
            elif text.startswith("/loc "):
                coords = text[len("/loc "):].strip()
                lat, lon = coords.split()
                msg = LocMessage(lat, lon)
                sock.sendall((msg.to_client_line() + "\n").encode("utf-8"))
                print(f"(위치 보냄: 위도 {lat}, 경도 {lon})")
 
            else:
                msg = TextMessage(text)
                sock.sendall((msg.to_client_line() + "\n").encode("utf-8"))
                    
            # ==================================================

    except (EOFError, KeyboardInterrupt):
        print("\n[클라이언트] 대화를 종료합니다.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
