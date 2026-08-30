# `app/api` 폴더

특정 기능 모듈 하나에 속하지 않는 공통 API를 둔다.

현재 `health.py`가 다음 endpoint를 제공한다.

- `GET /health`: FastAPI 프로세스가 요청에 응답하는지 확인
- `GET /health/db`: DB에 `SELECT 1`을 실행하여 연결 상태 확인

`/health` 성공은 서버가 켜졌다는 뜻이고, PostgreSQL 연결 성공까지 의미하지 않는다. DB 상태는 반드시 `/health/db`로 별도 확인한다.
