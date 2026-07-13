"""
Week 2 - 서버 (server.py)  :  여러 명이 동시에, 단체 채팅
------------------------------------------------------------
1주차 서버는 손님을 '한 명만' 받았습니다.
이번에는 여러 명이 동시에 접속해서, 한 사람이 보낸 말을
'접속한 모두'에게 다시 뿌립니다(= 브로드캐스트).

핵심 도구 두 가지:
  - clients : 접속한 소켓을 모아 두는 목록 (전역)
  - threading : 손님마다 전담 직원(스레드)을 한 명씩 붙인다
                → 여러 사람을 '동시에' 받을 수 있다

이 파일도 아직 클래스(객체)는 쓰지 않습니다. 함수와 전역변수만 사용.
------------------------------------------------------------
실행:  python server.py   (먼저 켜 두세요)
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

# 접속한 소켓 -> 닉네임  (누가 접속해 있는지 전부 여기 모인다)
clients = {} #배열(dictionary)
# 여러 스레드가 clients 를 동시에 건드리면 꼬일 수 있어 자물쇠로 보호한다
clients_lock = threading.Lock()


def broadcast(text, exclude = None):
    """접속한 모두에게 같은 문장을 보낸다 (= 중앙 우체국에서 전원에게 배달)."""
    data = text.encode("utf-8")
    with clients_lock:
        targets = list(clients.keys())   # 잠깐 복사해서 안전하게 순회
    for sock in targets:
        if sock is exclude:
            continue #건너뛴다
        try:
            sock.sendall(data)
        except OSError:
            pass   # 이미 끊긴 소켓은 그냥 건너뛴다


def handle(conn, addr):
    """손님 한 명을 전담하는 함수. 손님마다 별도 스레드로 실행된다."""
    # 접속하면 가장 먼저 닉네임 한 줄을 받는다
    try:
        nickname = conn.recv(1024).decode("utf-8").strip()
    except OSError:
        conn.close()
        return
    if not nickname:
        nickname = f"손님{addr[1]}"

    # 목록에 추가하고, 모두에게 입장 소식을 알린다
    with clients_lock:
        clients[conn] = nickname
        count = len(clients)
    print(f"[서버] {nickname} 접속  (현재 {count}명)")
    broadcast(f"*** {nickname}님이 들어왔습니다 (현재 {count}명) ***")

    # 이 손님이 보내는 말을 계속 받아서 전원에게 뿌린다
    while True:
        try:
            data = conn.recv(1024) #메세지를 컴퓨터언어로 보냄
        except OSError: #에러뜨면 넘어가
            break
        if not data:          # 빈 데이터 = 손님이 나갔다 넘어가
            break
        message = data.decode("utf-8") #사람이 볼 수 있는 언어로 바꿔

        #"/count" 명령어 처리
        if message.strip() == "/count": #.strip()은 "/count"를 치고 엔터를 누르면 서버에서 줄바꿈으로 인식할 수 있어 공백을 제거하기 위해 쓰임
            with clients_lock: #락 걸고 클라이언트 목록 세고
                count = len(clients)
            try: #"/count" 이거 친 사람한테만 현재 접속자 수 보여줌 사람이 볼 수 있는 언어로 바꿔서 
                conn.sendall(f"[서버]현재 접속자 수 : {count}명\n".encode("utf-8"))
            except OSError: #try는 "일단 이거 해봐" 이고, except는 "만약 이거 하다가 에러 터지면, 프로그램 죽지 말고 이렇게 대처해"
                break
            continue
        broadcast(f"{nickname}: {message}", exclude=conn) #계속 채팅

    # 퇴장 처리: 목록에서 빼고, 모두에게 알린다
    with clients_lock:
        clients.pop(conn, None)
        count = len(clients)
    conn.close()
    print(f"[서버] {nickname} 퇴장  (현재 {count}명)")
    broadcast(f"*** {nickname}님이 나갔습니다 (현재 {count}명) ***")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[서버] {HOST}:{PORT} 에서 손님을 기다립니다... (Ctrl+C 로 종료)")

    try:
        while True:
            # 손님이 올 때마다 연결을 받아서
            conn, addr = server_socket.accept()
            # 그 손님 전담 스레드를 하나 띄운다 → accept 루프는 곧바로 다음 손님을 받으러 간다
            t = threading.Thread(target=handle, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[서버] 종료합니다.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
