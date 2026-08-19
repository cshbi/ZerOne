"""
Week 7 - room.py  :  방을 '객체'로 묶는다
------------------------------------------------------------
6주차에는 방 정보가 전역 딕셔너리 세 군데(rooms/nicknames/where)에
흩어져 있었습니다. 입장·퇴장마다 그 세 곳을 다 맞춰야 했죠.

이제 'Room' 객체 하나가 자기 일을 스스로 책임집니다(캡슐화):
  - 이름(name), 멤버(members), 대화 기록(history)을 자기가 가진다
  - join / leave / post 동작을 스스로 한다

Room 은 소켓도, Codec 도 모릅니다. '보내는 방법(send)'은 밖에서 받습니다.
(그래서 테스트하기도, 다른 전송으로 바꾸기도 쉽다)
"""


class Room:
    def __init__(self, name):
        self.name = name
        self.members = {}     # conn -> nickname  (이 방에 누가 있나)
        self.history = []     # 이 방의 대화 기록 (Message 리스트)

    def join(self, conn, nickname):
        self.members[conn] = nickname

    def leave(self, conn):
        return self.members.pop(conn, None)

    def member_names(self):
        return list(self.members.values())

    def is_empty(self):
        return not self.members

    def deliver(self, message, send):
        """이 방 멤버에게만 보낸다 (기록은 안 함). send(conn, message) 는 밖에서 주입."""
        for conn in list(self.members):
            send(conn, message)

    def post(self, message, send):
        """대화 메시지: 기록에 남기고 멤버에게 보낸다."""
        self.history.append(message)
        self.deliver(message, send)


# ------------------------------------------------------------
# [실습/과제 힌트] 방 최대 인원 제한
#   def __init__(self, name, capacity=None):
#       ...; self.capacity = capacity
#   def is_full(self):
#       return self.capacity is not None and len(self.members) >= self.capacity
# join 전에 is_full() 을 확인하면 된다.
# ------------------------------------------------------------
