"""
클래스 기초 Step 6b — @register 완전 해부: 폰 대리점 카탈로그
------------------------------------------------------------
week04 messages.py 에 남은 마지막 수수께끼:

    @register
    class TextMessage(Message): ...

이 @ 한 줄을 '폰 대리점' 이야기로 완전히 해부합니다.

  상황: 대리점에 손님이 주문서를 냅니다 → "IPHONE|철수|010-1111-1111"
        직원은 카탈로그(등록표)에서 기종을 찾아 개통해 줍니다.
        신제품이 출시되면? 카탈로그에 자동으로 올라갑니다. ← 이게 @register!

비밀은 딱 두 가지뿐입니다.
  비밀 1: 클래스도 '값'이다 — 변수에 담고, 딕셔너리에 넣고, 함수에 넘길 수 있다.
  비밀 2: @함수 는 "바로 아래 것을 그 함수에 넣었다 빼라"는 줄임 표기다.
"""


class Phone:
    # ── Phone 핵심 (Step 1 그대로) ──────────────
    tag = None                        # 기종 코드 (클래스 변수, Step 2b) — 자식이 채운다

    def __init__(self, owner, number):
        self.owner = owner
        self.number = number
        self.power = False

    def power_on(self):
        self.power = True
        print(f"[{self.owner}의 폰] 전원 ON")

    def call(self, to):
        if not self.power:
            print(f"[{self.owner}의 폰] 전원이 꺼져 있어요!")
            return
        print(f"[{self.owner}의 폰] {to} 에게 전화 📞")

    # ── 오늘의 재료: Step 4 의 그 벨소리 ────────
    def ring(self):
        print(f"[{self.owner}의 폰] 따르릉 따르릉 ☎️")


class IPhone(Phone):                  # Step 3~4 에서 만든 그 자식들!
    tag = "IPHONE"

    def ring(self):
        print(f"[{self.owner}의 아이폰] 띠리링~ 마림바 🎵")


class GPhone(Phone):
    tag = "GPHONE"

    def ring(self):
        print(f"[{self.owner}의 갤럭시] Over the Horizon~ 🎶")


# ────────────────────────────────────────────
# 1. 비밀 1: 클래스도 '값'이다
# ────────────────────────────────────────────
print("=== 비밀 1: 클래스도 값이다 ===")
print(IPhone)                         # 클래스 '자체'를 출력할 수 있다 (<class ...>)

box = IPhone                          # 변수에 담을 수 있다! (괄호 없음 = 호출 아님)
p = box("철수", "010-1111-1111")      # 담은 것으로 객체도 만들 수 있다
p.ring()

d = {"IPHONE": IPhone}                # 딕셔너리의 '값'으로도 넣을 수 있다
p2 = d["IPHONE"]("영희", "010-2222-2222")   # 꺼내서 바로 객체 만들기
p2.ring()

# IPhone 이라는 이름은 사실 '클래스가 담긴 변수'였던 겁니다.
# 값이니까 → 담고, 넣고, 넘길 수 있다. 카탈로그(등록표)의 전부가 이것입니다.


# ────────────────────────────────────────────
# 2. 그러니 함수에 클래스를 '넘길' 수도 있다 — register 는 보통 함수
# ────────────────────────────────────────────
REGISTRY = {}                         # 대리점 카탈로그: 기종코드 → 클래스


def register(phone_class):            # 클래스를 받아서
    print(f"   [카탈로그 등록] {phone_class.tag}")
    REGISTRY[phone_class.tag] = phone_class   # 카탈로그에 올리고
    return phone_class                # ★ 받은 그대로 돌려준다 (이유는 4번에서!)


print("\n=== 보통 함수 호출로 등록해 보기 ===")
register(IPhone)                      # 숫자 넘기듯 클래스를 넘겼다
print("카탈로그:", REGISTRY)


# ────────────────────────────────────────────
# 3. 정의하자마자 등록하기 — 그런데 귀찮다
# ────────────────────────────────────────────
print("\n=== 정의 직후 등록 (수동) ===")
GPhone = register(GPhone)             # 출시하자마자 카탈로그에 올리고 다시 담아 둔다

# 동작은 완벽합니다. 그런데 신제품을 만들 때마다 이 한 줄을 써야 하고,
# 무엇보다 '깜빡하기' 쉽습니다. 깜빡하면? 카탈로그에 없어서 주문을 못 받습니다.


# ────────────────────────────────────────────
# 4. 비밀 2: @ 는 방금 그 한 줄의 '줄임 표기'다
# ────────────────────────────────────────────
print("\n=== @register: 같은 일의 줄임 표기 ===")


@register                             # ← "아래 클래스를 register 에 넣었다 빼라"
class FoldPhone(Phone):               #    즉  FoldPhone = register(FoldPhone)
    tag = "FOLD"                      #    과 완전히 같은 뜻!

    def ring(self):
        print(f"[{self.owner}의 폴더폰] (접힌 채로) 웅웅- 📳")


