"""
Week 6 - interfaces.py  :  '계약(인터페이스)' 정하기
------------------------------------------------------------
인터페이스 = "이런 메서드를 가진 부품이면 무엇이든 OK"라는 약속.
파이썬에서는 abc(추상 베이스 클래스)로 표현한다.

핵심 계약 3가지:
  - Codec        : 메시지 ↔ 바이트 (5주차의 그 부품)
  - MessageStore : 메시지를 어딘가에 저장
  - Transport    : 한 연결로 바이트를 보낸다

서버 핵심(ChatServer)은 '이 계약을 지키는 부품'이면
진짜든 가짜든 가리지 않고 받아서 쓴다. → 교체·테스트가 쉬워진다.
"""

from abc import ABC, abstractmethod


class Codec(ABC):
    """메시지 ↔ 전송용 바이트 변환 부품."""

    @abstractmethod
    def encode(self, message):
        """메시지 -> bytes (한 줄, 끝에 \\n)."""

    @abstractmethod
    def decode(self, line):
        """한 줄(문자열) -> 메시지."""


class MessageStore(ABC):
    """메시지를 저장하는 부품 (메모리·파일·DB 무엇이든)."""

    @abstractmethod
    def save(self, message):
        """메시지 하나를 저장."""

    @abstractmethod
    def all(self):
        """저장된 메시지 전체를 리스트로."""


class Transport(ABC):
    """하나의 연결(클라이언트)로 바이트를 보내는 부품."""

    @abstractmethod
    def send(self, data):
        """bytes 를 이 연결로 보낸다."""
