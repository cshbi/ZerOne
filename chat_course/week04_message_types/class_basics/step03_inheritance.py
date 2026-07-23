"""
클래스 기초 Step 3 — 상속: 물려받고, 덧붙인다
------------------------------------------------------------
지난주 과제였던 Phone → IPhone / GPhone 을 함께 완성해 봅니다.

상속 = 이미 있는 클래스의 데이터와 동작을 '물려받아' 새 클래스를 만드는 것.
비유: "전화기"라는 설계도가 있으면, 아이폰 설계도는 처음부터 다시 그리지 않는다.
     전화기 설계도를 물려받고, 아이폰만의 기능(페이스타임)을 덧붙인다.

Step 1 의 Phone 그대로 시작합니다. 오늘 얹는 것: power_off, sms, 그리고 자식들.
"""


class Phone:
    # ── Phone 핵심 (Step 1 그대로) ──────────────
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

    # ── 오늘의 추가: 모든 전화기의 공통 기능 확장 ──
    def power_off(self):
        self.power = False
        print(f"[{self.owner}의 폰] 전원 OFF")

    def sms(self, to, text):
        print(f"[{self.owner}의 폰] {to} 에게 문자: \"{text}\" ✉️")


# ────────────────────────────────────────────
# 1. 자식 클래스: 물려받고 + 자기 기능을 덧붙인다
# ────────────────────────────────────────────
class IPhone(Phone):                     # 괄호 안 = 부모 클래스
    def facetime(self, to):              # 아이폰에만 있는 기능
        print(f"[{self.owner}의 아이폰] {to} 와 페이스타임 📹")


class GPhone(Phone):
    def circle_search(self, thing):      # 갤럭시에만 있는 기능
        print(f"[{self.owner}의 갤럭시] '{thing}' 서클 투 서치 🔍")


print("=== 상속: 안 만든 기능도 쓸 수 있다 ===")
iphone = IPhone("철수", "010-1111-1111")
iphone.power_on()                # IPhone 에는 power_on 이 없는데 된다! (부모 것)
iphone.call("010-2222-2222")     # 이것도 부모 것
iphone.facetime("영희")          # 이건 자기 것

gphone = GPhone("영희", "010-2222-2222")
gphone.power_on()
gphone.sms("010-1111-1111", "밥 먹었어?")
gphone.circle_search("맛집")

# IPhone 클래스 안에는 facetime 딱 하나만 썼는데,
# power_on / power_off / call / sms 가 전부 됩니다. 이게 상속의 힘.


# ────────────────────────────────────────────
# 2. 자식이 __init__ 을 새로 쓰고 싶다면? → super()
# ────────────────────────────────────────────
class SmartPhone(Phone):
    def __init__(self, owner, number, app):
        super().__init__(owner, number)  # 부모의 __init__ 을 먼저 실행 (핵심 3총사 준비)
        self.app = app                   # 그 다음 내 것을 추가

    def run_app(self):
        print(f"[{self.owner}의 폰] {self.app} 실행 🚀")


print("\n=== super(): 부모의 준비 + 나의 준비 ===")
sp = SmartPhone("민수", "010-3333-3333", "카카오톡")
sp.power_on()                            # 부모 __init__ 이 만든 power 가 잘 있다
sp.run_app()

# 주의: 자식이 __init__ 을 새로 쓰면 부모의 __init__ 은 '자동 실행되지 않는다'.
#       super().__init__(...) 을 안 부르면 self.owner 가 아예 안 만들어져서
#       power_on() 에서 AttributeError 가 난다. (주석 풀고 실험해 보세요)
# class BrokenPhone(Phone):
#     def __init__(self, owner, number, app):
#         self.app = app                 # super().__init__ 을 빼먹음!
# BrokenPhone("민수", "010-3333-3333", "게임").power_on()
#                                        # AttributeError: no attribute 'owner'

# ┌──────────────────────────────────────────────────┐
# │ 이 프로그램 한 줄 요약:                                │
# │ 상속 = 공통 기능은 부모에 한 번만, 자식은 차이만. │
# │ super().__init__() = 부모의 준비도 잊지 말 것.   │
# └──────────────────────────────────────────────────┘

# [직접 해보기]
# 1. FoldPhone(폴더블) 클래스를 만들어 fold()/unfold() 기능을 덧붙여 보세요.
# 2. IPhone 으로 sms 를 보내 보세요. 어느 클래스의 코드가 실행된 걸까요?
