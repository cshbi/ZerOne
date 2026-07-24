# -*- coding: utf-8 -*-
"""
Week 5(통합) 강의자료(PPT) 생성 스크립트
실행:  python make_ppt.py   →   Week05_부품과계약_Codec_DI.pptx

원칙: 소스를 함께 열어 놓고 보는 발표용.
     설명(왜 이렇게 했나)을 발표자 노트가 아니라 '슬라이드 본문'에 담아,
     슬라이드만 봐도 생각이 읽히도록 한다.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ppt_theme import Deck

KICKER = "파이썬으로 만드는 실시간 채팅 프로그램"

d = Deck()

# ── 1. 표지 ────────────────────────────────────────────────
d.title(
    kicker=KICKER,
    title="부품과 계약: 갈아끼우는 채팅",
    subtitle="Codec · 의존성 주입(DI), 그리고 평문 탈취 데모 — 소스를 함께 읽으며",
)

# ── 2. 도입 질문 ──────────────────────────────────────────
d.big_question(
    question="내 메시지, 중간에서 그대로 보이는 거 아냐?\n그리고 — 부품을 왜 굳이 '밖에서' 끼울까?",
    hint="4주차에 Phone(ringtone) 으로 이미 맛봤죠. 오늘은 진짜 채팅에 적용합니다.",
)

# ── 3. 이번 주 소스 지도 ──────────────────────────────────
d.bullets(
    "오늘 열어 둘 소스와 읽는 순서",
    [
        "messages.py — 메시지 객체 (4주차 그대로, 안 바뀜)",
        "codec.py — 변환 부품: 평문 ↔ 암호화  ★ 오늘 새것",
        "interfaces.py — 계약(abc): 부품이 지켜야 할 약속",
        "server.py — ChatServer 두뇌(부품을 주입받음) + 조립부",
        "client.py — 같은 Codec 을 끼운 클라이언트",
        "sniffer.py — 평문 탈취 데모 (중간자)",
        "demo_fake_parts.py — 가짜 부품으로 네트워크 없이 확인",
        ("읽는 순서: messages → codec → interfaces → server(두뇌→조립) → 나머지", 1),
        ("이유: '데이터 → 부품 → 계약 → 조립' 순서로 보면 큰 그림이 먼저 잡힌다", 1),
    ],
)

# ── 4. 평문 탈취 데모 (실제 캡처) ─────────────────────────
d.terminals(
    "먼저 충격 — 평문은 그대로 털린다 (sniffer.py)",
    [
        ("평문(PlainCodec) 일 때",
         "😱 [탈취 성공] 클라 → 서버\n"
         "   TEXT|철수|비밀번호는 1234야\n"
         "\n"
         "→ 접속했을 뿐인데\n"
         "  대화가 그대로 보인다"),
        ("암호화(SecretCodec) 로 바꾸면",
         "🔒 [탈취 실패] 클라 → 서버\n"
         "   fm9yflbGmIrGorJWwZOu...\n"
         "\n"
         "→ 같은 도청자인데\n"
         "  이제 못 읽는다"),
    ],
)

# ── 5. Codec 개념 + 어원 ──────────────────────────────────
d.bullets(
    "그래서 필요한 것: 변환을 '부품'으로 — Codec",
    [
        "Codec = COder + DECoder (부호화 encode + 복호화 decode 한 쌍)",
        ("동영상·오디오 코덱의 그 코덱 — \"코덱 없어서 영상이 안 열려요\" = decode 할 부품이 없다", 1),
        ("1주차의 .encode()/.decode()(UTF-8)도 사실 '글자 코덱'이었다", 1),
        "변환을 부품으로 떼어내면 → 평문 ↔ 암호화가 '부품 교체' 한 줄",
        "왜 부품으로? 암호화를 send() 안에 박아 넣으면 끄지도·바꾸지도 못한다",
        ("박아 넣기 = 4주차 StuckPhone 의 병. 분리 = 그 처방", 1),
    ],
)

# ── 6. codec.py 읽는 법 ───────────────────────────────────
d.code(
    "codec.py — 둘 다 encode/decode 라는 '같은 약속'",
    "class PlainCodec(Codec):          # 평문 부품\n"
    "    def encode(self, message):\n"
    "        return (message.to_wire() + \"\\n\").encode()\n"
    "    def decode(self, line):\n"
    "        return Message.from_wire(line)\n"
    "\n"
    "class SecretCodec(Codec):         # 암호화 부품 (모양이 똑같다!)\n"
    "    def encode(self, message):\n"
    "        scrambled = xor(message.to_wire().encode(), key)  # 뒤섞고\n"
    "        return base64.b64encode(scrambled) + b\"\\n\"        # 줄에 안전하게\n"
    "    def decode(self, line):\n"
    "        raw = xor(base64.b64decode(line), key)             # 거꾸로\n"
    "        return Message.from_wire(raw.decode())",
    caption="모양(encode/decode)이 같아서 서로 '갈아끼울 수 있다'. 이게 부품의 조건이다.",
)

# ── 7. 계약(abc) 승격 ─────────────────────────────────────
d.code(
    "interfaces.py — 약속을 코드로 '강제'하기 (abc)",
    "from abc import ABC, abstractmethod\n"
    "\n"
    "class Codec(ABC):\n"
    "    @abstractmethod\n"
    "    def encode(self, message): ...   # \"부품이라면 이건 꼭 있어야 해\"\n"
    "    @abstractmethod\n"
    "    def decode(self, line): ...\n"
    "\n"
    "# 4주차 Ringtone = '안내판'(안 지켜도 돌아감)\n"
    "# 이제 abc     = '강제'  — encode 를 빼먹은 부품은\n"
    "#                아예 만들어지지도 않는다(에러로 막음)",
    caption="4주차 step08 의 Ringtone(약속)이 여기서 abc(지키지 않으면 에러)로 승격된다.",
)

# ── 8. DI: 왜 밖에서 끼우나 ────────────────────────────────
d.bullets(
    "핵심 질문: 부품을 왜 '밖에서' 끼우나 (DI)",
    [
        "ChatServer(codec, store) — 두뇌가 부품을 '직접 만들지' 않고 받는다",
        ("4주차 Phone(owner, number, ringtone) 과 완전히 같은 구조", 1),
        "이점 1) 교체 — 평문↔암호화, 메모리↔파일 저장을 바꿔도 두뇌는 그대로",
        "이점 2) 확인 — 가짜 부품을 꽂으면 네트워크 없이 두뇌를 시험",
        "이점 3) 분업 — 부품마다 따로 만들 수 있다",
        "그래서 두뇌(ChatServer)는 '소켓을 모르게' 설계했다",
        ("소켓을 알면 테스트할 때마다 진짜 네트워크가 필요해지니까", 1),
    ],
)

# ── 9. server.py 읽는 법 ──────────────────────────────────
d.code(
    "server.py — 두뇌는 소켓을 모른다 (읽는 법)",
    "class ChatServer:                 # ← 두뇌: 소켓을 모른다\n"
    "    def __init__(self, codec, store):\n"
    "        self.codec = codec        # 밖에서 받은 부품\n"
    "        self.store = store        # 밖에서 받은 부품\n"
    "    def on_line(self, transport, line):\n"
    "        msg = self.codec.decode(line)   # 부품에게 맡김\n"
    "        self.store.save(msg)            # 부품에게 맡김\n"
    "        self._broadcast(msg)\n"
    "\n"
    "def build_server():               # ← 조립부: 여기서만 부품을 '결정'\n"
    "    codec = SecretCodec() if USE_SECRET else PlainCodec()\n"
    "    store = InMemoryStore()       # FileStore(...) 로 바꿔 끼우면 파일 저장\n"
    "    return ChatServer(codec, store)",
    caption="읽는 법: 두뇌(무엇을 하나)와 조립부(무엇을 끼우나)를 나눠서 본다. 소켓은 main 이 담당.",
)

# ── 10. 가짜 부품으로 확인 (실제 데모 출력) ───────────────
d.terminals(
    "가짜 부품으로 확인 — 소켓 없이 (demo_fake_parts.py)",
    [
        ("데모: 부품 교체 (평문→암호화)",
         "영희에게 나간 줄:\n"
         "  fm9yflbBhZbGorJWwZOu...\n"
         "'비밀' 이 보이나? → 아니오 ✅\n"
         "풀어보면: 비밀\n"
         "\n"
         "※ ChatServer 는 한 줄도\n"
         "  안 바꿨다. codec 만 교체!"),
        ("데모: 저장 실패해도 채팅은 계속",
         "[경고] 저장 실패:\n"
         "  디스크가 꽉 찼습니다\n"
         "영희는 받았나? → 예 ✅\n"
         "\n"
         "→ 저장(부품)이 망가져도\n"
         "  채팅(두뇌)은 멀쩡\n"
         "= 책임이 나뉘어 있다"),
    ],
)

# ── 11. 소스 읽는 순서 정리 ───────────────────────────────
d.bullets(
    "정리 — 소스를 이 눈으로 읽으면 된다",
    [
        "① messages.py : 무엇을 주고받나 (데이터)",
        "② codec.py : 그걸 어떻게 바꾸나 (부품) — encode/decode 한 쌍",
        "③ interfaces.py : 부품이 지킬 약속 (계약/abc)",
        "④ server.py : 두뇌(로직) + 조립부(부품 결정)를 나눠 본다",
        "⑤ sniffer / demo : 왜 이렇게 했는지 '증명'하는 데모",
        ("한 문장: 박아 넣지 말고 '부품 + 계약 + 조립'으로 나눴다", 1),
        ("그래서 바꿀 땐 부품만, 확인할 땐 가짜만 꽂으면 된다", 1),
    ],
)

# ── 12. 깨달음 ────────────────────────────────────────────
d.takeaway(
    headline="박아 넣지 말고 분리하면,\n부품만 갈아끼우면 된다.",
    points=[
        "Codec 교체로 평문 ↔ 암호화 (두뇌는 그대로)",
        "계약(abc)이 '갈아끼울 수 있음'을 보장한다",
        "두뇌는 소켓을 몰라서 → 가짜 부품으로 네트워크 없이 확인",
        "이 XOR 암호는 개념용 — 진짜 보안은 TLS(HTTPS/WSS)",
    ],
)

# ── 13. 직접 해보기 ──────────────────────────────────────
d.bullets(
    "직접 해보기",
    [
        "SecretCodec 의 변환 규칙(열쇠·방식)을 바꿔 나만의 버전 만들기",
        "\"왜 이건 진짜 보안이 아닌가\" 한 줄로 적어 오기 (힌트: sniffer 의 SHOW_CRACK)",
        "FileStore 를 주입해 재시작 후에도 기록이 남는지 확인",
        "demo_fake_parts 에 '저장 실패' 외 다른 가짜 부품 상황 추가해 보기",
        ("(생각) 서버와 클라이언트의 Codec 이 다르면 어떻게 될까?", 1),
    ],
)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "Week05_부품과계약_Codec_DI.pptx")
d.save(out)
print("저장 완료:", out)
print("슬라이드 수:", len(d.prs.slides._sldIdLst))
