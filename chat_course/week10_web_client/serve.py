"""
serve.py  :  웹 파일(HTTP) + 채팅(WebSocket) 을 '한 번에' 띄우는 실행기
============================================================
폴더를 둘로 나눴습니다:
  server/  ← 파이썬 백엔드 (ws_server.py + 8주차 두뇌)
  client/  ← 브라우저 (rooms.html, chat.html, codec.js ...)

이 실행기가 둘을 이어 줍니다:
  · http://localhost:8000   ← client/ 파일 제공
  · ws://localhost:8765     ← server/ws_server.py 의 채팅 서버

브라우저 암호화(crypto.subtle)는 'localhost 또는 https' 에서만 되므로,
HTML 을 file:// 로 직접 열지 말고 반드시 http://localhost 로 여세요.

준비:  python -m pip install websockets
실행:  python serve.py
접속:  http://localhost:8000/rooms.html
"""
import os
import sys
import threading
import http.server
import socketserver
import asyncio

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(HERE, "server")
CLIENT_DIR = os.path.join(HERE, "client")

# server/ 안의 모듈(ws_server, server, codec ...)을 import 할 수 있게 (맨 앞에 넣어 우선)
sys.path.insert(0, SERVER_DIR)
import ws_server        # server/ws_server.py  (import 만으론 서버가 켜지지 않음)

WEB_PORT = 8000


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    """client/ 폴더를 서빙하고, 수정이 새로고침에 바로 반영되도록 캐시를 끈다."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=CLIENT_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()


def run_http():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", WEB_PORT), NoCacheHandler) as httpd:
        print(f"[웹]  http://localhost:{WEB_PORT}/rooms.html  (여기로 접속)")
        httpd.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=run_http, daemon=True).start()
    try:
        asyncio.run(ws_server.main())     # WebSocket 채팅 서버 (메인)
    except KeyboardInterrupt:
        print("\n[종료]")
