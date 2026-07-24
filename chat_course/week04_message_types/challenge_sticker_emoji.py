"""
[도전 과제] 이모지를 '스티커 파일'로 — 진짜 카톡처럼
============================================================
지금 EmojiMessage 는 이름(smile)을 유니코드 글자(😄)로 바꿔 보여 줍니다.
그런데 실제 카카오톡 이모티콘·스티커는 유니코드가 아니라 '이미지 파일'입니다.

이 과제에서는 이모지를 '파일'로 다루는 StickerMessage 를 만듭니다.
(터미널은 그림을 못 그리니, 이미지 대신 stickers/ 폴더의 '아스키 아트 텍스트
 파일'을 스티커로 씁니다. 원리는 이미지 파일과 똑같습니다.)

────────────────────────────────────────────────────────────
설계 결정: 파일을 어떻게 주고받을까?  (수업에서 이미 둘 다 봤습니다)
  방식 A. 파일을 '매번 실어' 보낸다   → FileMessage (base64 로 통째 전송)
  방식 B. '이름만' 보내고 받는 쪽이    → 이번 과제! 카톡 스티커 방식
          자기 폴더에서 파일을 찾는다     (스티커 팩을 한 번 받아두면 이후엔 이름만)

  이번엔 방식 B 로 만듭니다. 그래서 네트워크로 오가는 건 여전히 'smile' 이라는
  '이름' 뿐 — 지금 EmojiMessage 와 전송 방식은 똑같고, '표시(display)'만 파일을
  읽도록 바뀝니다. (핵심: 종류를 바꿔도 to_wire 는 그대로, display 만 달라진다)
────────────────────────────────────────────────────────────

이 파일은 지금도 실행됩니다. TODO 를 채우기 전에는 스티커가 '미완성'으로만
표시되고, 다 채우면 stickers/ 폴더의 아스키 아트가 화면에 뜹니다.
"""

import os


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


class StickerMessage(Message):
    STICKER_DIR = "stickers"          # 스티커 파일들이 있는 로컬 폴더 (내 컴퓨터에 있음)

    def __init__(self, sender, name):
        super().__init__(sender)
        self.name = name              # 전송되는 건 이 '이름' 뿐 (예: "smile")

    def display(self):
        # TODO(1): STICKER_DIR 폴더에서 self.name + ".txt" 파일을 찾으세요.
        #          (힌트: os.path.join(self.STICKER_DIR, self.name + ".txt"))
        # TODO(2): 그 파일이 있으면(os.path.exists) 열어서 내용을 읽고,
        #          "철수 님의 스티커:\n<아스키 아트>" 형태로 return 하세요.
        #          (힌트: with open(path, encoding="utf-8") as f: art = f.read().rstrip("\n"))
        # TODO(3): 파일이 없으면 "철수: [스티커 없음: 이름]" 을 return 하세요.
        #          ← EMOJI.get(name, "❓") 의 '❓' 와 같은 대비책입니다!
        #
        # 아래는 '미완성' 임시 표시입니다. 위 TODO 를 채우면 지우세요.
        return f"{self.sender}: [스티커 미완성 - {self.name}]"

    @classmethod
    def parse(cls, sender, body):
        return cls(sender, body)


def from_wire(line):
    """받은 한 줄 -> 알맞은 메시지 객체 (받는 쪽 팩토리)."""
    tag, sender, body = line.split("|", 2)
    if tag == "TEXT":
        return TextMessage.parse(sender, body)
    elif tag == "STICKER":
        return StickerMessage.parse(sender, body)
    return TextMessage(sender, f"(알 수 없는 메시지: {line})")


# ────────────────────────────────────────────
# 실행 코드 (여기는 고치지 마세요!)
#   ※ stickers/ 폴더가 있는 곳에서 실행해야 스티커를 찾습니다.
#     week04_message_types/ 안에서:  python challenge_sticker_emoji.py
# ────────────────────────────────────────────
if __name__ == "__main__":
    received_lines = [
        "TEXT|철수|스티커 보낼게~",
        "STICKER|철수|smile",
        "STICKER|영희|heart",
        "STICKER|민수|kimchi",     # stickers/ 에 kimchi.txt 는 없다 → 대비책 확인용
    ]
    for line in received_lines:
        print(from_wire(line).display())


# ────────────────────────────────────────────
# [기대 출력] — TODO 를 다 채우면 이렇게 나옵니다
# ────────────────────────────────────────────
# 철수: 스티커 보낼게~
# 철수 님의 스티커:
#  \(^_^)/
#   smile!
# 영희 님의 스티커:
#  <3 <3
#   love
# 민수: [스티커 없음: kimchi]

# [생각해 보기 — 답을 주석으로 적어 제출]
# Q1. 네트워크로 실제 오간 건 무엇인가요? 그림 파일 전체인가요, 이름뿐인가요?
#     방식 A(FileMessage 처럼 매번 전송)와 비교해 무엇이 더 효율적인가요?
# Q2. 그런데 방식 B 는 '받는 쪽에 그 스티커 파일이 이미 있어야' 합니다.
#     처음 스티커 팩은 어떻게 받아야 할까요? (힌트: 그때는 방식 A 를 쓴다)
# Q3. to_wire(전송 형식)는 EmojiMessage 와 똑같은데 display 만 바꿨습니다.
#     '종류를 바꿔도 전송은 그대로, 표시만 다르다' — 이게 왜 좋은가요?
# Q4. (심화) 10주차 tkinter 나 11주차 웹에서는 이 display 가 어떻게 달라질까요?
#     같은 StickerMessage 인데 터미널/앱/웹에서 다르게 보이려면?

# [도전 확장 — 원하는 학생]
#  · 나만의 스티커 .txt 를 stickers/ 에 추가하고 STICKER 로 보내 보기
#  · 스티커가 없을 때 서버에 자동 요청해 받아오는 흐름을 '설계만' 글로 적어 보기
