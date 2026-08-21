-- ============================================================
-- 01_crud.sql  :  한 테이블로 CRUD 4형제 (DML)
-- ============================================================
-- DML = 데이터를 다루는 명령. CRUD = Create/Read/Update/Delete.
--   INSERT(추가) · SELECT(조회) · UPDATE(수정) · DELETE(삭제)
-- 먼저 messages 한 테이블에서만 연습합니다 (JOIN 은 다음 파일).
--
-- 실행:  python run_sql.py 01_crud.sql
--   (run_sql.py 가 매번 schema+seed 로 DB 를 새로 만든 뒤 이 파일을 실행합니다)
-- ============================================================

-- ── C: INSERT (추가) ──────────────────────────────
-- 잡담방(1)에 철수(1)가 새 메시지를 남긴다
INSERT INTO messages (room_id, user_id, content) VALUES (1, 1, '나 왔어');

-- ── R: SELECT (조회) ──────────────────────────────
-- 잡담방(1)의 모든 메시지를 시간 순으로
SELECT message_id, user_id, kind, content
FROM   messages
WHERE  room_id = 1
ORDER BY message_id;

-- 조건 좁히기: 텍스트 메시지만
SELECT content FROM messages WHERE room_id = 1 AND kind = 'TEXT';  

-- 개수 세기: 잡담방 메시지 몇 개?
SELECT COUNT(*) AS 잡담방_메시지수 FROM messages WHERE room_id = 1;

-- ── U: UPDATE (수정) ──────────────────────────────
-- 방금 넣은 '나 왔어' 를 고친다  (WHERE 를 빼먹으면 전체가 바뀐다! 항상 WHERE)
UPDATE messages SET content = '나 이제 왔어~', WHERE content = '나 왔어';

-- 확인
SELECT content FROM messages WHERE content = '나 이제 왔어~';

-- ── D: DELETE (삭제) ──────────────────────────────
-- 이모티콘 메시지를 지운다  (역시 WHERE 필수)
DELETE FROM messages WHERE kind = 'EMOJI';

-- 확인: 이제 EMOJI 가 없어야 한다
SELECT COUNT(*) AS 남은_이모티콘 FROM messages WHERE kind = 'EMOJI';

-- ============================================================
-- ⚠️ 새기고 갈 것: UPDATE/DELETE 에 WHERE 를 빼먹으면 '전체'가 바뀌거나 지워진다.
--    실무 대형 사고 1위. 항상 WHERE 를 먼저 쓰는 습관!
-- ============================================================
