# Week 10 — 웹 클라이언트 (WebSocket · JavaScript)

우리 채팅을 **브라우저**에서 씁니다. 서버의 두뇌는 그대로 두고 **통로만 WebSocket 으로**
갈아끼웠습니다 — 지금까지 계약(Repository/Transport)으로 분리해 둔 것의 마지막 증명입니다.

> 이 웹 클라이언트가 **다음에 만들 파이썬 클라이언트의 '기초/참조'** 입니다.
> 웹이 확정한 약속(`PROTOCOL.md`)을 파이썬으로 옮기면 됩니다.

## 준비물
```bash
python -m pip install websockets
```
> **꼭 `python -m pip` 로 설치하세요** (`pip install ...` 가 아니라).
> `serve.py` 를 돌리는 '바로 그 파이썬' 에 설치되도록 보장합니다. (아래 '문제 해결' 참고)

(암호화는 브라우저 표준 crypto.subtle + 파이썬 cryptography 를 씁니다. `cryptography` 는 6주차부터 이미 설치.)

## 실행 (명령 하나)
```bash
python serve.py
```
그다음 브라우저에서 **http://localhost:8000/rooms.html** 로 접속.
> ⚠️ 반드시 `http://localhost` 로 여세요. HTML 을 파일(file://)로 직접 열면 브라우저가
> 암호화(crypto.subtle)를 막아 동작하지 않습니다. `serve.py` 가 그래서 http 로 서빙합니다.

## 문제 해결 (자주 나는 오류)

### ① `ModuleNotFoundError: No module named 'websockets'`
`pip install websockets` 를 했는데도 이 오류가 나면, **설치된 파이썬과 `serve.py` 를 돌리는
파이썬이 다른 것**입니다 (한 PC 에 파이썬이 여러 개면 흔함).

**해결** — 실행하는 그 파이썬에 직접 설치:
```bash
python -m pip install websockets
```
설치됐는지 확인:
```bash
python -c "import websockets; print(websockets.__version__)"
```
버전 숫자가 뜨면 성공 → 다시 `python serve.py`.

**그래도 안 되면** — 어떤 파이썬을 쓰는지 확인하고, 그 파이썬으로 설치:
```bash
python -c "import sys; print(sys.executable)"     # 지금 쓰는 파이썬 경로
```
- Windows 에서 `python` 이 안 먹히면 py 런처로:  `py -m pip install websockets`  후  `py serve.py`
- VS Code 를 쓰면, 우하단/상단의 '파이썬 인터프리터' 가 방금 설치한 그 파이썬과 같은지 확인.

### ② 브라우저에서 아무 반응이 없다 / codec_test 가 실패한다
- 반드시 **http://localhost:8000/...** 로 여세요. HTML 파일을 **더블클릭(file://)** 하면
  브라우저가 암호화(crypto.subtle)를 막습니다. `serve.py` 가 http 로 서빙하는 이유입니다.
- `serve.py` 를 고친 뒤엔 **껐다 다시 실행**(Ctrl+C → `python serve.py`). HTML/CSS/JS 만 고쳤으면
  브라우저 **새로고침(F5)** 이면 됩니다(캐시는 서버가 꺼 둠).

### ③ 포트가 이미 쓰인다 (`Address already in use` / 8000·8765)
- 이전에 켠 `serve.py` 가 아직 떠 있는 겁니다. 그 창을 `Ctrl+C` 로 끄고 다시 실행.

### ④ 혼자인데 방 인원이 계속 늘어난다
- 창(대화창) 하나당 접속 1개 = 멤버 1명입니다. **대화창을 닫으면** 줄어듭니다.
  같은 방을 다시 클릭하면 새 창을 열지 않고 기존 창을 앞으로 가져옵니다.

## 처음 한 번 — 자가진단
http://localhost:8000/**codec_test.html** 을 열어 "모두 통과" 가 뜨는지 확인하세요.
→ 브라우저 AES 가 파이썬 AES 와 호환되는지 검사합니다. (여기서 통과하면 채팅도 됩니다)

## 사용법
1. `rooms.html` 에서 닉네임 입력 → **방 목록** 이 보인다.
2. **방 만들기** 로 방 생성, **새로고침** 으로 목록 갱신.
3. 방을 **클릭** 하면 **새 창** 으로 대화창(`chat.html`)이 열린다.
4. 대화창에서: 텍스트 입력·전송, 📎 파일, 이모티콘 버튼(😄❤️👍😢😮), **나가기**.
   - 입장하면 **기존 대화 최근 5개** 가 먼저 보인다.
   - **내가 보낸 말은 오른쪽(노랑)**, 남의 말은 왼쪽(흰색) — 카카오톡처럼.

## 파일
폴더를 **`server/`(파이썬 백엔드)** 와 **`client/`(브라우저)** 로 나눴습니다.
`serve.py`(루트) 하나가 둘을 이어 실행합니다.

```
week10_web_client/
├─ serve.py            # 실행기: client/ 를 HTTP 로, server/ 를 WebSocket 으로
├─ README.md · PROTOCOL.md
├─ server/             # ── 파이썬 백엔드 ──
│  ├─ ws_server.py     #   WebSocket 서버 (8주차 두뇌 build_server 그대로, 통로만 WS)
│  └─ server.py · command.py · room.py · repository.py · session.py · interfaces.py
│     · codec.py · messages.py     #   8주차 두뇌 그대로 재사용
└─ client/             # ── 브라우저 ──
   ├─ rooms.html       #   방 리스트 화면
   ├─ chat.html        #   대화창 (새 창으로 열림)
   ├─ codec.js         #   브라우저 AES-256-GCM (server/codec.py 와 짝)
   ├─ messages.js      #   파이프 포맷 파싱 (server/messages.py 와 짝)
   ├─ app.js           #   WebSocket+코덱+메시지 도우미 (파이썬 client 와 같은 일)
   ├─ style.css        #   카카오톡 느낌 UI
   └─ codec_test.html  #   AES 상호운용 자가진단
```

## 구조 한눈에
```
client/ 브라우저 ──WebSocket(AES)──▶ server/ws_server.py ──▶ ChatServer 두뇌
  codec.js / messages.js              (WSConn 어댑터)        (Room·Repository·Command)
        ↑ server/codec.py · messages.py 와 '완전히 같은 약속'
serve.py 가 client/ 를 http://localhost:8000 으로, server/ 를 ws://localhost:8765 로 함께 띄운다.
```

## 다음 — 파이썬 클라이언트 (숙제)
`PROTOCOL.md` 를 보고 `websockets` 라이브러리로 파이썬 클라이언트를 만들어 보세요.
서버·`codec.py`·`messages.py` 는 **그대로 재사용** — 웹이 한 일을 파이썬으로 옮기는 것뿐입니다.

## ⚠️ 왜 이 AES 는 '진짜 보안'이 아닌가 (마지막 교훈)

`client/codec.js` 를 열어 보면 열쇠가 그대로 보입니다:
```js
const PASSPHRASE = "우리반-공용-비밀열쇠-2026";
```
이 파일은 브라우저로 **다운로드** 되므로, **누구나 소스보기로 이 열쇠를 읽을 수 있습니다.**
열쇠가 공개되면, 회선을 캡처한 사람은 AES 라도 **전부 복호화**할 수 있습니다.

→ **5주차 XOR 에서 배운 그 교훈 그대로**: "열쇠가 코드에 박혀 있으면 진짜 보안이 아니다."
  알고리즘을 AES 로 세게 해도, **'코드에 박힌 공유 열쇠'** 라는 근본 문제는 안 풀립니다.
  (파이썬 `server/codec.py` 의 `SECRET_PASSPHRASE` 도 똑같이 배포되므로 동일한 한계)

### 그래서 진짜 답: wss:// (TLS)
- **키 교환**: 접속마다 새 세션 키를 협상 → 열쇠가 **코드에도 회선에도 남지 않음**
- **서버 인증**(인증서): '진짜 서버' 인지 확인 → 가짜 서버(evil twin)도 막음

이 두 가지가 우리의 '코드에 박힌 AES' 가 절대 못 하는 일이고, 그래서 결론이 **"진짜 보안은 TLS"** 입니다.
이 웹의 AES 는 *"암호화 부품을 끼우면 회선이 어떻게 바뀌나"* 를 보여 주는 **학습용**입니다.

> 수업 마무리 활동: 학생에게 `codec.js` 를 열어 열쇠를 직접 찾게 하고 —
> "그럼 이 AES 는 진짜 안전할까?" 를 스스로 답하게 하면, 5주차 XOR → 6주차 스니퍼 →
> 10주차 웹으로 이어진 **보안 서사가 완성**됩니다.

## ws:// 와 wss:// 차이 (간단히)
`http` : `https` = `ws` : `wss` — 끝의 **`s` = Secure = TLS(암호화)** 입니다.

| | `ws://` | `wss://` |
|---|---------|----------|
| 정체 | WebSocket **평문** (그냥 TCP 위) | WebSocket **+ TLS** (암호화된 통로 위) |
| 비유 | `http://` | `https://` |
| 회선에서 | **그대로 보임** (스니퍼가 다 읽음) | **안 보임** (중간자가 못 읽음) |
| 열쇠 | 앱에서 AES 하면 열쇠가 코드에 노출됨 | TLS 가 접속마다 **새 키 교환** — 코드·회선에 열쇠 없음 |
| 서버 인증 | 없음 | **인증서로 '진짜 서버' 확인** |

→ `wss` 는 통로 자체를 TLS 로 암호화하므로, codec.js 에서 억지로 AES 를 안 해도(열쇠 노출 없이)
회선이 안전합니다. 그래서 **"진짜 보안은 TLS(=wss)"**.

## 실습 후 배포(선택)
지금은 로컬 실습이라 `ws://localhost`(평문) 를 씁니다. 실제 배포 때는 `wss://`(TLS) 로 열면
전송 구간까지 안전해집니다. "진짜 보안은 TLS" — 6주차부터의 결론이 여기서 완성됩니다.
