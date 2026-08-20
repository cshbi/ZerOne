"""
Week 8 - command.py  :  명령을 해석하는 객체
------------------------------------------------------------
서버 본체에 흩어져 있던 if cmd == "/create" ... elif "/join" ... 를
한 객체(CommandHandler)로 모읍니다.

핵심: 명령 -> 처리함수 '표(dict)'를 둔다.
     새 명령을 추가하려면 표에 한 줄, 메서드 하나만 더하면 끝.
     (서버 본체는 건드리지 않는다)
"""

from messages import TextMessage, SystemMessage


class CommandHandler:
    def __init__(self, server):
        self.server = server
        # 명령 -> 처리 메서드 (새 명령은 여기에 한 줄 추가)
        self.table = {
            "/create": self.cmd_create,
            "/join":   self.cmd_join,
            "/leave":  self.cmd_leave,
            "/rooms":  self.cmd_rooms,
            "/who":    self.cmd_who,
            "/rename": self.cmd_rename,
            "/w":      self.cmd_whisper,
        }

    def handle(self, session, text):
        parts = text.split(" ", 1)
        cmd = parts[0]
        arg = parts[1].strip() if len(parts) > 1 else ""
        fn = self.table.get(cmd)
        if fn is None:
            self.server.send_to(session, SystemMessage(f"알 수 없는 명령: {cmd}"))
            return
        fn(session, arg)

    # ── 각 명령은 한 가지 일만 한다 ──
    def cmd_create(self, session, arg):
        if not arg:
            self.server.send_to(session, SystemMessage("방 이름을 함께 적어주세요:  /create 방이름"))
            return
        if self.server.rooms.find(arg):
            self.server.send_to(session, SystemMessage(f"이미 있는 방입니다: {arg}"))
            return
        self.server.rooms.create(arg)
        self.server.send_to(session, SystemMessage(f"방을 만들었습니다: {arg}  (/join {arg})"))

    def cmd_join(self, session, arg):
        if not arg:
            self.server.send_to(session, SystemMessage("방 이름을 함께 적어주세요:  /join 방이름"))
            return
        room = self.server.rooms.find(arg)
        if room is None:
            self.server.send_to(session, SystemMessage(f"없는 방입니다: {arg}  (/create {arg} 먼저)"))
            return
        if session.room:
            self.server.leave_room(session)
        room.join(session.conn, session.nickname)
        session.room = room
        self.server.rooms.save(room)
        # 기존 대화가 있으면 '최근 5개' 를 나에게만 먼저 보여 준다 (이어보기)
        for past in room.history[-5:]:
            self.server.send_to(session, past)
        room.deliver(SystemMessage(f"*** {session.nickname}님이 입장했습니다 ***"),
                     self.server.raw_send)

    def cmd_leave(self, session, arg):
        if session.room:
            name = session.room.name
            self.server.leave_room(session)
            self.server.send_to(session, SystemMessage(f"방에서 나왔습니다: {name}"))
        else:
            self.server.send_to(session, SystemMessage("아직 방에 없습니다."))

    def cmd_rooms(self, session, arg):
        parts = [f"{r.name}({len(r.members)}명)" for r in self.server.rooms.all()]
        self.server.send_to(session, SystemMessage("방 목록: " + (", ".join(parts) if parts else "(없음)")))

    def cmd_who(self, session, arg):
        if session.room:
            members = ", ".join(session.room.member_names())
            self.server.send_to(session, SystemMessage(f"[{session.room.name}] 멤버: {members}"))
        else:
            self.server.send_to(session, SystemMessage("아직 방에 없습니다. /join 방이름"))

    def cmd_rename(self, session, arg):
        new = arg.strip()
        if not new:
            self.server.send_to(session, SystemMessage("사용법: /rename 새닉네임"))
            return
        old = session.nickname
        session.nickname = new
        if session.room:                       # 방 멤버 목록의 이름도 갱신
            session.room.members[session.conn] = new
            session.room.deliver(SystemMessage(f"*** {old} 님이 {new} (으)로 이름을 바꿨습니다 ***"),
                                 self.server.raw_send)
        else:
            self.server.send_to(session, SystemMessage(f"이름을 {new} (으)로 바꿨습니다."))

    def cmd_whisper(self, session, arg):
        # /w 닉네임 메시지
        bits = arg.split(" ", 1)
        if len(bits) < 2:
            self.server.send_to(session, SystemMessage("사용법: /w 닉네임 메시지"))
            return
        target_name, text = bits[0], bits[1]
        target = self.server.connections.find_by_nickname(target_name)
        if target is None:
            self.server.send_to(session, SystemMessage(f"그런 사람이 없습니다: {target_name}"))
            return
        self.server.send_to(target, TextMessage(text, sender=f"(귓속말) {session.nickname}"))
        self.server.send_to(session, TextMessage(text, sender=f"(귓속말 → {target_name}) 나"))
