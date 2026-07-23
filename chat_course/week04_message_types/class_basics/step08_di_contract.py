"""
클래스 기초 Step 8 — DI 완성: '약속'을 코드로 못박는다 (계약)
------------------------------------------------------------
Step 7 에서 부품(벨소리)을 밖에서 꽂았습니다. 그런데 한 가지 찜찜함이 남았죠.

    "부품이 갖출 조건은 play 메서드가 있을 것" — 그 약속, 어디에 적혀 있지?

지금까지 약속은 우리 머릿속에만 있었습니다. 오늘은 그 약속을
Ringtone 이라는 '부모 클래스'로 코드에 못박습니다.

  - Ringtone 은 실제로 울 줄 모릅니다. "울 줄 알아야 한다(play)"는 약속만 남깁니다.
  - 모든 벨소리 부품은 Ringtone 을 상속받아 play 를 자기 방식대로 채웁니다.
  - 어디서 본 구조죠? Step 6 의 Message → TextMessage/EmojiMessage 와 똑같습니다!

이렇게 '약속만 있는 부모'를 흔히 인터페이스(계약)라고 부릅니다.
(파이썬은 약속을 더 엄격하게 강제하는 도구(abc)도 있지만, 그건 나중에 Codec 과
 함께 배웁니다. 오늘은 "약속을 코드로 보이게 만들었다"까지면 충분합니다.)
"""


# ────────────────────────────────────────────
# 1. 약속(계약): 벨소리 부품이라면 play 를 갖춰야 한다
# ────────────────────────────────────────────
class Ringtone:
    """모든 벨소리 부품의 공통 약속. 내용은 없고 '약속'만 있다."""

    def play(self, owner):
        # 자식이 play 를 안 만들고 쓰면 이 에러가 대신 알려준다.
        # (Step 6 의 Message.display() 와 같은 장치)
        raise NotImplementedError("자식 클래스가 play() 를 직접 만들어야 합니다")


# ────────────────────────────────────────────
# 2. 부품들: 약속(Ringtone)을 상속받아 각자 방식으로 채운다
# ────────────────────────────────────────────
class Marimba(Ringtone):
    def play(self, owner):                     # 오버라이딩 (Step 4)
        print(f"[{owner}의 폰] 띠리링~ 마림바 🎵")


class Bell(Ringtone):
    def play(self, owner):
        print(f"[{owner}의 폰] 따르릉 따르릉 ☎️")


class Vibration(Ringtone):
    def play(self, owner):
        print(f"[{owner}의 폰] (무음) 지이잉- 📳")


# ────────────────────────────────────────────
# 3. 본체: Step 7 과 완전히 같다 — 약속을 만들어도 본체는 안 바뀐다!
# ────────────────────────────────────────────
class Phone:
    # ── Phone 핵심 (Step 7 그대로: 벨소리를 밖에서 받는다) ──
    def __init__(self, owner, number, ringtone):   # ringtone 자리에는
        self.owner = owner                         # 'Ringtone 약속을 지킨 부품'이 꽂힌다
        self.number = number
        self.power = False
        self.ringtone = ringtone

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


print("=== 약속을 지킨 부품이라면 무엇이든 꽂힌다 ===")
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
# 4. 정리: 약속을 '클래스로' 적어 두면 뭐가 좋아지나?
# ────────────────────────────────────────────
# ① 약속이 보인다      : "벨소리 부품 만들려면? Ringtone 을 상속받아 play 를
#                        채우면 되는구나" — 코드만 보고도 규격을 안다.
# ② 실수를 잡아 준다   : play 를 깜빡한 부품은 NotImplementedError 가
#                        "무엇을 안 했는지"까지 짚어 준다. (③번 실험!)
# ③ 본체는 그대로      : Step 7 의 Phone 과 비교해 보세요. 한 글자도 안 바뀜.
#                        약속은 '부품 쪽' 규격이지 본체의 일이 아니다.
#
# 이것이 6주차에 배울 인터페이스(계약)의 정신입니다:
#   "이런 메서드를 가진 부품이면 무엇이든 OK" 라는 약속을 코드로 남기는 것.
#
# 미리 보기: 우리 채팅도 곧 이렇게 조립됩니다.
#   ChatServer(codec=PlainCodec())     # 평문 부품을 꽂으면 평문 채팅
#   ChatServer(codec=SecretCodec())    # 암호화 부품을 꽂으면 암호화 채팅
#   → Codec 이 바로 Ringtone 같은 '약속 클래스'입니다.

# ┌────────────────────────────────────────────────────┐
# │ 이 프로그램 한 줄 요약:                                  │
# │ 부품의 약속(play)을 부모 클래스(Ringtone)로 못박고, │
# │ 부품들은 약속을 상속받아 각자 방식으로 채운다.      │
# │ 본체(Phone)는 약속만 믿고 부른다 — 이게 계약이다.   │
# └────────────────────────────────────────────────────┘

# [직접 해보기]
# 1. 새 벨소리 부품(예: Song — "노래가 흘러나온다")을 Ringtone 상속으로
#    만들어 꽂아 보세요. Phone 클래스는 한 글자도 고치지 않아야 합니다!
# 2. 일부러 play 를 안 만든 부품(class Broken(Ringtone): pass)을 꽂고
#    ring() 을 불러 보세요. 어떤 에러 메시지가 여러분을 도와주나요?
# 3. (비교) Ringtone 을 상속받지 않았지만 play 는 있는 부품도 꽂아 보세요.
#    울리나요? → 울립니다! 파이썬에서 약속 클래스는 '강제'가 아니라
#    '안내판'입니다. 강제하는 도구(abc)는 6주차에서 만납니다.
