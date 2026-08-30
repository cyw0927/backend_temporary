# `migrations` 폴더

Alembic이 데이터베이스 schema 변경 이력을 관리하는 폴더이다.

| 위치 | 역할 |
| --- | --- |
| `env.py` | DB URL과 SQLAlchemy metadata를 Alembic에 연결 |
| `script.py.mako` | 새 revision 파일의 기본 템플릿 |
| `versions/` | 순서대로 적용되는 실제 migration 파일 |

적용:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

현재 revision 확인:

```powershell
.\.venv\Scripts\python.exe -m alembic current
```

이미 공유된 migration은 직접 고치지 않고 schema 변경마다 새 revision을 추가한다.
