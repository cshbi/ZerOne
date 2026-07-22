"""
message.py - 메시지 종류별 클래스 (다형성 리팩터링)
------------------------------------------------------------
기존에는 if/elif 로 종류(TEXT/FILE/LOC)를 분기했지만,
이제는 "종류마다 클래스"를 만들고 공통 부모(Message)를 통해
동일한 방식으로 다룬다 (다형성 = 부모 타입으로 자식들을 통일해서 다룸).

새로운 메시지 종류(예: 이모티콘)를 추가하고 싶으면
if/elif 를 서버·클라이언트 곳곳에서 고칠 필요 없이
Message 를 상속하는 클래스 하나만 새로 만들면 된다.
(맨 아래 EmojiMessage 예시 참고)
------------------------------------------------------------
"""

import base64
import os


class Message:
    """모든 메시지 종류의 부모(추상) 클래스."""

    type_tag = None            # 자식 클래스가 반드시 채움 (예: "TEXT")
    broadcast_exclude_sender = False   # 서버가 뿌릴 때 보낸 사람을 뺄지 여부
    _registry = {}              # {"TEXT": TextMessage, "FILE": FileMessage, ...}

    def __init_subclass__(cls, **kwargs):
        """자식 클래스가 정의될 때 자동으로 registry 에 등록됨."""
        super().__init_subclass__(**kwargs)
        if cls.type_tag:
            Message._registry[cls.type_tag] = cls

    # ---------- 클라이언트 -> 서버 방향 ----------
    @classmethod
    def parse_from_client(cls, line):
        """클라이언트가 보낸 한 줄을 알맞은 메시지 객체로 변환."""
        tag = line.split("|", 1)[0]
        msg_cls = cls._registry.get(tag)
        return msg_cls.from_client_line(line) if msg_cls else None

    @classmethod
    def from_client_line(cls, line):
        """예: 'TEXT|안녕' -> TextMessage 인스턴스. 자식이 오버라이딩."""
        raise NotImplementedError

    def to_client_line(self):
        """클라이언트가 서버로 보낼 때의 한 줄 (닉네임 없음). 자식이 오버라이딩."""
        raise NotImplementedError

    # ---------- 서버 -> 클라이언트 방향 ----------
    def to_broadcast_line(self, sender):
        """서버가 클라이언트들에게 뿌릴 때의 한 줄 (닉네임 포함). 자식이 오버라이딩."""
        raise NotImplementedError

    @classmethod
    def parse_from_server(cls, line):
        tag = line.split("|", 1)[0]
        msg_cls = cls._registry.get(tag)
        return msg_cls.from_server_line(line) if msg_cls else None

    @classmethod
    def from_server_line(cls, line):
        raise NotImplementedError

    # ---------- 클라이언트 화면 표시 ----------
    def display(self):
        """클라이언트가 받은 메시지를 어떻게 보여줄지. 자식이 오버라이딩."""
        raise NotImplementedError

    # ---------- 서버 쪽 검증 (선택적으로 오버라이딩) ----------
    def validate(self):
        """문제 있으면 에러 메시지(str) 반환, 문제 없으면 None."""
        return None


# =====================================================================
# TEXT
# =====================================================================
class TextMessage(Message):
    type_tag = "TEXT"

    def __init__(self, text, sender=None):
        self.text = text
        self.sender = sender

    @classmethod
    def from_client_line(cls, line):
        _, text = line.split("|", 1)
        return cls(text)

    def to_client_line(self):
        return f"TEXT|{self.text}"

    def to_broadcast_line(self, sender):
        return f"TEXT|{sender}|{self.text}"

    @classmethod
    def from_server_line(cls, line):
        _, sender, text = line.split("|", 2)
        return cls(text, sender)

    def display(self):
        if self.sender == "시스템":
            print(self.text)
        else:
            print(f"{self.sender}: {self.text}")


