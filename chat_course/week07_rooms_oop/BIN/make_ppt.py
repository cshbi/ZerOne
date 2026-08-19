# -*- coding: utf-8 -*-
"""
Week 7 강의자료(PPT) 생성 스크립트
실행:  python make_ppt.py   →   Week07_Room객체_저장소DI.pptx
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ppt_theme import Deck

KICKER = "파이썬으로 만드는 실시간 채팅 프로그램"

d = Deck()

# ── 1. 표지 ────────────────────────────────────────────────
d.title(
    kicker=KICKER,
    title="방을 객체로, 저장소는 부품으로",
    subtitle="Room 객체로 캡슐화 · RoomRepository 를 주입해 재시작에도 살아남기",
    notes=(
        "지난주: 방이 전역 딕셔너리 세 곳에 흩어져 엉켰다.\n"
        "오늘 한 줄 목표: 흩어진 상태를 Room 객체로 묶고, 저장소를 DI 로 갈아끼워 '재시작 후 방 유지'를 보여 준다.\n"
        "하이라이트: 파일 저장소로 바꾸면 서버를 껐다 켜도 방이 남는 장면."
    ),
)

# ── 2. 도입 질문 ──────────────────────────────────────────
d.big_question(
    question="방 정보를 어딘가 저장하고,\n서버를 껐다 켜도 남게 하려면?",
    hint="지난주 방은 서버를 끄면 통째로 사라졌습니다. 어떻게 남길까요?",
    notes=(
        "지난주 엉킴(전역 3개)과 '끄면 사라짐'을 떠올리게 한다.\n"
        "두 가지를 오늘 푼다: (1) 흩어진 상태 → Room 객체, (2) 휘발 → 저장소 부품 교체."
    ),
)

# ── 3. 개념: Room 객체(캡슐화) ────────────────────────────
d.bullets(
    "방을 'Room 객체'로 묶는다 (캡슐화)",
    [
        "Room 이 자기 것을 스스로 가진다: 이름 · 멤버 · 대화 기록",
        "Room 이 자기 일을 스스로 한다: join · leave · post(멤버에게만)",
        "전역 딕셔너리 세 개가 사라진다 → 상태가 한 곳에 모인다",
        "Room 은 소켓도 Codec 도 모른다 — '보내는 방법'만 밖에서 받는다",
    ],
    notes=(
        "캡슐화 = 관련된 데이터와 동작을 한 덩어리로. 지난주 흩어짐의 반대.\n"
        "Room 이 send 방법을 주입받는 점도 강조 — 5주차 DI 와 같은 패턴(테스트·교체 쉬움)."
    ),
)

# ── 4. 개념: 저장소 분리 + 합성 ───────────────────────────
d.bullets(
    "방을 어디에 저장할까 — 부품으로 분리",
    [
        "메모리에 둘지·파일에 둘지·DB에 둘지는 '교체 가능한 부품'",
        ("5주차 DI 재사용: 계약(RoomRepository)을 정하고 주입받는다", 1),
        "InMemoryRoomRepository / FileRoomRepository",
        "합성(composition): 서버가 여러 Room 을, Room 이 여러 멤버를 가진다",
    ],
    notes=(
        "저장 '방식'을 로직에서 떼어낸다 — Codec 을 떼어냈던 것과 똑같은 발상.\n"
        "합성: '~을 가진다(has-a)' 관계. 서버 has Room, Room has 멤버. 상속과 구분해 한 줄만."
    ),
)

# ── 5. code: Room 클래스 ──────────────────────────────────
d.code(
    "room.py — 방이 자기 일을 스스로",
    "class Room:\n"
    "    def __init__(self, name):\n"
    "        self.name = name\n"
    "        self.members = {}      # conn -> nickname\n"
    "        self.history = []      # 대화 기록\n"
    "\n"
    "    def join(self, conn, nickname):  self.members[conn] = nickname\n"
    "    def leave(self, conn):           return self.members.pop(conn, None)\n"
    "\n"
    "    def post(self, message, send):   # 기록 + 멤버에게 전송\n"
    "        self.history.append(message)\n"
    "        for conn in self.members:\n"
    "            send(conn, message)      # '보내는 법'은 밖에서 주입",
    caption="6주차의 흩어진 상태가 Room 안으로 모였다.",
    notes=(
        "members/history 가 Room 안에 있다 — 더 이상 전역이 아니다.\n"
        "post 가 send 를 인자로 받는 점이 핵심: Room 은 소켓을 모른 채 '보내라'고만 한다."
    ),
)

# ── 6. BEFORE/AFTER: /join ────────────────────────────────
d.code(
    "/join 비교 — 흩어짐 vs 위임",
    "# BEFORE (6주차): 전역 세 군데를 손으로 맞춤\n"
    "rooms[old].remove(conn)\n"
    "rooms[arg].append(conn)\n"
    "where[conn] = arg\n"
    "\n"
    "# AFTER (7주차): Room 에게 맡긴다\n"
    "old.leave(conn);  REPO.save(old)\n"
    "room.join(conn, nickname);  REPO.save(room)\n"
    "room_of[conn] = room",
    caption="상태 변경을 Room 이 책임지니, 서버는 '맡기기'만 한다.",
    notes=(
        "BEFORE 의 세 줄(전역 직접 수정)과 AFTER(Room 위임 + 저장)를 나란히 비교.\n"
        "퇴장 처리도 마찬가지로 Room.leave 한 번 — 6주차의 '세 군데 청소'가 사라졌다."
    ),
)

# ── 7. code: 저장소 주입 ──────────────────────────────────
d.code(
    "repository.py — 저장소를 갈아끼운다",
    "class RoomRepository(ABC):          # 계약\n"
    "    def create(self, name): ...\n"
    "    def find(self, name): ...\n"
    "    def save(self, room): ...\n"
    "    def all(self): ...\n"
    "\n"
    "# 조립: 한 줄만 바꾸면 저장 방식이 바뀐다\n"
    "REPO = InMemoryRoomRepository()      # 끄면 사라짐\n"
    "# REPO = FileRoomRepository(\"rooms.json\")  # 재시작해도 남음",
    caption="서버 코드는 그대로. 어떤 저장소를 주입하느냐만 다르다.",
    notes=(
        "InMemory ↔ File 을 조립부 한 줄로 교체하는 시연.\n"
        "FileRoomRepository 는 방 이름과 대화 기록을 JSON 으로 저장했다가 시작할 때 복원한다."
    ),
)

# ── 8. 실행 결과 (실제 캡처) ──────────────────────────────
d.terminals(
    "직접 돌려보자 — 재시작해도 방이 남는다",
    [
        ("메모리 저장소",
         "방 생성 후: ['잡담']\n"
         "\n"
         "── 서버 재시작 ──\n"
         "\n"
         "재시작 후 : []\n"
         "→ 사라짐 😢"),
        ("파일 저장소",
         "방 생성 후: ['잡담', '게임']\n"
         "\n"
         "── 서버 재시작 ──\n"
         "\n"
         "재시작 후 : ['잡담', '게임']\n"
         "→ 살아있음 🎉"),
        ("복원된 대화 기록",
         "fil.find('잡담').history\n"
         "→ ['민수: 안녕']\n"
         "\n"
         "방 이름뿐 아니라\n"
         "대화 기록까지 복원된다"),
    ],
    notes=(
        "실제로 두 저장소로 '생성 → 재시작(새 객체로 로드)'을 돌려 캡처한 결과.\n"
        "메모리는 사라지고, 파일은 방+기록이 살아남는다 — 저장소만 바꿨을 뿐 서버 로직은 동일.\n"
        "라이브로는 server.py 의 REPO 한 줄을 File 로 바꾸고 서버를 재시작해 보여 준다."
    ),
)

# ── 9. 깨달음 ─────────────────────────────────────────────
d.takeaway(
    headline="잘 설계하니, 저장·확장이 '부품 교체'로 끝난다.",
    points=[
        "흩어진 전역 상태가 Room 객체 하나로 모였다(캡슐화)",
        "입장·퇴장의 '세 군데 맞추기'가 사라졌다 — Room 에게 위임",
        "저장 방식(메모리/파일)은 주입으로 갈아끼운다",
        "다음 주: 서버가 다시 커졌다 — 책임을 객체로 나눠 정리한다",
    ],
    notes=(
        "6주차의 엉킴이 사라졌음을 대비로 보여 주며 마무리.\n"
        "DI 가 Codec(5·6주) → 저장소(8주)로 반복 적용된다는 '패턴'을 인식시킨다.\n"
        "다음 주 예고: 명령 해석·세션 관리 등으로 다시 커진 서버를 작은 객체들로 나눈다."
    ),
)

# ── 10. 직접 해보기 ──────────────────────────────────────
d.bullets(
    "직접 해보기",
    [
        "Room 에 최대 인원 제한 추가 (capacity / is_full)",
        ("힌트는 room.py 맨 아래 주석에 있습니다", 1),
        "FileRoomRepository 로 바꿔 서버를 껐다 켜며 방 유지 확인",
        "SqliteRoomRepository 골격 구현 (원하는 학생)",
        "(생각) 접속별 정보(닉네임·현재 방)도 객체로 묶으면? → 다음 주 Session",
    ],
    notes=(
        "최대 인원 제한으로 'Room 에 동작을 더하는' 경험을 시킨다(캡슐화의 이점).\n"
        "Sqlite 골격은 도전 과제. 계약(RoomRepository)만 지키면 서버는 안 바뀐다는 점을 강조.\n"
        "마지막 생각거리가 8주차 Session/ConnectionManager 의 씨앗."
    ),
)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "Week07_Room객체_저장소DI.pptx")
d.save(out)
print("저장 완료:", out)
print("슬라이드 수:", len(d.prs.slides._sldIdLst))
