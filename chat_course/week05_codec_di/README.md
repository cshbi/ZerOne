# Week 5 (통합) — 부품과 계약: Codec · 의존성 주입 · 테스트

> 기존 **week05(Codec/보안)** 와 **week06(DI/테스트)** 를 한 주로 합친 버전입니다.
> 4주차 `class_basics`(특히 `step07_di_taste`·`step08_di_contract`)에서 이미
> "부품을 밖에서 끼운다 / 약속을 클래스로 못박는다"를 다뤘으므로, 이 주는
> **개념 반복을 걷어내고 '실제 채팅에 적용 + 탈취 데모 + 테스트'에 집중**합니다.

## 이 주에 새로 얻는 것 (4주차와 겹치지 않는 알맹이)
1. **평문이 왜 위험한지** — 중간자(도청자)가 실제로 내용을 훔치는 걸 눈으로 본다 (`sniffer.py`)
2. **Codec** — 변환(직렬화·암호화)을 부품으로 떼어 평문 ↔ 암호화를 한 줄로 전환
   - 이름의 정체: **Codec = COder + DECoder**. 동영상·오디오 코덱의 그 코덱이다
     ("코덱이 없어 영상이 안 열려요" = decode 할 부품이 없다는 뜻). 자세한 어원은
     `codec.py` 맨 위 주석 참고 — 학생들이 "그게 이거였어?" 하는 지점
3. **abc(진짜 계약)** — 4주차의 `Ringtone`(안내판)이 `@abstractmethod`(강제)로 승격
4. **DI로 조립한 서버** — `ChatServer(codec, store)`, 저장소를 메모리 ↔ 파일로 교체
5. **네트워크 없이 확인** — 가짜 부품을 주입해 소켓 없이 두뇌 검증 (`demo_fake_parts.py`)

## 파일
| 파일 | 설명 |
|------|------|
| `messages.py` | 4주차 메시지 객체 재사용 (수정 없음) |
| `interfaces.py` | 계약(abc): `Codec` · `MessageStore` · `Transport` |
| `codec.py` | `PlainCodec` / `SecretCodec` (계약을 지키는 변환 부품) |
| `server.py` | `ChatServer(codec, store)` 두뇌 + 저장 부품 + 조립부 |
| `client.py` | 같은 Codec 을 끼운 클라이언트 |
| `sniffer.py` | **평문 탈취 데모 (중간자/도청자)** ★ 이번 주 하이라이트 |
| `demo_fake_parts.py` | 가짜 부품을 꽂아 **네트워크 없이** 두뇌 확인 (DI의 이점 시연) |

---

## 🕵️ 해킹 데모: 평문 탈취 (sniffer.py)

"내 메시지가 중간에 그대로 보이는 거 아냐?" 를 **직접** 보여 줍니다.
`sniffer.py` 는 클라이언트와 서버 **사이에 끼어드는 중간자**입니다.
오가는 내용을 그대로 흘려보내(채팅은 멀쩡) 동시에 몰래 엿봅니다(탈취).

```
클라이언트 ──▶ [ sniffer.py = 도청자(나) ] ──▶ 진짜 서버
              (5000 에서 받아 5001 로 중계하며 전부 엿본다)
```

### 실행 (터미널 3개)
```bash
# ① 진짜 서버를 5001 로 숨긴다: server.py 맨 위 PORT = 5000 → PORT = 5001 로 바꾼 뒤
python server.py
python sniffer.py         # ② 도청자가 5000 에서 받아 5001 로 중계 (sniffer 는 안 고쳐도 됨)
python client.py          # ③ 학생은 평소처럼 5000 으로 접속 (사실은 도청자에게!)
# ④ client 에 "비밀번호는 1234야" 를 쳐 보고 sniffer 창을 본다
```
> 포트는 week01 부터 해온 대로 **파일 맨 위 `PORT` 상수**만 고칩니다(명령행 인자 안 씀).
> 데모가 끝나면 server.py 의 `PORT` 를 다시 5000 으로 되돌리면 평소 채팅이 됩니다.
> (client.py 는 늘 5000 그대로 — 고칠 필요 없습니다.)

### 평문일 때 (기본, `USE_SECRET = False`)
```
😱 [탈취 성공] 클라 → 서버  |  TEXT|철수|비밀번호는 1234야
```
→ 접속했을 뿐인데 대화가 **그대로** 털린다.

### 암호화로 바꾸면 (`server.py` + `client.py` 의 `USE_SECRET = True`)
```
🔒 [탈취 실패] 클라 → 서버  |  fm9yflbGmIrGorJWwZOu...   ← 알아볼 수 없음
```
→ 같은 도청자인데 이제 **못 읽는다**. 부품(Codec)만 바꿨을 뿐.

