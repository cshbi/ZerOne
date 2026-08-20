// ============================================================
// app.js  :  WebSocket + 코덱 + 메시지를 묶은 작은 도우미
// ============================================================
// 두 화면(rooms.html, chat.html)이 함께 씁니다.
// 파이썬 client.py 와 하는 일이 똑같습니다 — 통로만 WebSocket 일 뿐:
//   접속 → 첫 줄로 닉네임(평문) → 이후 메시지는 AES 로 암호화해 주고받기
// ============================================================

// 서버 주소: http://localhost:8000 으로 열었으면 ws://localhost:8765 로 붙는다.
const WS_URL = `ws://${location.hostname || "127.0.0.1"}:8765`;

class ChatSocket {
  constructor(nickname) {
    this.nick = nickname;
    this.ws = null;
    this.onMessage = null;   // (parsed) => {}
    this.onOpen = null;
    this.onClose = null;
  }

  connect() {
    this.ws = new WebSocket(WS_URL);
    this.ws.onopen = () => {
      this.ws.send(this.nick);              // 첫 메시지 = 닉네임(평문 핸드셰이크)
      if (this.onOpen) this.onOpen();
    };
    this.ws.onmessage = async (e) => {
      try {
        const line = await Codec.decode(e.data);   // AES 복호화
        if (this.onMessage) this.onMessage(parseWire(line));
      } catch (err) {
        console.warn("복호화 실패(무시):", err);
      }
    };
    this.ws.onclose = () => { if (this.onClose) this.onClose(); };
  }

  async _send(wireLine) {
    this.ws.send(await Codec.encode(wireLine));     // AES 암호화해서 전송
  }
  sendText(t)         { return this._send(Wire.text(this.nick, t)); }
  sendEmoji(name)     { return this._send(Wire.emoji(this.nick, name)); }
  sendFile(name, b64) { return this._send(Wire.file(this.nick, name, b64)); }
  command(cmd)        { return this._send(Wire.command(this.nick, cmd)); }

  close() { if (this.ws) this.ws.close(); }
}

// URL 쿼리에서 값 꺼내기 (chat.html?nick=철수&room=잡담)
function qs(name) {
  return new URLSearchParams(location.search).get(name) || "";
}