# =====================================================================
# FILE
# =====================================================================
class FileMessage(Message):
    type_tag = "FILE"
    broadcast_exclude_sender = True   # 파일은 보낸 사람이 로컬에서 이미 확인 -> 자기 자신은 제외
    MAX_BYTES = 5 * 1024 * 1024
    DOWNLOAD_DIR = "downloads"

    def __init__(self, filename, b64, sender=None):
        self.filename = filename
        self.b64 = b64
        self.sender = sender

    @classmethod
    def from_client_line(cls, line):
        _, filename, b64 = line.split("|", 2)
        return cls(filename, b64)

    def to_client_line(self):
        return f"FILE|{self.filename}|{self.b64}"

    def to_broadcast_line(self, sender):
        return f"FILE|{sender}|{self.filename}|{self.b64}"

    @classmethod
    def from_server_line(cls, line):
        _, sender, filename, b64 = line.split("|", 3)
        return cls(filename, b64, sender)

    @classmethod
    def from_path(cls, path):
        """/file <경로> 입력을 처리할 때 쓰는 헬퍼. (파일 크기도 같이 반환)"""
        with open(path, "rb") as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode("ascii")
        filename = os.path.basename(path)
        return cls(filename, b64), len(raw)

    def validate(self):
        approx = len(self.b64) * 3 // 4
        if approx > self.MAX_BYTES:
            return "파일이 너무 큽니다(5MB 제한)"
        return None

    def display(self):
        data = base64.b64decode(self.b64)
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)
        save_as = os.path.join(self.DOWNLOAD_DIR, f"{self.sender}_{self.filename}")
        if os.path.exists(save_as):
            name, ext = os.path.splitext(f"{self.sender}_{self.filename}")
            n = 1
            while True:
                try_path = os.path.join(self.DOWNLOAD_DIR, f"{name}_{n}{ext}")
                if not os.path.exists(try_path):
                    save_as = try_path
                    break
                n += 1
        with open(save_as, "wb") as f:
            f.write(data)
        print(f"📎 [{self.sender}]님이 파일을 보냈습니다 → 저장: {save_as} ({len(data)} bytes)")


# =====================================================================
# LOC (위치)
# =====================================================================
class LocMessage(Message):
    type_tag = "LOC"

    def __init__(self, lat, lon, sender=None):
        self.lat = lat
        self.lon = lon
        self.sender = sender

    @classmethod
    def from_client_line(cls, line):
        _, lat, lon = line.split("|", 2)
        return cls(lat, lon)

    def to_client_line(self):
        return f"LOC|{self.lat}|{self.lon}"

    def to_broadcast_line(self, sender):
        return f"LOC|{sender}|{self.lat}|{self.lon}"

    @classmethod
    def from_server_line(cls, line):
        _, sender, lat, lon = line.split("|", 3)
        return cls(lat, lon, sender)

    def display(self):
        print(f"{self.sender}님이 위치를 공유했습니다.: 위도:{self.lat} 경도:{self.lon}")


# =====================================================================
# 새 종류 추가 예시: 이모티콘
# 표에 있던 "이모티콘 - ? - ? - ?" 를 이런 식으로 채우면 됨.
# 서버/클라이언트 코드는 한 글자도 안 고쳐도 자동으로 동작함!
# =====================================================================
class EmojiMessage(Message):
    type_tag = "EMOJI"

    def __init__(self, emoji_code, sender=None):
        self.emoji_code = emoji_code   # 예: "😀" 나 "smile" 같은 코드
        self.sender = sender

    @classmethod
    def from_client_line(cls, line):
        _, emoji_code = line.split("|", 1)
        return cls(emoji_code)

    def to_client_line(self):
        return f"EMOJI|{self.emoji_code}"

    def to_broadcast_line(self, sender):
        return f"EMOJI|{sender}|{self.emoji_code}"

    @classmethod
    def from_server_line(cls, line):
        _, sender, emoji_code = line.split("|", 2)
        return cls(emoji_code, sender)

    def display(self):
        print(f"{self.sender}님이 이모티콘을 보냈습니다: {self.emoji_code}")