> **토론 포인트**: 암호화해도 첫 줄 닉네임(`철수`)은 평문으로 보입니다.
> 핸드셰이크가 암호화 전에 오가기 때문 — "무엇을 암호화하고 무엇을 안 하나"의 실마리.

### (심화) "이건 왜 진짜 보안이 아닌가"
`sniffer.py` 위쪽 `SHOW_CRACK = True` 로 켜면, 코드에 **박혀 있는 열쇠(42)** 로
암호를 도로 풉니다.
```
🔒 [탈취 실패] ...  ← 알아볼 수 없음
    └ (박힌 열쇠 42 로 복호화) TEXT|철수|비밀번호는 1234야   ← 그래서 진짜 보안이 아니다!
```
→ 열쇠가 코드에 있으면 XOR 은 쉽게 뚫린다. **진짜 보안은 TLS(HTTPS/WSS).**

> ⚠️ 이 도청 시연은 **수업용**입니다. 남의 통신을 실제로 엿보는 것은 불법입니다.
> 반드시 내 PC(localhost) 안에서, 내가 띄운 서버로만 실습하세요.

---

## 보통 채팅 실행 (도청자 없이)
```bash
python server.py          # 5000
python client.py          # 5000, 터미널 여러 개
```

## 네트워크 없이 확인 (DI의 이점 시연)
```bash
python demo_fake_parts.py     # 가짜 부품을 꽂아 소켓 없이 두뇌를 확인
```
보여 주는 것: ① 모두에게 전달 ② 저장됨 ③ Codec 을 암호화로 바꿔도 두뇌는 그대로
④ 저장이 실패해도 채팅은 계속. — 전부 소켓을 한 번도 안 열고 확인합니다.

> unittest 격식 대신, 가짜 부품(`FakeTransport`/`FakeStore`/`FailingStore`)을 직접
> 꽂아 출력으로 보여 줍니다. "가짜를 꽂으니 네트워크 없이 되네"의 깨달음이 목표이고,
> 원한다면 이 데모를 그대로 `unittest` 로 감싸는 게 심화 과제가 됩니다.

## 부품 갈아끼우기 (server.py 의 build_server 한 곳만)
```python
store = InMemoryStore()              # 끄면 사라짐
store = FileStore("chat_log.txt")    # 재시작해도 남음  ← 한 줄만 바꿔 끼운다
# ChatServer 코드는 그대로!
```

---

## 4주차와의 연결 (한 줄 대응)
| 4주차 class_basics | 이번 주 |
|---|---|
| `step07` Phone(ringtone) 주입 | `ChatServer(codec, store)` 주입 |
| `step08` `Ringtone`(약속, 안내판) | `interfaces.Codec`(abc, **강제**) |
| `Ringtone.play()` | `Codec.encode()/decode()` |
| "상속 안 해도 꽂히더라(안내판)" | `@abstractmethod` 는 안 지키면 **에러로 막는다** |

## 2시간 수업 배분(제안)
1. **(10분)** 복습 브릿지 — `step07`의 `StuckPhone` 을 띄우고 "병명과 처방을 말해 보라"
2. **(15분)** 🕵️ 평문 탈취 데모 (sniffer) — 충격으로 시작
3. **(25분)** Codec: `Ringtone`→`Codec` 대응으로 빠르게, Plain↔Secret 교체 + 스니퍼 재실행
4. **(15분)** abc 승격: "안내판 → 강제"(`@abstractmethod`) — 4주차 복선 회수
5. **(35분)** `ChatServer(codec, store)` 주입 + FileStore 교체 + `demo_fake_parts.py`(가짜 부품으로 네트워크 없이 확인)
6. **(20분)** 실습 — 나만의 SecretCodec 변형 / FailingStore 테스트 / (심화) SHOW_CRACK 켜 보기

> `Transport`(두뇌가 소켓을 모른다)까지 깊게 가면 벅찹니다. 소개만 하고
> 자세한 리팩터링은 9주차(서버 종합 리팩터링)로 넘기면 부담이 줍니다.

## 실습 / 과제
1. `SecretCodec` 의 변환 규칙(열쇠·방식)을 바꿔 나만의 버전 만들기
2. "왜 이건 진짜 보안이 아닌가"를 한 줄로 적어 오기 (힌트: `SHOW_CRACK`)
3. `FileStore` 주입해 재시작 후에도 기록이 남는지 확인
4. `FailingStore` 같은 실패 부품으로 예외 처리 테스트 추가
