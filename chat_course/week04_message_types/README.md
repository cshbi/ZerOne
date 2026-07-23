# Week 4 — 메시지 종류를 객체로: 다형성

3주차의 흩어진 `if/elif` 를 **메시지 클래스 + 다형성**으로 걷어냅니다.
새 종류는 **클래스 하나만 추가**하면 끝 — 서버·받기 코드는 바뀌지 않습니다.

## 파일
| 파일 | 설명 |
|------|------|
| `messages.py` | `Message` 기반 + `Text/Emoji/File/System Message`, 해석기 `from_wire` |
| `server.py` | 종류를 묻지 않는 서버 (`from_wire` → `to_wire` 만) |
| `client.py` | 받기는 `display()` 한 줄, 보내기는 객체 생성 한 번 |
| `make_ppt.py` / `Week04_메시지객체_다형성.pptx` | 강의 슬라이드 (발표자 노트 포함) |

## 실행 방법
```bash
python server.py                  # 터미널 1
python client.py                  # 터미널 2, 3 …
```
대화 중:
- 그냥 입력 → 텍스트
- `/emoji smile` → 이모티콘 (smile/heart/thumbsup/cry/wow)
- `/file <경로>` → 파일 (받는 사람 `downloads/` 에 저장)

## 핵심 개념
- **공통 약속(메서드)**: `to_wire()`(전송용), `display()`(화면 표시)
- **다형성**: 같은 `display()` 호출이 종류마다 다르게 동작
- **해석은 한 곳**: `Message.from_wire(line)` 이 꼬리표로 알맞은 객체를 만든다
- 받기·서버에서 **`if/elif` 가 사라진다**

## BEFORE → AFTER
```python
# 3주차: 받을 때마다 종류를 물었다
if line.startswith("TEXT|"): ...
elif line.startswith("FILE|"): ...
elif line.startswith("EMOJI|"): ...

# 4주차: 종류를 묻지 않는다
msg = Message.from_wire(line)
print(msg.display())
```

## 실습 / 과제
1. 위치 공유 `LocationMessage` 추가 (힌트는 `messages.py` 맨 아래 주석)
   → 서버·받기 코드를 **거의 안 건드리는 것**을 확인
2. 이모티콘 종류 늘리기 (`EMOJI` 표에 추가)
3. (생각) `display()` 가 '저장'까지 하는 게 맞을까? → 6주차 관심사 분리의 복선

## PPT 다시 만들기 (강사용)
```bash
pip install python-pptx
python make_ppt.py
```
