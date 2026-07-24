"""
Week 5(통합) - demo_fake_parts.py  :  가짜 부품으로 '네트워크 없이' 확인
============================================================
DI(부품을 밖에서 주입)의 진짜 이점을 눈으로 봅니다.

  ChatServer 는 부품(codec, store, transport)을 '주입받아' 쓴다.
  → 그럼 진짜 부품 대신 '가짜 부품'을 꽂을 수 있다!
  → 소켓(네트워크)을 한 번도 안 열고 서버 두뇌를 확인할 수 있다.

보통 채팅 서버를 확인하려면: 서버 켜고 → 클라이언트 여러 개 띄우고 →
타이밍 맞춰 메시지 보내고 → 눈으로 확인… 매번 손이 많이 갑니다.
가짜 부품을 꽂으면 이 파일 하나 실행으로 끝납니다.

실행:  python demo_fake_parts.py
"""

from interfaces import Transport, MessageStore
from codec import PlainCodec, SecretCodec
from messages import TextMessage
from server import ChatServer


# ── 가짜 부품들 (계약만 지키면 진짜 대신 쓸 수 있다 — 4주차 step08 의 그 계약!) ──
class FakeTransport(Transport):
    """진짜 소켓 대신, 보낸 바이트를 리스트에 '기록만' 한다."""
    def __init__(self):
        self.sent = []

    def send(self, data):
        self.sent.append(data)


class FakeStore(MessageStore):
    """진짜 파일 대신, 메모리에 모아두는 가짜 저장소."""
    def __init__(self):
        self.saved = []

    def save(self, message):
        self.saved.append(message)

    def all(self):
        return list(self.saved)


class FailingStore(MessageStore):
    """저장할 때마다 일부러 실패하는 가짜 저장소 (예외 상황 흉내)."""
    def save(self, message):
        raise IOError("디스크가 꽉 찼습니다")

    def all(self):
        return []


def line(title):
    print("\n" + "─" * 50 + f"\n{title}\n" + "─" * 50)


# ============================================================
# 데모 1: 한 사람이 보내면 '모두'에게 가는가 — 소켓 없이 확인
# ============================================================
line("데모 1: 브로드캐스트 (소켓 없이)")
server = ChatServer(PlainCodec(), FakeStore())
minsu, younghee = FakeTransport(), FakeTransport()      # 가짜 '연결' 두 개
server.join(minsu, "민수")
server.join(younghee, "영희")
minsu.sent.clear(); younghee.sent.clear()               # 입장 알림은 비우고 시작

server.on_line(minsu, TextMessage("안녕!").to_wire())    # 민수가 한 줄 보냄

# 진짜 서버였다면 소켓으로 나갔을 데이터가, 가짜에는 리스트에 남는다 → 그대로 확인!
print("영희가 받은 것:", younghee.sent)
got = PlainCodec().decode(younghee.sent[0].decode().rstrip("\n"))
print(f"  → 해석하면: '{got.display()}'  (보낸사람={got.sender})")
print("민수도 받았나?:", "예" if minsu.sent else "아니오")


# ============================================================
# 데모 2: 받은 메시지가 '저장'되는가
# ============================================================
line("데모 2: 저장 (가짜 저장소)")
store = FakeStore()
server = ChatServer(PlainCodec(), store)
server.join(FakeTransport(), "민수")
server.on_line(list(server.clients)[0], TextMessage("기록해줘").to_wire())
print("저장된 메시지 수:", len(store.all()))
print("저장된 내용:", store.all()[0].text)


# ============================================================
# 데모 3: Codec 을 '암호화'로 바꿔도 두뇌 코드는 그대로 도는가
# ============================================================
line("데모 3: 부품 교체 (평문 → 암호화)")
server = ChatServer(SecretCodec(), FakeStore())        # store 는 그대로, codec 만 교체
a, b = FakeTransport(), FakeTransport()
server.join(a, "민수"); server.join(b, "영희")
b.sent.clear()
server.on_line(a, SecretCodec().encode(TextMessage("비밀", sender="민수")).decode().rstrip("\n"))
wire = b.sent[0].decode().rstrip("\n")
print("영희에게 나간 줄:", wire)
print("  → '비밀' 이 그대로 보이나?:", "아니오(암호화됨) ✅" if "비밀" not in wire else "예")
print("  → 풀어보면:", SecretCodec().decode(wire).text)
print("  ※ ChatServer 코드는 한 줄도 안 바꿨다. codec 부품만 갈아끼웠을 뿐!")


# ============================================================
# 데모 4: 저장이 '실패'해도 채팅은 계속되는가
# ============================================================
line("데모 4: 저장 실패해도 채팅은 계속")
server = ChatServer(PlainCodec(), FailingStore())      # 저장이 늘 실패하는 부품
a, b = FakeTransport(), FakeTransport()
server.join(a, "민수"); server.join(b, "영희")
b.sent.clear()
server.on_line(a, TextMessage("그래도 가야지").to_wire())   # 저장은 실패하지만…
print("영희는 메시지를 받았나?:", "예 ✅ (저장 실패와 무관하게 전달됨)" if b.sent else "아니오")

print("\n✔ 네 가지 모두 '소켓 한 번 안 열고' 확인했습니다. 이게 DI 의 힘입니다.")
