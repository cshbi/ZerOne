"""
[과제 2] 음성 메시지 추가하기 (도전 과제)
------------------------------------------------------------
step06 의 미니 채팅에 '음성 메시지' 종류를 새로 추가합니다.

목표 전송 형식:  "VOICE|보낸사람|길이(초)"
목표 화면 표시:  철수: 🎤 음성 메시지 (7초)

이 파일은 지금도 실행됩니다. 실행해 보면 마지막 줄이
"(알 수 없는 메시지: ...)" 로 나올 겁니다.
여러분이 VoiceMessage 를 완성하면 그 줄이 제대로 표시됩니다.
"""


class Message:
    def __init__(self, sender):
        self.sender = sender

    def display(self):
        raise NotImplementedError("자식 클래스가 display() 를 직접 만들어야 합니다")


class TextMessage(Message):
    def __init__(self, sender, text):
        super().__init__(sender)
        self.text = text

    def display(self):
        return f"{self.sender}: {self.text}"

    @classmethod
    def parse(cls, sender, body):
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
# TODO(1): 여기에 VoiceMessage 클래스를 만드세요.
#   - Message 를 상속받는다
#   - __init__(self, sender, seconds) : 부모 준비(super) + self.seconds 저장
#   - display(self) : "철수: 🎤 음성 메시지 (7초)" 형태의 문자열을 return
#   - parse(cls, sender, body) 클래스메서드 : body 가 "7" 같은 문자열로 온다
#   (막히면 위의 EmojiMessage 를 그대로 보고 흉내 내세요. 그게 정상입니다!)
# ────────────────────────────────────────────


def from_wire(line):
    tag, sender, body = line.split("|", 2)
    if tag == "TEXT":
        return TextMessage.parse(sender, body)
    elif tag == "EMOJI":
        return EmojiMessage.parse(sender, body)
    # TODO(2): VOICE 꼬리표가 오면 VoiceMessage 를 만들어 주도록
    #          elif 한 개를 추가하세요.
    else:
        return TextMessage(sender, f"(알 수 없는 메시지: {line})")


# ────────────────────────────────────────────
# 실행 코드 (여기는 고치지 마세요!)
# ────────────────────────────────────────────
if __name__ == "__main__":
    received_lines = [
        "TEXT|철수|어제 노래방 갔다왔어",
        "EMOJI|영희|smile",
        "VOICE|철수|7",
    ]
    for line in received_lines:
        msg = from_wire(line)
        print(msg.display())


# [기대 출력]
# 철수: 어제 노래방 갔다왔어
# 영희: 😄
# 철수: 🎤 음성 메시지 (7초)

# [생각해 보기 — 답을 주석으로 적어 제출]
# Q1. 새 종류를 추가하면서 고친 곳은 몇 군데였나요? (클래스 추가 제외)
# Q2. week04 의 messages.py 는 '등록표(registry)' 덕분에 from_wire 의
#     elif 조차 안 고칩니다. 수업 후 messages.py 에서 그 장치(@register)를
#     찾아 밑줄을 그어 오세요.
