"""
Week 4 - 메시지 '종류'를 객체로 (messages.py)
------------------------------------------------------------
3주차의 고통: 종류(TEXT/FILE)가 늘 때마다 보내기·받기·서버의
            if/elif 를 전부 찾아 고쳐야 했다.

이번 주 해결: 각 종류를 '클래스'로 만든다.
  - 공통 약속(메서드): to_wire() 전송용 문자열,  display() 화면 표시
  - 종류가 달라도 같은 방식으로 부른다  →  이것이 '다형성'

비유: 리모컨의 '재생' 버튼 하나로 TV·에어컨·선풍기를 다룬다.
     누르는 쪽은 똑같이 누르지만, 각 기기는 자기 방식대로 반응한다.

핵심: 받은 줄을 알맞은 객체로 바꿔주는 곳(from_wire)은 '단 한 군데'.
     그 뒤로는 어떤 종류든 msg.display() 한 줄로 끝난다. (if/elif 사라짐)
"""

import base64
import os

# 꼬리표(tag) -> 클래스   :  if/elif 대신 '등록표(registry)'
_REGISTRY = {}


def register(cls):
    """클래스를 종류 등록표에 올린다 (데코레이터)."""
    _REGISTRY[cls.tag] = cls
    return cls


class Message:
    """모든 메시지의 공통 기반. '약속(공통 메서드)'만 정의한다."""
    tag = None        # 전송 꼬리표 (TEXT, EMOJI, FILE, SYS)
    kind = "메시지"    # 사람이 읽는 종류 이름 (서버 로그용)

    def __init__(self, sender=""):
        self.sender = sender

    def to_wire(self):
        """전송용 한 줄 문자열로 만든다. 종류마다 다르게 구현."""
        raise NotImplementedError

    def display(self):
        """화면에 보일 문자열을 돌려준다. 종류마다 다르게 구현."""
        raise NotImplementedError

    # ── [받는 쪽 팩토리] 받은 줄 -> 알맞은 메시지 객체 (해석기는 '단 한 곳') ──
    # 팩토리(factory): 재료(line)를 넣으면 알맞은 '제품 객체'를 찍어낸다.
    # 여기선 꼬리표가 '기계가 만든' 규격(TEXT|·EMOJI|)이라, if/elif 대신
    # 등록표(_REGISTRY)에서 '찾아서' 그 클래스에게 만들게 시킨다.
    #   (보내는 쪽 팩토리는 client.py 의 make_message — 사람 입력을 다뤄서 성격이 다름)
    @staticmethod
    def from_wire(line):
        tag, rest = line.split("|", 1)     # "TEXT|철수|안녕" -> tag="TEXT", rest="철수|안녕"
        cls = _REGISTRY.get(tag)           # 꼬리표로 '어느 클래스인지' 등록표에서 찾기
        if cls is None:                    # 등록표에 없는 종류면 (대비책)
            return UnknownMessage(line)
        return cls.parse(rest)             # 찾은 클래스에게 "네가 만들어" (아래 parse)

    @classmethod
    def parse(cls, rest):
        """[팩토리 메서드] 꼬리표 뒤(rest)를 받아 그 종류의 객체로. 종류마다 구현.
        from_wire 가 '어느 클래스인지'를 고르면, 실제 재료 손질·생성은 각 parse 가 맡는다."""
        raise NotImplementedError


@register
class TextMessage(Message):
    tag = "TEXT"
    kind = "텍스트"

    def __init__(self, text, sender=""):
        super().__init__(sender)
        self.text = text

    def to_wire(self):
        return f"TEXT|{self.sender}|{self.text}"

    def display(self):
        return f"{self.sender}: {self.text}"

    @classmethod
    def parse(cls, rest):
        sender, text = rest.split("|", 1)
        return cls(text, sender)


EMOJI = {"smile": "😄", "heart": "❤️", "thumbsup": "👍", "cry": "😢", "wow": "😮"}


