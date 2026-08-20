# -*- coding: utf-8 -*-
"""
Week 10(최종 정리 · 웹 클라이언트) 강의자료(PPT) 생성 스크립트
실행:  python make_ppt.py   →   Week10_웹클라이언트_최종정리.pptx
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ppt_theme import Deck

KICKER = "파이썬으로 만드는 실시간 채팅 프로그램 · 최종"

d = Deck()

# ── 1. 표지 ────────────────────────────────────────────────
d.title(
    kicker=KICKER,
    title="우리가 만든 메신저, 웹으로 열다",
    subtitle="브라우저 클라이언트 · WebSocket, 그리고 전체 여정 정리",
    notes=(
        "마지막 회차: 웹 클라이언트로 마무리하고, 1~10주 전체를 한 번에 되짚는다.\n"
        "핵심 메시지: '서버 두뇌는 그대로, 통로만 WebSocket 으로 갈아끼웠다' — DI/Repository 의 결실."
    ),
)

# ── 2. 도입 질문 ──────────────────────────────────────────
d.big_question(
    question="터미널·앱·웹이 같은 채팅에 붙는다.\n어떻게 가능했을까?",
    hint="서버를 '두뇌'와 '통로'로 나눠 뒀기 때문 — 통로만 갈아끼우면 된다.",
    notes=(
        "브라우저는 raw TCP 를 못 쓴다 → WebSocket. 그런데 서버 두뇌(ChatServer/Room/Repository)는\n"
        "계약으로 분리돼 있어서, 통로(Transport)만 WebSocket 으로 바꾸면 그대로 붙는다."
    ),
)

# ── 3. 전체 시스템 구성 (요청) ────────────────────────────
d.code(
    "전체 시스템 구성 — 서비스가 도는 방식",
    "① 브라우저 (client/)   rooms.html · chat.html · codec.js · messages.js · app.js\n"
    "        │  메시지를 AES 로 암호화(pipe 포맷)해서 보냄\n"
    "        ▼\n"
    "② WebSocket   ws://localhost:8765\n"
    "        │\n"
    "        ▼\n"
    "③ server/ws_server.py   WSConn 이 WebSocket 을 '소켓처럼' 보이게 함\n"
    "        │  (통로만 WS, 두뇌는 그대로)\n"
    "        ▼\n"
    "④ ChatServer (8주차 두뇌)   Room · RoomRepository · CommandHandler\n"
    "        │  codec.py · messages.py 로 해독→처리→방 멤버에게 다시 전송\n"
    "\n"
    "※ serve.py 하나가:  client/ → http://:8000,   server/ → ws://:8765  동시 실행",
    caption="브라우저(client/) ↔ WebSocket ↔ ws_server(통로) ↔ ChatServer 두뇌(server/).",
    notes=(
        "이 한 장이 '전체가 어떻게 연결돼 도는지'다. serve.py 가 파일서버(http)와 채팅서버(ws)를 함께 띄운다.\n"
        "④의 ChatServer 는 8주차 그대로 — 웹을 위해 두뇌를 새로 만들지 않았다는 점을 강조."
    ),
)

# ── 4. 통로만 갈아끼웠다 ──────────────────────────────────
d.bullets(
    "서버는 그대로, 통로만 갈아끼웠다",
    [
        "ws_server.py 는 build_server() 로 만든 '그 두뇌' 를 그대로 쓴다",
        "WSConn: WebSocket 에 sendall 만 흉내 내는 얇은 어댑터",
        ("→ ChatServer·Room·CommandHandler 를 한 줄도 안 고쳤다", 1),
        "메시지 약속(AES · pipe 포맷)도 파이썬과 완전히 동일",
        ("client/codec.js ↔ server/codec.py,   messages.js ↔ messages.py", 1),
        "이게 5주차 계약(Codec/Repository)으로 분리해 둔 진짜 이유",
    ],
    notes=(
        "DI/계약의 결실을 정리. 통로(Transport)만 갈아끼우면 터미널·웹 어디든 붙는다.\n"
        "브라우저 codec.js 는 파이썬 codec.py 와 '같은 약속' 이라 서로 통한다."
    ),
)

# ── 5. 웹 클라이언트 기능 ─────────────────────────────────
d.bullets(
    "웹 클라이언트가 하는 일",
    [
        "방 리스트 화면 → 방 만들기 · 클릭하면 새 창으로 대화창",
        "대화: 입장하면 기존 대화 '최근 5개' 를 먼저 보여 준다",
        "내가 보낸 말은 오른쪽(노랑), 남의 말은 왼쪽 — 카카오톡처럼",
        "파일 전송(base64) · 이모티콘(😄❤️👍😢😮)",
        "순수 HTML + JavaScript (프레임워크·빌드 없음)",
    ],
    notes=(
        "요청 기능이 다 들어갔다. 방마다 창을 하나만 유지(같은 방 재클릭 시 새 연결 안 만듦).\n"
        "codec_test.html 로 브라우저 AES 가 파이썬과 통하는지 먼저 확인하는 흐름."
    ),
)

# ── 6. ws vs wss (요청) ───────────────────────────────────
d.table(
    "ws:// 와 wss:// — 통로의 보안",
    ["구분", "ws://", "wss://"],
    [
        ["정체", "WebSocket 평문 (그냥 TCP 위)", "WebSocket + TLS (암호화 통로)"],
        ["비유", "http://", "https://"],
        ["회선에서", "그대로 보임 (스니퍼가 읽음)", "안 보임 (중간자 못 읽음)"],
        ["열쇠", "앱에서 AES 하면 코드에 노출", "접속마다 새 키 교환 (노출 없음)"],
        ["서버 인증", "없음", "인증서로 '진짜 서버' 확인"],
    ],
    col_widths=[1.7, 4.75, 4.75],
    caption="끝의 s = Secure = TLS. wss 는 통로 자체를 암호화 → \"진짜 보안은 TLS(=wss)\".",
    notes=(
        "http:https = ws:wss 로 기억. 지금은 로컬이라 ws://localhost(평문), 배포 땐 wss://.\n"
        "wss 는 키를 코드·회선에 남기지 않고(키 교환) 서버 신원까지 확인한다 — 우리 AES 가 못 하는 것."
    ),
)

# ── 7. 왜 codec.js AES 는 진짜 보안 아닌가 ────────────────
d.bullets(
    "그런데 — 우리 AES 는 '진짜 보안'이 아니다",
    [
        "codec.js 는 브라우저로 다운로드된다 → 누구나 소스보기로 열쇠를 본다",
        ("const PASSPHRASE = \"우리반-공용-비밀열쇠-2026\"  ← 그대로 보임", 1),
        "열쇠가 공개면, 회선을 캡처한 사람은 AES 라도 다 복호화한다",
        "5주차 XOR 교훈 그대로: '열쇠가 코드에 박히면 진짜 보안 아님'",
        "진짜 답은 wss(TLS): 키 교환 + 서버 인증 (코드·회선에 열쇠 없음)",
    ],
    notes=(
        "마무리 활동: 학생에게 codec.js 를 열어 열쇠를 직접 찾게 하고 '이게 안전할까?' 를 묻는다.\n"
        "5주차 XOR → 6주차 스니퍼 → 10주차 웹 AES 노출 → wss. 보안 서사의 완성."
    ),
)

# ── 8. 전체 여정 정리 ─────────────────────────────────────
d.bullets(
    "우리가 걸어온 길 (1 → 10주)",
    [
        "1~2주: 소켓 · 브로드캐스트 — 절차적으로 '되게' 만들기",
        "3주: 파일 전송 → if/elif 분기 지옥 (고통)",
        "4주: 메시지를 객체로 · 다형성 (Factory 등장)",
        "5주: Codec · 의존성 주입 · 계약 (Strategy) + 평문 탈취 데모",
        "6~7주: 방 — 전역 dict(엉성) → Room 객체 + Repository",
        "8주: 서버 리팩터링 — Session · Command 로 협력",
        "9주(번외): 데이터베이스 — SQLite, Repository 의 또 다른 구현체",
        "10주: 웹 클라이언트 — 통로만 WebSocket 으로",
    ],
    notes=(
        "'느끼게 한 다음 도구를 꺼낸다' 가 매주 반복됐다. 절차적 → 객체 → 다형성 → DI → 방 → 정리 → DB → 웹.\n"
        "if/elif 로 시작한 코드가 지금 어떻게 변했는지 처음과 끝을 나란히 보여 주면 좋다."
    ),
)

# ── 9. 사실은 교과서 패턴 ─────────────────────────────────
d.table(
    "사실 — 우리가 만든 게 '교과서 패턴' 이었다",
    ["패턴", "우리 코드", "한 일"],
    [
        ["Factory", "from_wire · make_message", "알맞은 객체를 만들어 줌"],
        ["Strategy", "Codec (평문↔AES)", "동작(알고리즘)을 갈아끼움"],
        ["Repository", "RoomRepository (메모리↔파일↔DB)", "저장 방식을 갈아끼움"],
        ["의존성 주입(DI)", "ChatServer(codec, rooms, ...)", "부품을 밖에서 꽂음"],
    ],
    col_widths=[2.6, 5.0, 3.6],
    caption="새 개념이 아니다 — 우리가 만들어 쓰던 것에 '이름' 을 붙인 것. 다른 언어에서도 같은 이름으로 만난다.",
    notes=(
        "학생이 만든 코드가 곧 교과서 패턴이었음을 보여 주는 마무리. Java/C++ 어디서든 같은 이름으로 재회한다.\n"
        "이 어휘를 쥐여 주면 'Python 에만 갇힌다' 는 걱정이 사라진다."
    ),
)

# ── 10. 깨달음 ────────────────────────────────────────────
d.takeaway(
    headline="잘 나눠 두면,\n무엇이든 갈아끼울 수 있다.",
    points=[
        "통로(터미널·웹), 부품(Codec·저장소), 저장(메모리·파일·DB) — 다 교체 가능",
        "그 비결은 '계약으로 분리' — 5주차부터 쌓아온 설계",
        "if/elif 로 시작한 코드가, 이름표 붙은 교과서 패턴으로 자랐다",
        "그리고 — 진짜 보안은 코드에 박은 열쇠가 아니라 TLS(wss)",
    ],
    notes=(
        "전체를 한 문장으로: '잘 나눠 두면 갈아끼울 수 있다'. 이게 객체지향·DI 를 배운 진짜 이유.\n"
        "마지막으로 보안(진짜는 TLS) 을 다시 못 박으며 마무리."
    ),
)

# ── 11. 더 나아가기 ──────────────────────────────────────
d.bullets(
    "더 나아가기 (확장 과제)",
    [
        "파이썬 웹 클라이언트: PROTOCOL.md 보고 websockets 로 이식 (서버·codec 재사용)",
        "wss(TLS) 로 배포해 '진짜 전송 보안' 을 붙여 보기",
        "로그인/회원, 메시지 DB 영구 저장(9주차 SqliteRoomRepository 완성)",
        "읽음 표시 · 알림 · 이모티콘을 스티커(파일)로 (4주차 도전과제 연장)",
        "(회고) if/elif 로 시작했던 코드가 지금 어떻게 변했나?",
    ],
    notes=(
        "다음 걸음을 안내. 특히 '파이썬 클라 이식' 은 이 웹 클라가 확정한 프로토콜을 그대로 옮기는 것.\n"
        "회고 질문으로 12주(또는 마지막)를 닫는다."
    ),
)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "Week10_웹클라이언트_최종정리.pptx")
d.save(out)
print("저장 완료:", out)
print("슬라이드 수:", len(d.prs.slides._sldIdLst))
