"""
클래스 기초 Step 1 — 왜 클래스를 쓰는가?
------------------------------------------------------------
클래스 문법을 배우기 전에, "클래스가 없으면 뭐가 불편한지"부터 겪어봅니다.

전화기 1대를 프로그램으로 표현한다고 해봅시다.
전화기에는 '데이터'(주인, 번호, 전원상태)와 '동작'(전원켜기, 전화걸기)이 있습니다.
"""

# ────────────────────────────────────────────
# 방법 1. 변수를 따로따로 만든다
# ────────────────────────────────────────────
phone1_owner = "철수"
phone1_number = "010-1111-1111"
phone1_power = False

phone2_owner = "영희"
phone2_number = "010-2222-2222"
phone2_power = False

# 문제: 전화기가 10대면? 변수가 30개!
#       "철수의 전원상태"가 어느 변수인지 이름으로만 구분해야 한다.


# ────────────────────────────────────────────
# 방법 2. 딕셔너리 + 함수
# ────────────────────────────────────────────
def make_phone(owner, number):
    return {"owner": owner, "number": number, "power": False}


def power_on(phone):
    phone["power"] = True
    print(f"[{phone['owner']}의 폰] 전원 ON")


def call(phone, to):
    if not phone["power"]:
        print(f"[{phone['owner']}의 폰] 전원이 꺼져 있어요!")
        return
    print(f"[{phone['owner']}의 폰] {to} 에게 전화 📞")


print("=== 방법 2: 딕셔너리 + 함수 ===")
chulsu = make_phone("철수", "010-1111-1111")
power_on(chulsu)
call(chulsu, "010-2222-2222")

# 돌아는 간다. 그런데…
# 문제 1: 데이터(chulsu)와 동작(power_on, call)이 남남이다.
#         call(학생성적표, ...) 처럼 엉뚱한 걸 넣어도 파이썬은 막지 못한다.
# 문제 2: phone["poweer"] 처럼 키 오타를 내도 실행 전엔 모른다.
# 문제 3: 전화기 관련 함수가 100개가 되면, 어떤 함수가 전화기용인지 찾기 어렵다.


# ────────────────────────────────────────────
# 방법 3. 클래스 — 데이터와 동작을 '한 덩어리'로
# ────────────────────────────────────────────
class Phone:
    def __init__(self, owner, number):
        self.owner = owner            # 주인            ┐
        self.number = number          # 전화번호        │ 데이터 (속성)
        self.power = False            # 전원 상태       ┘

    def power_on(self):               # 동작 (메서드)
        self.power = True
        print(f"[{self.owner}의 폰] 전원 ON")

    def call(self, to):
        if not self.power:
            print(f"[{self.owner}의 폰] 전원이 꺼져 있어요!")
            return
        print(f"[{self.owner}의 폰] {to} 에게 전화 📞")


print("\n=== 방법 3: 클래스 ===")
chulsu = Phone("철수", "010-1111-1111")
chulsu.power_on()
chulsu.call("010-2222-2222")

# 달라진 점을 잘 보세요. 출력은 방법 2와 완전히 같습니다. 구조만 바뀌었습니다.
#   power_on(chulsu)      →  chulsu.power_on()
#   call(chulsu, "...")   →  chulsu.call("...")
# "누가(chulsu) 무엇을(power_on) 한다" 가 문장처럼 읽힙니다.
# 전화기의 데이터와 동작이 Phone 이라는 한 덩어리 안에 다 모여 있습니다.

# ★ 중요: 방금 만든 이 Phone —
#   데이터 3개(owner, number, power) + 동작 2개(power_on, call) —
#   가 앞으로 '모든 스텝의 출발점'입니다.
#   다음 스텝부터는 늘 이 폰으로 시작해서, 그날의 개념 하나씩만 얹습니다.

# ┌─────────────────────────────────────────┐
# │ 이 프로그램 한 줄 요약:                       │
# │ 클래스 = 데이터 + 그 데이터를 다루는 동작 │
# │ 을 한 덩어리로 묶은 것                   │
# └─────────────────────────────────────────┘

# [직접 해보기]
# 1. Phone 에 power_off(전원 끄기) 메서드를 추가해 보세요.
# 2. 전원을 켜지 않은 채 call() 을 호출해 보세요. 무슨 일이 일어나나요?
