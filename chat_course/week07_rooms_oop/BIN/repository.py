"""
Week 7 - repository.py  :  방을 어디에 저장할지 (DI)
------------------------------------------------------------
방을 메모리에 둘지·파일에 둘지·DB에 둘지는 '교체 가능한 부품'입니다.
5주차 DI 를 그대로 재사용합니다: 계약(RoomRepository)을 정하고,
서버는 어떤 저장소든 '주입'받아 씁니다.

  - InMemoryRoomRepository : 메모리에만. 서버 끄면 사라진다.
  - FileRoomRepository     : 파일(JSON)에. 껐다 켜도 방이 남는다.
"""

import json
from abc import ABC, abstractmethod

from room import Room
from messages import Message


class RoomRepository(ABC):
    """방의 생성·조회·저장을 담당하는 부품의 계약."""

    @abstractmethod
    def create(self, name):
        """새 방을 만들어 저장하고 돌려준다."""

    @abstractmethod
    def find(self, name):
        """이름으로 방을 찾는다 (없으면 None)."""

    @abstractmethod
    def save(self, room):
        """변경된 방을 저장한다."""

    @abstractmethod
    def all(self):
        """모든 방을 리스트로."""


class InMemoryRoomRepository(RoomRepository):
    """메모리에만 보관. 가볍지만 서버를 끄면 사라진다."""

    def __init__(self):
        self._rooms = {}

    def create(self, name):
        room = Room(name)
        self._rooms[name] = room
        return room

    def find(self, name):
        return self._rooms.get(name)

    def save(self, room):
        self._rooms[room.name] = room

    def all(self):
        return list(self._rooms.values())


class FileRoomRepository(RoomRepository):
    """파일(JSON)에 방 이름과 대화 기록을 남긴다. 재시작해도 방이 살아 있다."""

    def __init__(self, path="rooms.json"):
        self.path = path
        self._rooms = {}
        self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        for name, wires in data.items():
            room = Room(name)
            room.history = [Message.from_wire(w) for w in wires]   # 기록 복원
            self._rooms[name] = room          # 멤버는 비어 있음(접속은 휘발성)

    def _persist(self):
        data = {name: [m.to_wire() for m in room.history]
                for name, room in self._rooms.items()}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create(self, name):
        room = Room(name)
        self._rooms[name] = room
        self._persist()
        return room

    def find(self, name):
        return self._rooms.get(name)

    def save(self, room):
        self._rooms[room.name] = room
        self._persist()

    def all(self):
        return list(self._rooms.values())
