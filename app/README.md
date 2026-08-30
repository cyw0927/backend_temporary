# `app` 폴더

FastAPI 백엔드의 실제 애플리케이션 코드가 들어 있다.

## 주요 구성

| 위치 | 역할 |
| --- | --- |
| `main.py` | `create_app()`으로 FastAPI 앱을 만들고 각 router를 등록한다. 실행 진입점은 `app.main:app`이다. |
| `api/` | 특정 도메인에 속하지 않는 공통 API |
| `core/` | 환경변수 등 애플리케이션 공통 설정 |
| `db/` | SQLAlchemy Base, engine, session 관리 |
| `modules/` | identity, learning, grading 등 기능별 코드 |
| `integrations/` | AI, durable queue 등 외부 시스템 연결 지점 |

서버 실행 명령:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