print("카탈로그:", REGISTRY)

# ★ 방금 실행 결과를 보세요: FoldPhone 을 '정의(출시)하는 순간'
#   [카탈로그 등록] FOLD 가 찍혔습니다. 우리가 부르지 않아도,
#   파이썬이 클래스 정의를 읽자마자 register 를 실행한 것입니다.
#   → 그래서 messages.py 는 import 만 해도 모든 종류가 자동 등록됩니다.
#
# 그런데 register 가 왜 phone_class 를 return 할까요?
# @ 는 '넣었다 빼기' 즉  FoldPhone = register(FoldPhone) 이므로,
# register 가 아무것도 안 돌려주면  FoldPhone = None 이 되어
# 클래스가 통째로 사라져 버립니다! ([직접 해보기] 2번에서 확인)


# ────────────────────────────────────────────
# 5. 완성: 주문서 한 줄 → 개통 (직원은 기종을 몰라도 된다)
# ────────────────────────────────────────────
def from_order(line):
    """'IPHONE|철수|010-1111-1111' 주문서 한 줄 → 알맞은 폰 개통."""
    tag, owner, number = line.split("|")
    phone_class = REGISTRY.get(tag)       # 카탈로그에서 기종을 찾아서
    if phone_class is None:
        print(f"[대리점] 죄송합니다, 없는 기종입니다: {tag}")
        return None
    return phone_class(owner, number)     # 그 클래스로 개통!


print("\n=== 대리점 개점: 주문서를 처리하자 ===")
orders = [
    "IPHONE|철수|010-1111-1111",
    "GPHONE|영희|010-2222-2222",
    "FOLD|민수|010-3333-3333",
]
for line in orders:
    phone = from_order(line)
    phone.ring()                     # 개통 확인 벨 — Step 4 의 다형성!

# from_order 안에 if/elif 가 없습니다. 직원(from_order)은 기종을 모릅니다.
# 카탈로그가 찾아 주고, 울리는 건 각 기종이 알아서 합니다.


# 신제품 출시도 즉석에서 시연해 봅시다. from_order 는 안 건드립니다!
@register
class RetroPhone(Phone):              # Step 4 [직접 해보기]의 그 옛날 폰!
    tag = "RETRO"

    def ring(self):
        print(f"[{self.owner}의 옛날폰] 벨~~~ 벨~~~ 🔔")


print("\n=== 신제품 출시: @register 한 줄이면 끝 ===")
from_order("RETRO|할머니|010-9999-9999").ring()


# ────────────────────────────────────────────
# 6. week04 와 짝짓기 — 이름만 다르고 완전히 같다
# ────────────────────────────────────────────
# ┌───────────────────────┬─────────────────────────────┐
# │ 오늘 (폰 대리점)       │ week04 (messages.py)        │
# ├───────────────────────┼─────────────────────────────┤
# │ 주문서 "IPHONE|철수|…" │ 전송 줄 "TEXT|철수|안녕"    │
# │ REGISTRY (카탈로그)    │ _REGISTRY (밑줄 = 만지지 마 │
# │                       │  시오 표시, Step 2b 의 그것) │
# │ @register (출시)       │ @register                   │
# │ tag = "IPHONE"        │ tag = "TEXT"  (클래스 변수) │
# │ from_order(line)      │ Message.from_wire(line)     │
# │ phone.ring()          │ msg.display()               │
# └───────────────────────┴─────────────────────────────┘
# 차이 하나: messages.py 는 phone_class(owner, number) 대신 cls.parse(rest) 를
# 부릅니다 — 종류마다 재료 손질이 달라서요 (Step 5 의 @classmethod parse).

# ┌──────────────────────────────────────────────────────┐
# │ 이 프로그램 한 줄 요약:                                    │
# │ 클래스도 값이라 카탈로그(딕셔너리)에 올릴 수 있고,    │
# │ @register 는 "출시하자마자 카탈로그에 넣었다 빼기".   │
# │ 그래서 직원(from_order)은 기종을 몰라도 개통한다.     │
# └──────────────────────────────────────────────────────┘

# [직접 해보기]
# 1. 신기종을 하나 출시해 보세요 (예: tag="GAME" 게임폰, ring 은 게임 소리).
#    from_order 와 주문 처리 for 문은 한 글자도 고치지 않아야 합니다.
# 2. (실험) register 의 return phone_class 줄을 지우고 실행해 보세요.
#    어디서, 왜 문제가 생기나요? (힌트: print(FoldPhone) 을 찍으면 None)
# 3. week04 의 messages.py 를 열어 @register 와 _REGISTRY 를 찾아
#    밑줄을 긋고, 위 6번 표의 어느 칸과 짝인지 적어 보세요.
