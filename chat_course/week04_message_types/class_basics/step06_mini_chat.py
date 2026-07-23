"""
클래스 기초 Step 6 — 미니 채팅 메시지: 배운 것을 전부 조립한다
------------------------------------------------------------
Step 1~5 에서 배운 것만으로 week04 의 핵심을 미리 만들어 봅니다.
소켓(네트워크)은 아직 없습니다. "서버에서 이런 줄들이 왔다고 치자"로 연습합니다.

등장하는 개념 복습:
  클래스(1) · self/__init__(2) · 상속(3) · 오버라이딩/다형성(4) · classmethod(5)
"""


# ────────────────────────────────────────────
# 1. 공통 약속: 모든 메시지의 부모
# ────────────────────────────────────────────
class Message:
    def __init__(self, sender):
        self.sender = sender

    def display(self):
        # 부모는 "모든 메시지는 display 를 갖는다"는 '약속'만 남긴다.
        # 실제 내용은 자식이 각자 채운다. (채우지 않고 쓰면 에러로 알려줌)
        raise NotImplementedError("자식 클래스가 display() 를 직접 만들어야 합니다")


# ────────────────────────────────────────────
# 2. 종류별 메시지: 상속 + 오버라이딩
# ────────────────────────────────────────────
class TextMessage(Message):
    def __init__(self, sender, text):
        super().__init__(sender)
        self.text = text

    def display(self):
        return f"{self.sender}: {self.text}"

    @classmethod
    def parse(cls, sender, body):        # "철수", "안녕" → TextMessage 객체
        return cls(sender, body)


class EmojiMessage(Message):
    EMOJI = {"smile": "😄", "heart": "❤️", "cry": "😢"}

    def __init__(self, sender, name):
        super().__init__(sender)
        self.name = name

    def display(self):
        face = self.EMOJI.get(self.name, "❓")
        return f"{self.sender}: {face}"

    @classmethod
    def parse(cls, sender, body):
        return cls(sender, body)


# ────────────────────────────────────────────
# 3. 해석은 '단 한 곳'에서: 한 줄 → 알맞은 객체
# ────────────────────────────────────────────
def from_wire(line):
    """'TEXT|철수|안녕' 같은 한 줄을 알맞은 메시지 객체로 바꾼다."""
    tag, sender, body = line.split("|", 2)
    if tag == "TEXT":
        return TextMessage.parse(sender, body)
    elif tag == "EMOJI":
        return EmojiMessage.parse(sender, body)
    else:
        return TextMessage(sender, f"(알 수 없는 메시지: {line})")


# ────────────────────────────────────────────
# 4. 다형성의 순간: 받는 쪽은 종류를 묻지 않는다
# ────────────────────────────────────────────
received_lines = [                       # 서버에서 이런 줄들이 왔다고 치자
    "TEXT|철수|얘들아 안녕!",
    "EMOJI|영희|smile",
    "TEXT|민수|과제 다 했어?",
    "EMOJI|철수|cry",
]

print("=== 미니 채팅 화면 ===")
for line in received_lines:
    msg = from_wire(line)      # ① 한 줄 → 객체 (해석은 여기 한 곳)
    print(msg.display())       # ② 종류가 뭐든 display() 한 줄 (다형성!)

# for 문 안의 두 줄은 텍스트인지 이모티콘인지 전혀 묻지 않습니다.
# Step 4 의 p.ring() 과 완전히 같은 패턴입니다.


# ────────────────────────────────────────────
# 5. week04 와의 차이 (예고)
# ────────────────────────────────────────────
# 위 from_wire 안에는 아직 if/elif 가 '한 곳' 남아 있습니다.
# 종류가 늘면 여기 한 곳은 고쳐야 하죠.
# week04 의 messages.py 는 이 마지막 if/elif 마저 '등록표(registry)'로
# 없애 버립니다. 그 원리를 지금 미리 봅시다.


# ────────────────────────────────────────────
# 6. 등록표(registry) 맛보기 — 마지막 if/elif 마저 없애기
# ────────────────────────────────────────────
# 원리는 간단합니다: '꼬리표 → 클래스' 딕셔너리를 하나 만들어 두면,
# if/elif 로 묻는 대신 딕셔너리에서 '찾으면' 됩니다.

REGISTRY = {"TEXT": TextMessage, "EMOJI": EmojiMessage}    # 등록표


def from_wire2(line):
    tag, sender, body = line.split("|", 2)
    msg_class = REGISTRY.get(tag)          # ① 꼬리표로 클래스를 '찾아서'
    if msg_class is None:                  #    (등록표에 없으면 대비책)
        return TextMessage(sender, f"(알 수 없는 메시지: {line})")
    return msg_class.parse(sender, body)   # ② 그 클래스에게 만들게 시킨다


print("\n=== 등록표 버전: if/elif 가 사라졌다 ===")
for line in received_lines:
    print(from_wire2(line).display())

# 이제 새 종류를 추가할 때 고칠 곳은? 클래스 하나 만들고,
# REGISTRY 에 한 줄 등록 — from_wire2 는 안 건드립니다!
#
# week04 의 messages.py 는 그 '등록 한 줄'마저 깜빡하지 않도록
# 클래스 머리 위에 @register 를 붙여 자동으로 등록합니다.
# 그 @ 한 줄의 정체는 다음 스텝(step06b)에서 완전히 해부합니다.

# ┌──────────────────────────────────────────────────────┐
# │ 이 프로그램 한 줄 요약:                                    │
# │ 해석(객체 만들기)은 한 곳에 모으고,                   │
# │ 그 뒤로는 종류를 묻지 않고 display() 만 부른다.       │
# └──────────────────────────────────────────────────────┘

# [직접 해보기]
# 1. received_lines 에 "EMOJI|영희|heart" 를 추가해 실행해 보세요.
# 2. display() 를 오버라이딩하지 않은 새 자식 클래스를 만들어 display() 를
#    불러 보세요. 부모의 NotImplementedError 가 어떻게 도와주나요?
