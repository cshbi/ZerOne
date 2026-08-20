// ============================================================
// codec.js  :  브라우저용 AES-256-GCM 코덱 (파이썬 codec.py 와 짝)
// ============================================================
// 파이썬 AesGcmCodec 과 '완전히 같은' 방식이라 서로 통합니다:
//   · 열쇠 = SHA-256(공용 암호)  → 32바이트
//   · 암호문 = base64( nonce(12) + AES-GCM(암호문+태그) )
// 브라우저는 표준 SubtleCrypto(crypto.subtle) 로 AES 를 처리합니다.
//
// ※ 서버(ws_server.py)와 반드시 같은 PASSPHRASE 여야 서로 알아봅니다.
//
// ⚠️⚠️ 중요 — 이건 '진짜 보안'이 아닙니다 ⚠️⚠️
//   아래 PASSPHRASE 는 이 codec.js 파일에 그대로 적혀 있고, 이 파일은 브라우저로
//   '다운로드' 됩니다. 즉 누구나 개발자도구/소스보기로 이 열쇠를 볼 수 있습니다.
//   열쇠가 공개되면, 회선을 캡처한 사람은 AES 라도 전부 복호화할 수 있습니다.
//   → 5주차 XOR 때 배운 그 교훈 그대로: "열쇠가 코드에 박혀 있으면 진짜 보안이 아니다".
//     (알고리즘이 AES 로 세져도, '코드에 박힌 공유 열쇠'라는 근본 문제는 그대로)
//
//   ✅ 진짜 답은 wss:// (TLS): 접속마다 새 세션 키를 '교환'해서 열쇠가 코드에도
//      회선에도 남지 않고, 서버 인증서로 '진짜 서버'인지도 확인합니다.
//      이 AES 코덱은 '암호화 부품을 끼우면 회선이 어떻게 바뀌나'를 보여 주는 학습용입니다.
// ============================================================

const PASSPHRASE = "우리반-공용-비밀열쇠-2026";   // codec.py 의 SECRET_PASSPHRASE 와 동일
                                                 //  ↑ 이 값이 브라우저에서 그대로 보인다! (위 ⚠️ 참고)

// 문자열 <-> 바이트
const enc = new TextEncoder();
const dec = new TextDecoder();

// base64 <-> 바이트
function bytesToB64(bytes) {
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}
function b64ToBytes(b64) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

// 공용 암호 -> AES 열쇠 (한 번만 만들어 재사용)
let _keyPromise = null;
function getKey() {
  if (!_keyPromise) {
    _keyPromise = crypto.subtle
      .digest("SHA-256", enc.encode(PASSPHRASE))          // 32바이트
      .then((hash) =>
        crypto.subtle.importKey("raw", hash, "AES-GCM", false, ["encrypt", "decrypt"])
      );
  }
  return _keyPromise;
}

const Codec = {
  // 전송용 문자열('TEXT|철수|안녕') -> 암호문 base64 한 줄
  async encode(wireLine) {
    const key = await getKey();
    const nonce = crypto.getRandomValues(new Uint8Array(12));   // 매번 새 난수
    const ct = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv: nonce }, key, enc.encode(wireLine)
    );
    const packed = new Uint8Array(nonce.length + ct.byteLength);
    packed.set(nonce, 0);
    packed.set(new Uint8Array(ct), nonce.length);
    return bytesToB64(packed);
  },

  // 암호문 base64 한 줄 -> 원래 문자열
  async decode(b64line) {
    const key = await getKey();
    const raw = b64ToBytes(b64line.trim());
    const nonce = raw.slice(0, 12);
    const ct = raw.slice(12);
    const pt = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: nonce }, key, ct
    );
    return dec.decode(pt);
  },
};
