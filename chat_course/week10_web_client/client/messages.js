// ============================================================
// messages.js  :  전송용 한 줄 <-> 메시지 (파이썬 messages.py 와 짝)
// ============================================================
// 포맷(파이프 구분)은 파이썬과 동일:
//   TEXT|보낸이|내용        EMOJI|보낸이|이름
//   FILE|보낸이|파일명|base64   SYS|보낸이|내용(시스템)
// ============================================================

// 파이썬 messages.py 의 EMOJI 와 동일하게 유지
const EMOJI = { smile: "😄", heart: "❤️", thumbsup: "👍", cry: "😢", wow: "😮" };

// ── 보낼 것 만들기 (전송용 한 줄) ──
const Wire = {
  text(sender, text)        { return `TEXT|${sender}|${text}`; },
  emoji(sender, name)       { return `EMOJI|${sender}|${name}`; },
  file(sender, name, b64)   { return `FILE|${sender}|${name}|${b64}`; },
  command(sender, cmd)      { return `TEXT|${sender}|${cmd}`; },   // /join 등도 텍스트
};

// ── 받은 한 줄 -> 화면에 쓸 객체 ──
//   { kind, sender, ... }  (파이썬 from_wire 의 브라우저 버전)
function parseWire(line) {
  const bar = line.indexOf("|");
  const tag = line.slice(0, bar);
  const rest = line.slice(bar + 1);
  if (tag === "TEXT") {
    const i = rest.indexOf("|");
    return { kind: "text", sender: rest.slice(0, i), text: rest.slice(i + 1) };
  }
  if (tag === "EMOJI") {
    const i = rest.indexOf("|");
    const name = rest.slice(i + 1);
    return { kind: "emoji", sender: rest.slice(0, i), name, face: EMOJI[name] || "❓" };
  }
  if (tag === "FILE") {
    const p = rest.split("|");            // sender | filename | b64
    return { kind: "file", sender: p[0], filename: p[1], b64: p.slice(2).join("|") };
  }
  if (tag === "SYS") {
    const i = rest.indexOf("|");
    return { kind: "sys", text: rest.slice(i + 1) };
  }
  return { kind: "text", sender: "?", text: line };   // 알 수 없는 건 그대로
}
