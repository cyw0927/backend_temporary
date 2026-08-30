# `app/db` 폴더

SQLAlchemy 데이터베이스 공통 구성을 관리한다.

| 파일 | 역할 |
| --- | --- |
| `base.py` | 모든 ORM 모델이 상속하는 `Base` 선언 |
| `session.py` | engine, `SessionLocal`, FastAPI용 `get_db()` 제공 |

각 HTTP 요청은 `get_db()`로 session을 받고 요청이 끝나면 닫는다. 백그라운드 채점은 요청 session을 재사용하지 않고 새 `SessionLocal`을 사용한다.

테이블 변경은 모델만 수정해서 끝내지 않고 반드시 새 Alembic revision을 추가한다.
