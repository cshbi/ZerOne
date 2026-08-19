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
  · PlainCodec    : 메시지 ↔ 평문 바이트            (교육용 — 이제 안 씀)
  · SecretCodec   : 메시지 ↔ XOR+base64            (교육용 — '진짜 보안 아님' 예시)
  · AesGcmCodec   : 메시지 ↔ AES-256-GCM 암호문     ★ 지금 실제로 쓰는 것
'무엇으로 바꾸느냐'만 다를 뿐, 전부 encode/decode 한 쌍이다.
→ 새 암호화를 '클래스 하나 추가'로 끼웠다 = 5주차에 배운 Strategy(부품 교체)의 실전.
------------------------------------------------------------
그리고 이 코덱들은 interfaces.Codec '계약'을 지키는 부품이다.
계약(encode/decode)만 지키면 서버·클라이언트가 무엇이든 받아 쓴다.

※ AES 는 파이썬 표준 라이브러리에 없어서 외부 패키지가 필요합니다:
    pip install cryptography
"""

import os
import base64
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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


# ============================================================
# 진짜 암호화: AES-256-GCM  (실무에서 쓰는 방식)
# ============================================================
# 서버와 클라이언트가 '같은 암호(passphrase)'를 알아야 서로 통한다.
# 이 문자열을 SHA-256 으로 돌리면 항상 32바이트(=256비트) 열쇠가 나온다.
SECRET_PASSPHRASE = "우리반-공용-비밀열쇠-2026"


def _derive_key(passphrase):
    """암호 문자열 -> 32바이트 AES-256 열쇠."""
    return hashlib.sha256(passphrase.encode("utf-8")).digest()


class AesGcmCodec(Codec):
    """AES-256-GCM: 암호화(기밀성) + 변조 감지(무결성)를 함께 준다.

    XOR 과 달리 '진짜' 암호다:
      · GCM 모드라 암호문에 인증 태그가 붙어, 중간에서 한 글자만 바꿔도 decode 가 거부한다.
      · nonce(1회용 난수)를 매 메시지마다 새로 써서, 같은 내용도 매번 다른 암호문이 된다.
    다만 이것도 '완전한' 보안은 아니다: 양쪽이 열쇠(passphrase)를 미리 나눠 가져야 하고
    (키 교환 없음), 상대가 진짜 서버인지 확인하지 못한다(서버 인증 없음).
    그 둘까지 해주는 것이 TLS(HTTPS/WSS).
    """
    name = "암호화(AES-256-GCM)"

    def __init__(self, passphrase=SECRET_PASSPHRASE):
        self.key = _derive_key(passphrase)

    def encode(self, message):
        aes = AESGCM(self.key)
        nonce = os.urandom(12)                      # 매번 새 1회용 난수 (재사용 금지!)
        wire = message.to_wire().encode("utf-8")
        ciphertext = aes.encrypt(nonce, wire, None)  # 암호문 + 무결성 태그(자동 포함)
        packed = base64.b64encode(nonce + ciphertext).decode("ascii")  # nonce 를 앞에 붙여 함께 전송
        return (packed + "\n").encode("utf-8")

    def decode(self, line):
        raw = base64.b64decode(line)
        nonce, ciphertext = raw[:12], raw[12:]       # 앞 12바이트가 nonce
        aes = AESGCM(self.key)
        wire = aes.decrypt(nonce, ciphertext, None)  # 태그가 안 맞으면(변조/열쇠 불일치) 예외
        return Message.from_wire(wire.decode("utf-8"))
