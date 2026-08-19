"""
Week 8 - session.py  :  '누가 접속해 있나'를 객체로
------------------------------------------------------------
7주차까지 접속 정보(닉네임·현재 방)는 서버 여기저기의 작은 딕셔너리에
조금씩 남아 있었습니다. 이걸 두 객체로 정리합니다.

  - Session           : 접속한 한 사람 (소켓 + 닉네임 + 현재 방)
  - ConnectionManager : 모든 Session 을 모아 관리 (추가/제거/조회)

단일 책임: 각 객체는 한 가지 일만 한다.
"""
"""
ConnectionManager ── 모든 Session 관리
        │
        └─ Session.room ──→ 지금 있는 Room 을 가리킴 (없으면 None)
                                    │
                              RoomRepository ── 모든 Room 관리

"""
import threading


class Session:
    """접속한 한 사람."""
    def __init__(self, conn, nickname):
        self.conn = conn
        self.nickname = nickname
        self.room = None          # 현재 들어가 있는 Room (없으면 None)


class ConnectionManager:
    """접속(Session)들을 모아 관리한다."""
    def __init__(self):
        self._sessions = {}       # conn -> Session
        self._lock = threading.Lock()

    def add(self, conn, nickname):
        session = Session(conn, nickname)
        with self._lock:
            self._sessions[conn] = session
        return session

    def remove(self, conn):
        with self._lock:
            return self._sessions.pop(conn, None)

    def get(self, conn):
        with self._lock:
            return self._sessions.get(conn)

    def all(self):
        with self._lock:
            return list(self._sessions.values())

    def find_by_nickname(self, nickname):
        with self._lock:
            for s in self._sessions.values():
                if s.nickname == nickname:
                    return s
        return None

