"""
Week 10 - ws_server.py  :  웹(브라우저)용 WebSocket 서버
============================================================
브라우저는 raw TCP 소켓을 못 씁니다. WebSocket 만 됩니다.
그래서 '통로' 만 WebSocket 으로 바꿉니다 — 서버의 두뇌는 그대로!

  build_server()  ← 8주차에서 만든 ChatServer/Room/Repository 두뇌를 그대로 재사용
  WSConn          ← WebSocket 을 '소켓처럼' 보이게 하는 어댑터 (sendall 만 흉내)

메시지 포맷·암호화는 기존과 동일합니다:
  - AES-256-GCM 로 암호화된 'TAG|보낸이|내용' 한 줄 (codec.py / messages.py)
  - 브라우저 쪽은 codec.js 가 같은 AES 를 SubtleCrypto 로 처리

준비:  pip install websockets
실행:  python ws_server.py            (기본 0.0.0.0:8765)
"""

import asyncio

import websockets

from server import build_server        # ★ 그 두뇌를 그대로 가져온다

HOST = "0.0.0.0"
PORT = 8765

server = build_server()                # ChatServer(codec=AES, rooms, connections)


class WSConn:
    """WebSocket 을 '소켓처럼' 보이게 하는 어댑터.

    ChatServer 는 conn.sendall(bytes) 로 메시지를 보낸다(동기).
    여기서는 그 바이트를 큐에 넣고, 별도 writer 가 WebSocket 으로 흘려보낸다.
    → ChatServer/Room/CommandHandler 를 한 줄도 안 고치고 재사용할 수 있다.
    """
    def __init__(self, ws):
        self.ws = ws
        self.queue = asyncio.Queue()

    def sendall(self, data):           # ChatServer 가 부르는 그 이름 그대로
        self.queue.put_nowait(data)


def as_text(frame):
    """WS 프레임(텍스트=str, 바이너리=bytes)을 안전하게 문자열로. 깨진 바이트는 대체."""
    if isinstance(frame, bytes):
        return frame.decode("utf-8", "replace")
    return frame


async def pump_out(conn):
    """큐에 쌓인 바이트를 WebSocket 으로 내보낸다 (WS 는 개행 프레이밍이 필요 없음)."""
    while True:
        data = await conn.queue.get()
        try:
            await conn.ws.send(data.rstrip(b"\n").decode("utf-8"))
        except Exception:          # 연결 종료 등 어떤 오류든 writer 는 조용히 끝난다
            break


async def handle(ws):
    conn = WSConn(ws)
    # 첫 메시지 = 닉네임(평문). TCP 클라이언트의 '첫 줄 = 닉네임' 과 같은 약속.
    try:
        nickname = as_text(await ws.recv()).strip()
    except Exception:              # 닉네임을 못 받으면(즉시 끊김 등) 조용히 종료
        return
    if not nickname:
        return

    session = server.on_connect(conn, nickname)     # 두뇌 그대로
    writer = asyncio.create_task(pump_out(conn))
    try:
        async for message in ws:                    # WS 메시지 1개 = 암호문 한 줄
            server.on_line(session, as_text(message).strip())  # 두뇌가 해독·처리(실패는 내부에서 무시)
    except Exception:              # 연결 종료·프로토콜 오류 등 어떤 오류든 아래 finally 로
        pass
    finally:
        try:
            server.on_disconnect(session)           # 정리도 실패해도 서버는 계속
        except Exception:
            pass
        writer.cancel()


async def main():
    print(f"[WS서버] ws://{HOST}:{PORT}  대기 중... (Codec={server.codec.name}, Ctrl+C 종료)")
    # max_size: 기본 1MB 면 파일 전송이 막힌다(암호화+base64 로 더 커짐) → 넉넉히 16MB.
    async with websockets.serve(handle, HOST, PORT, max_size=16 * 1024 * 1024):
        await asyncio.Future()          # 영원히 대기


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[WS서버] 종료합니다.")
