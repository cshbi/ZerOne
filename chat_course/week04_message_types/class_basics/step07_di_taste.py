"""
클래스 기초 Step 7 — (맛보기) 부품은 밖에서 만들어 끼운다: DI
------------------------------------------------------------
※ 이 스텝은 '맛보기'입니다. 깊은 내용(인터페이스 문서화, 테스트)은
  나중에 Codec 을 배운 다음 제대로 다룹니다. 오늘은 딱 한 가지 질문만:

      "부품을 왜 안에서 만들지 않고, 밖에서 만들어 넣어 줄까?"

새로 배울 문법은 없습니다! Step 4 의 '공통 약속'(같은 이름의 메서드)만
그대로 씁니다. 소재도 그대로 전화기 — 이번엔 '벨소리'가 부품입니다.

비유: 게임기는 게임(카트리지)을 직접 만들지 않는다.
     꽂아 주는 대로 실행할 뿐이다. 그래서 게임기 하나로 온갖 게임을 한다.

이번에는 Phone 핵심에 '추가'가 아니라 '변경'이 일어납니다. 잘 비교해 보세요.
"""


# ────────────────────────────────────────────
# 부품들: '벨소리'  (공통 약속 = play 메서드, Step 4 에서 배운 그것!)
# ────────────────────────────────────────────
class Marimba:
    def play(self, owner):
        print(f"[{owner}의 폰] 띠리링~ 마림바 🎵")


class Bell:
    def play(self, owner):
        print(f"[{owner}의 폰] 따르릉 따르릉 ☎️")


class Vibration:
    def play(self, owner):
        print(f"[{owner}의 폰] (무음) 지이잉- 📳")


# ────────────────────────────────────────────
# 1. BEFORE: 부품을 '안에서' 직접 만들면 (박아 넣기)
# ────────────────────────────────────────────
class StuckPhone:
    # ── Phone 핵심 (Step 1 그대로) ──────────────
    def __init__(self, owner, number):
        self.owner = owner
        self.number = number
        self.power = False
        self.ringtone = Marimba()     # ← 폰이 벨소리를 '직접' 만든다 = 박아 넣기

    def power_on(self):
        self.power = True
        print(f"[{self.owner}의 폰] 전원 ON")

    def call(self, to):
        if not self.power:
            print(f"[{self.owner}의 폰] 전원이 꺼져 있어요!")
            return
        print(f"[{self.owner}의 폰] {to} 에게 전화 📞")

    def ring(self):                   # Step 4 에서 얹었던 그 벨소리
        self.ringtone.play(self.owner)


print("=== BEFORE: 안에서 직접 만들면 ===")
p = StuckPhone("철수", "010-1111-1111")
p.ring()

# 문제: 이 폰은 영원히 마림바만 울린다.
#  - 진동으로 바꾸고 싶다?  → StuckPhone 클래스를 '수술'해야 한다.
#  - 철수는 마림바, 영희는 진동?  → 클래스를 종류별로 또 만들어야 한다.
# 어디서 본 고통이죠? "바꾸려면 코드를 뜯어야 한다" — if/elif 때와 같은 병입니다.


# ────────────────────────────────────────────
# 2. AFTER: 부품을 '밖에서' 만들어 넣어 주면 (= 의존성 주입, DI)
# ────────────────────────────────────────────
class Phone:
    # ── Phone 핵심 (★ 오늘의 변경: 벨소리를 밖에서 받는다) ──
    def __init__(self, owner, number, ringtone):   # ← 재료가 하나 늘었다 (주입!)
        self.owner = owner
        self.number = number
        self.power = False
        self.ringtone = ringtone      # 직접 만들지 않고, 받아서 꽂을 뿐

    def power_on(self):
        self.power = True
        print(f"[{self.owner}의 폰] 전원 ON")

    def call(self, to):
        if not self.power:
            print(f"[{self.owner}의 폰] 전원이 꺼져 있어요!")
            return
        print(f"[{self.owner}의 폰] {to} 에게 전화 📞")

    def ring(self):
        self.ringtone.play(self.owner)     # 무엇이 꽂혔든 '약속(play)'만 부른다


print("\n=== AFTER: 밖에서 만들어 넣으면 ===")
p1 = Phone("철수", "010-1111-1111", Marimba())      # 같은 Phone 클래스인데
p2 = Phone("영희", "010-2222-2222", Vibration())    # 넣어 주는 부품만 다르다
p3 = Phone("민수", "010-3333-3333", Bell())

for p in [p1, p2, p3]:
    p.ring()                       # Step 4 의 다형성이 여기서 또 일한다!

# Phone 클래스는 한 글자도 안 바꿨는데 세 가지 폰이 됐습니다.
# 밤에는 진동으로 바꾸고 싶다면? → 부품만 갈아 끼우면 끝:
p1.ringtone = Vibration()
print("\n--- 철수가 수업에 들어와서 진동으로 변경 ---")
p1.ring()


# ────────────────────────────────────────────
# 3. 정리: 왜 '밖에서' 인가?
# ────────────────────────────────────────────
# ① 본체를 안 뜯는다   : 벨소리를 바꿔도 Phone 코드는 그대로.
# ② 조합이 자유롭다    : 같은 본체 + 다른 부품 = 다른 폰.
# ③ 나중에, 시험 가능  : 가짜 부품을 꽂으면 본체만 따로 시험할 수 있다.
#                        (이건 Codec 배운 뒤 제대로 — 지금은 ①②만 기억!)
#
# 부품이 갖출 조건은 단 하나 — '약속한 메서드(play)'가 있을 것.
# Step 4 에서 배운 공통 약속이 곧 끼움 규격(소켓 모양)인 셈입니다.
# 이 약속을 문서로 못박는 도구(인터페이스)는 나중에 배웁니다. 지금은 몰라도 됩니다.
#
# 미리 보기: 우리 채팅도 곧 이렇게 조립됩니다.
#   ChatServer(codec=PlainCodec())     # 평문 부품을 꽂으면 평문 채팅
#   ChatServer(codec=SecretCodec())    # 암호화 부품을 꽂으면 암호화 채팅

# ┌────────────────────────────────────────────────────┐
# │ 이 프로그램 한 줄 요약:                                  │
# │ 부품을 안에서 만들면 바꿀 때마다 본체를 뜯는다.     │
# │ 밖에서 만들어 넣으면(주입) 갈아 끼우기만 하면 된다. │
# └────────────────────────────────────────────────────┘

# [직접 해보기]
# 1. 새 벨소리 부품(예: Song — "노래가 흘러나온다")을 만들어 꽂아 보세요.
#    Phone 클래스는 한 글자도 고치지 않아야 합니다!
# 2. StuckPhone 에서 같은 일을 하려면 어디를 고쳐야 했을지 세어 보세요.
# 3. (생각) play 메서드가 없는 엉뚱한 부품(예: 숫자 5)을 꽂으면 언제,
#    어떤 에러가 날까요? 직접 꽂아서 확인해 보세요.
