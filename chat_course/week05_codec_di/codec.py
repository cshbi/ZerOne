"""
Week 5(통합) - codec.py  :  변환(직렬화·암호화)을 '부품'으로
============================================================
'Codec' 이라는 이름, 어디서 들어봤죠? (동영상 코덱, 오디오 코덱…)
------------------------------------------------------------
Codec = COder + DECoder  (코더 + 디코더)
  - encode(부호화): 보낼 것을 '전송용 형태'로 바꾼다
  - decode(복호화): 받은 것을 '원래 형태'로 되돌린다
  → 이 encode/decode '한 쌍'을 묶은 부품이 코덱이다.

우리가 이미 아는 코덱들:
  · 동영상 코덱(H.264 등): 보낼 땐 압축(encode), 볼 땐 복원(decode)
    "코덱이 없어서 영상이 안 열려요" = decode 할 부품이 없다는 뜻!
  · 오디오 코덱(MP3, AAC): 소리를 작게 담고(encode) 재생 때 되살린다(decode)
  · 1주차의 문자열 .encode()/.decode()(UTF-8)도 사실 '글자 코덱'이었다.

우리 채팅의 코덱도 똑같은 일을 한다:
  · PlainCodec  : 메시지 ↔ 평문 바이트
  · SecretCodec : 메시지 ↔ 암호화 바이트 (XOR + base64)
'무엇으로 바꾸느냐'만 다를 뿐, 전부 encode/decode 한 쌍이다.
------------------------------------------------------------
그리고 이 코덱들은 interfaces.Codec '계약'을 지키는 부품이다.
계약(encode/decode)만 지키면 ChatServer 가 무엇이든 받아 쓴다.
"""

import base64

from interfaces import Codec
from messages import Message


class PlainCodec(Codec):
    name = "평문"

    def encode(self, message):
        return (message.to_wire() + "\n").encode("utf-8")

    def decode(self, line):
        return Message.from_wire(line)


SECRET_KEY = 42   # 교육용. 진짜 보안 아님!


def _xor(data, key):
    return bytes(b ^ key for b in data)


class SecretCodec(Codec):
    name = "암호화(XOR)"

    def __init__(self, key=SECRET_KEY):
        self.key = key

    def encode(self, message):
        scrambled = _xor(message.to_wire().encode("utf-8"), self.key)
        return (base64.b64encode(scrambled).decode("ascii") + "\n").encode("utf-8")

    def decode(self, line):
        raw = _xor(base64.b64decode(line), self.key)
        return Message.from_wire(raw.decode("utf-8"))
