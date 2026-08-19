# -*- coding: utf-8 -*-
"""
Week 8 강의자료(PPT) 생성 스크립트
실행:  python make_ppt.py   →   Week08_서버리팩터링.pptx
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ppt_theme import Deck

KICKER = "파이썬으로 만드는 실시간 채팅 프로그램"

d = Deck()

# ── 1. 표지 ────────────────────────────────────────────────
d.title(
    kicker=KICKER,
    title="객체들이 협력하는 서버",
    subtitle="책임을 작은 객체로 나누기 · 새 기능이 '수술'이 아니라 '끼우기'가 되도록",
    notes=(
        "지금까지 만든 부품(메시지·Codec·Room·저장소)을 한데 모았더니 서버가 다시 커졌다.\n"
        "오늘 한 줄 목표: 책임을 작은 객체로 나누고, 새 명령(/rename, /w)을 '한 곳 수정'으로 추가한다.\n"
        "이번 주가 C단계(방)의 마무리이자, 서버 측 설계의 완성."
    ),
)

# ── 2. 도입 질문 ──────────────────────────────────────────
d.big_question(
    question="기능이 늘면서 서버 코드가 다시 커졌다.\n어떻게 정리하지?",
    hint="한 함수가 명령 해석·방 관리·전송·세션까지 다 떠안고 있지 않나요?",
    notes=(
        "7주차까지의 server.py 를 띄워, handle 함수가 점점 길어진 걸 보여 준다.\n"
        "문제는 '한 곳이 너무 많은 일을 한다'. 해결은 '나누기'."
    ),
)

# ── 3. 개념: 단일 책임 ────────────────────────────────────
d.bullets(
    "단일 책임 — 한 객체는 한 가지 일만",
    [
        "연결 관리 — 누가 접속해 있나 (Session / ConnectionManager)",
        "명령 해석 — /create, /join, /w … (CommandHandler)",
        "방 라우팅 — 누구에게 보낼까 (Room)",
        "저장 — 방을 어디에 둘까 (RoomRepository)",
        "각자 자기 일만 하면, 고칠 때 '어디를 볼지'가 분명해진다",
    ],
    notes=(
        "단일 책임: 한 객체가 바뀌어야 하는 이유는 하나뿐이어야 한다.\n"
        "지난주까지 이미 Room/Repository 는 나눠 두었다. 오늘은 연결·명령을 추가로 분리."
    ),
)

# ── 4. 개념: 협력 ─────────────────────────────────────────
d.bullets(
    "협력 — 작은 객체들이 서로 부른다",
    [
        "ChatServer 는 직접 일하지 않는다. 부품들에게 시키고 흐름만 잇는다",
        ("on_line: 명령이면 CommandHandler 에, 아니면 Room 에 넘긴다", 1),
        "CommandHandler 는 Room·Repository·Connections 를 불러 일을 처리",
        "조립(주입)은 한 곳에서: ChatServer(codec, rooms, connections)",
    ],
    notes=(
        "ChatServer 를 '지휘자'로 비유. 연주는 부품(객체)들이 한다.\n"
        "조립 지점(build_server)에서 부품을 주입 — 5·7주차 DI 의 연장선."
    ),
)

# ── 5. code: 세션 ─────────────────────────────────────────
d.code(
    "session.py — 접속을 객체로",
    "class Session:                 # 접속한 한 사람\n"
    "    def __init__(self, conn, nickname):\n"
    "        self.conn = conn\n"
    "        self.nickname = nickname\n"
    "        self.room = None       # 현재 방\n"
    "\n"
    "class ConnectionManager:       # 모든 Session 관리\n"
    "    def add(self, conn, nickname): ...\n"
    "    def remove(self, conn): ...\n"
    "    def find_by_nickname(self, name): ...   # 귓속말에 사용",
    caption="흩어져 있던 접속 정보(닉네임·현재 방)가 Session 한 곳으로.",
    notes=(
        "Session 이 생기면서, 서버 곳곳의 작은 딕셔너리(nickname_of, room_of)가 사라진다.\n"
        "find_by_nickname 은 귓속말(/w) 구현에 쓰인다 — 다음 슬라이드 명령 표와 연결."
    ),
)

# ── 6. code: 명령 표 ──────────────────────────────────────
d.code(
    "command.py — 명령을 '표'로",
    "class CommandHandler:\n"
    "    def __init__(self, server):\n"
    "        self.server = server\n"
    "        self.table = {                 # 명령 -> 처리 메서드\n"
    "            \"/create\": self.cmd_create,\n"
    "            \"/join\":   self.cmd_join,\n"
    "            \"/rename\": self.cmd_rename,   # 새 명령\n"
    "            \"/w\":      self.cmd_whisper,  # 새 명령\n"
    "        }\n"
    "    def handle(self, session, text):\n"
    "        cmd, arg = split(text)\n"
    "        self.table[cmd](session, arg)   # if/elif 대신 표에서 찾기",
    caption="긴 if/elif 대신 표(dict). 새 명령은 표에 한 줄 + 메서드 하나.",
    notes=(
        "4주차 메시지 등록표(registry)와 같은 발상 — 분기 대신 표.\n"
        "새 명령을 추가해도 handle 코드는 안 바뀐다. 표와 메서드만 는다."
    ),
)

# ── 7. code: 지휘하는 서버 ────────────────────────────────
d.code(
    "server.py — 조립하고 흐름만 지휘",
    "class ChatServer:\n"
    "    def __init__(self, codec, rooms, connections):  # 주입\n"
    "        self.codec = codec; self.rooms = rooms\n"
    "        self.connections = connections\n"
    "        self.commands = CommandHandler(self)\n"
    "\n"
    "    def on_line(self, session, line):\n"
    "        msg = self.codec.decode(line)\n"
    "        if isinstance(msg, TextMessage) and msg.text.startswith(\"/\"):\n"
    "            self.commands.handle(session, msg.text)   # 명령은 위임\n"
    "        else:\n"
    "            session.room.post(msg, self.raw_send)     # 메시지는 방으로",
    caption="ChatServer 는 '누구에게 넘길지'만 정한다. 일은 부품이 한다.",
    notes=(
        "on_line 이 짧다 — 분기 두 갈래(명령/메시지)뿐, 나머지는 위임.\n"
        "7주차까지 길었던 handle 이 작은 객체들로 흩어지며 읽기 쉬워졌다."
    ),
)

# ── 8. 실행 결과 (실제 캡처) ──────────────────────────────
d.terminals(
    "직접 돌려보자 — 이름 변경과 귓속말",
    [
        ("민수",
         "/join 잡담\n"
         "다들 안녕\n"
         "민수: 다들 안녕\n"
         "*** 영희 님이 영희짱(으)로\n"
         "    이름을 바꿨습니다 ***\n"
         "영희짱: 이름 바꿨어\n"
         "/w 영희짱 우리끼리 비밀\n"
         "(귓속말 → 영희짱) 나: 우리끼리 비밀"),
        ("영희 → 영희짱",
         "/join 잡담\n"
         "민수: 다들 안녕\n"
         "/rename 영희짱\n"
         "이름 바꿨어\n"
         "영희짱: 이름 바꿨어\n"
         "\n"
         "(귓속말) 민수: 우리끼리 비밀\n"
         "← 둘만 보인다"),
        ("새 명령을 추가한 곳",
         "command.py 의 표:\n"
         "\"/rename\": self.cmd_rename,\n"
         "\"/w\": self.cmd_whisper,\n"
         "\n"
         "→ 서버 본체(server.py)는\n"
         "   한 줄도 안 고쳤다"),
    ],
    notes=(
        "실제로 server.py + 두 클라이언트로 캡처. /rename 과 /w 가 동작한다.\n"
        "데모 포인트: 귓속말은 방 전체가 아니라 두 사람에게만 간다.\n"
        "핵심: 두 새 명령을 넣을 때 server.py 는 건드리지 않았다 — command.py 표에 두 줄."
    ),
)

# ── 9. 깨달음 ─────────────────────────────────────────────
d.takeaway(
    headline="설계가 좋으면, 기능 추가가 '수술'이 아니라 '끼우기'가 된다.",
    points=[
        "한 객체는 한 가지 일만 (단일 책임)",
        "ChatServer 는 조립·지휘, 일은 부품이 (협력)",
        "새 명령 = 표에 한 줄 + 메서드 하나, 본체는 그대로",
        "다음 단계: 같은 서버에 화면(GUI)·웹 클라이언트를 붙인다",
    ],
    notes=(
        "1~9주를 한 문장으로 회수: 절차적 → 객체 → 다형성 → DI → 방 → 협력하는 서버.\n"
        "여기까지가 서버의 완성. 10주부터는 '서버는 그대로 두고' 클라이언트만 바꾼다.\n"
        "잘 만든 서버(계약)는 클라이언트 종류를 가리지 않는다고 예고."
    ),
)

# ── 10. 사실은 '교과서 패턴' 이었다 (Factory vs Strategy) ──
d.table(
    "사실은 — 우리가 만든 게 '교과서 패턴' 이었다",
    ["구분", "팩토리 (Factory)", "전략 (Strategy)"],
    [
        ["하는 일", "알맞은 객체를 만들어 준다", "동작(알고리즘)을 갈아끼운다"],
        ["핵심 질문", "무엇을 만들까?", "어떻게 처리할까?"],
        ["우리 코드", "from_wire, make_message", "Codec, RoomRepository"],
        ["갈아끼운 예", "한 줄 → 알맞은 Message 객체", "평문 ↔ AES,  메모리 ↔ 파일"],
    ],
    col_widths=[2.2, 4.8, 4.8],
    caption="새 개념이 아니다 — 이미 만들어 쓰던 것에 '이름'을 붙였을 뿐. (Factory=생성, Strategy=교체 가능한 동작)",
    notes=(
        "새로 가르치는 게 아니라 '이름표 붙이기'. 학생이 만든 코드가 곧 교과서 패턴이었음을 보여 준다.\n"
        "Factory: 5주차 from_wire / 4주차 make_message — '무엇을 만들까'를 한곳에서 결정.\n"
        "Strategy: 5주차 Codec(평문→AES 로 실제 교체함), 7~8주차 RoomRepository(메모리↔파일) — 동작을 부품으로 빼서 갈아끼움.\n"
        "둘 다 '주입(DI)'으로 밖에서 꽂는다는 점이 공통. 다른 언어(Java 등)에서도 같은 이름으로 만난다고 짚어 주면 좋다."
    ),
)

# ── 11. 직접 해보기 ──────────────────────────────────────
d.bullets(
    "직접 해보기",
    [
        "새 명령 직접 추가하기 — 예: /me (행동 표현), /clear",
        ("command.py 표에 한 줄 + 메서드 하나만 추가해 보기", 1),
        "/w 를 '현재 방 안에서만' 가능하도록 제한해 보기",
        "ConnectionManager 에 '전체 접속자 수' 보여주는 /count 추가",
        "(생각) 명령이 100개가 되어도 이 구조가 견딜까? 왜?",
    ],
    notes=(
        "직접 명령을 추가하며 '한 곳 수정'의 가벼움을 손으로 느끼게 한다.\n"
        "마지막 생각거리로 '표 기반 분리'의 확장성을 스스로 정리하게 한다.\n"
        "최종(12주) 발표의 '나만의 기능 1개'와 연결."
    ),
)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "Week08_서버리팩터링.pptx")
d.save(out)
print("저장 완료:", out)
print("슬라이드 수:", len(d.prs.slides._sldIdLst))