@register
class EmojiMessage(Message):
    tag = "EMOJI"
    kind = "이모티콘"

    def __init__(self, name, sender=""):
        super().__init__(sender)
        self.name = name

    def to_wire(self):
        return f"EMOJI|{self.sender}|{self.name}"

    def display(self):
        face = EMOJI.get(self.name, "❓")
        return f"{self.sender}: {face}  (:{self.name}:)"

    @classmethod
    def parse(cls, rest):
        sender, name = rest.split("|", 1)
        return cls(name, sender)


@register
class FileMessage(Message):
    tag = "FILE"
    kind = "파일"
    DOWNLOAD_DIR = "downloads"

    def __init__(self, filename, b64, sender=""):
        super().__init__(sender)
        self.filename = filename
        self.b64 = b64

    def to_wire(self):
        return f"FILE|{self.sender}|{self.filename}|{self.b64}"

    def display(self):
        # 파일은 '표시'할 때 저장까지 책임진다 (자기 일은 자기가)
        data = base64.b64decode(self.b64)
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)
        path = os.path.join(self.DOWNLOAD_DIR, f"{self.sender}_{self.filename}")
        with open(path, "wb") as f:
            f.write(data)
        return f"📎 [{self.sender}]님이 파일을 보냈습니다 → 저장: {path} ({len(data)} bytes)"

    @classmethod
    def parse(cls, rest):
        sender, filename, b64 = rest.split("|", 2)
        return cls(filename, b64, sender)

    @classmethod
    def from_path(cls, path, sender=""):
        """[팩토리 메서드] 파일 '경로로부터' FileMessage 를 만든다 (보내는 쪽이 사용).
        정문 __init__ 은 이미 만든 b64 를 받지만, 이 문은 '경로'라는 다른 재료에서
        시작해 파일을 읽고 base64 로 바꾼 뒤 객체를 찍어낸다. (4주차 step05 의 그 패턴)"""
        with open(path, "rb") as f:                          # 경로의 파일을 열어
            raw = f.read()                                   # 바이트로 읽고
        b64 = base64.b64encode(raw).decode("ascii")          # 전송용 base64 문자열로 바꿔
        return cls(os.path.basename(path), b64, sender)      # 그 재료로 객체 생성


@register
class SystemMessage(Message):
    tag = "SYS"
    kind = "시스템"

    def __init__(self, text, sender="시스템"):
        super().__init__(sender)
        self.text = text

    def to_wire(self):
        return f"SYS|{self.sender}|{self.text}"

    def display(self):
        return self.text          # 입퇴장 알림 등은 그대로 출력

    @classmethod
    def parse(cls, rest):
        sender, text = rest.split("|", 1)
        return cls(text, sender)


class UnknownMessage(Message):
    """등록표에 없는 종류가 와도 프로그램이 죽지 않게."""
    kind = "알수없음"

    def __init__(self, raw):
        super().__init__("")
        self.raw = raw

    def to_wire(self):
        return self.raw

    def display(self):
        return f"[알 수 없는 메시지] {self.raw[:30]}"


# ------------------------------------------------------------
# [실습/과제 힌트] 위치 공유를 추가해 보세요.
# 아래 클래스 하나만 추가하면 끝납니다. 서버도 클라이언트도 안 고칩니다!
#
# @register
# class LocationMessage(Message):
#     tag = "LOC"; kind = "위치"
#     def __init__(self, lat, lon, sender=""):
#         super().__init__(sender); self.lat = lat; self.lon = lon
#     def to_wire(self):
#         return f"LOC|{self.sender}|{self.lat}|{self.lon}"
#     def display(self):
#         return f"{self.sender}: 📍 위치 ({self.lat}, {self.lon})"
#     @classmethod
#     def parse(cls, rest):
#         sender, lat, lon = rest.split("|", 2)
#         return cls(lat, lon, sender)
# ------------------------------------------------------------
