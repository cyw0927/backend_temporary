# `tests` 폴더

외부 PostgreSQL이나 Docker 없이 핵심 백엔드 흐름을 검증한다.

| 파일 | 검증 내용 |
| --- | --- |
| `test_health.py` | 서버 health와 DB health endpoint |
| `test_mvp.py` | 사용자 조회, 문제 조회, 제출·채점·polling, 보상 중복 방지, 구매, inventory, housing 소유권 |

테스트는 메모리 SQLite DB를 사용하고 FastAPI의 DB dependency와 채점용 `SessionLocal`을 테스트 session으로 교체한다.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

SQLite 테스트 통과가 실제 PostgreSQL·Docker 실검증을 대신하지는 않는다.
