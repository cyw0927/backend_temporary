# Cat Game Backend — Vertical Slice MVP

프로그래밍 초보자를 위한 고양이 학습 게임의 FastAPI 백엔드이다.

이 저장소는 전체 PRD 완성본이 아니라, **문제 조회 → 코드 제출 → 백그라운드 채점 → 결과 조회 → 1회 보상 → 상품 구매 → 보유 가구 사용**으로 이어지는 백엔드 핵심 흐름을 실행하고 검증한 세로형(vertical slice) MVP이다.

## 1. 현재 구동 가능한 범위

```text
FastAPI 서버 실행
→ PostgreSQL 연결
→ Alembic migration 적용
→ 사용자 조회
→ 학습 문제 목록·상세 조회
→ 코드 제출 및 PENDING attempt 생성
→ 백그라운드 채점
→ 채점 결과 polling
→ 정답 보상 1회 지급
→ 상점 상품 조회·구매
→ 잔액 차감 및 inventory 반영
→ 보유 가구 조회·배치
```

| 모듈 | 현재 구현 내용 |
| --- | --- |
| Health | FastAPI 서버 및 데이터베이스 연결 상태 확인 |
| Identity | ID 기반 사용자 정보·재화 잔액 조회 |
| Learning | 문제 목록·상세 조회, 기준 정답 비공개 |
| Grading | 제출 기록 생성, HTTP 202, 백그라운드 채점, 결과 polling |
| Economy | 정답 보상 지급 기록, 동일 attempt 중복 보상 방지 |
| Shop | 활성 상품 조회, 조건부 원자적 잔액 차감, inventory 반영 |
| Housing | 보유 상품 조회, 소유한 furniture의 슬롯 배치 |
| Database | SQLAlchemy 모델, PostgreSQL 연결, Alembic migration |
| Test | 외부 서비스 없이 핵심 흐름을 검증하는 자동화 테스트 |

## 2. `tasks`와 `task_attempts` 역할 정정

초기 설명에서 `tasks`를 비동기 처리를 저장하는 테이블로 잘못 설명했으나, ERD 분석 결과 다음과 같이 정정한다.

| ERD 용어 | 현재 코드의 실제 테이블명 | 역할 |
| --- | --- | --- |
| `tasks` | `learning_tasks` | 문제 제목, 설명, 시작 코드, 기준 답안, 보상량 등 **문제 원본** 저장 |
| `task_attempts` | `attempts` | 사용자 제출 코드, `PENDING`/`COMPLETED`/`FAILED` 상태, 정답 여부, 결과 메시지 등 **제출 및 채점 결과** 저장 |

`attempts`가 비동기 처리 자체를 저장하는 것은 아니다. 사용자의 제출 건과 백그라운드 채점 작업의 현재 상태 및 결과를 영속적으로 기록하여, 클라이언트가 나중에 결과를 조회할 수 있도록 한다.

```text
learning_tasks에서 문제 조회
→ 사용자가 코드 제출
→ attempts에 PENDING 기록을 먼저 commit
→ 백그라운드 채점 실행
→ attempts를 COMPLETED 또는 FAILED로 변경
→ 클라이언트가 attempt ID로 결과 조회
```

향후 팀 ERD와 실제 데이터베이스 명칭을 통일할지는 별도 migration으로 결정해야 한다. 기존 migration을 직접 수정하거나 테이블명을 임의로 바꾸지 않는다.

## 3. 주요 API

| Method | Endpoint | 기능 |
| --- | --- | --- |
| `GET` | `/health` | FastAPI 서버 상태 확인 |
| `GET` | `/health/db` | 데이터베이스 연결 상태 확인 |
| `GET` | `/users/{user_id}` | 사용자 정보 조회 |
| `GET` | `/tasks` | 문제 목록 조회 |
| `GET` | `/tasks/{task_id}` | 문제 상세 조회 |
| `POST` | `/tasks/{task_id}/submissions` | `PENDING` 제출 기록 생성 및 채점 요청 |
| `GET` | `/attempts/{attempt_id}` | 채점 상태와 결과 조회 |
| `GET` | `/shop/items` | 판매 중인 상품 조회 |
| `POST` | `/shop/items/{item_id}/purchase` | 상품 구매 |
| `GET` | `/users/{user_id}/housing` | 보유 상품과 배치 상태 조회 |
| `PUT` | `/users/{user_id}/housing/{slot}` | 보유 가구 배치·변경 |

Swagger UI: `http://127.0.0.1:8000/docs`

## 4. Windows PowerShell 실행 방법

### 저장소 복제

```powershell
cd C:\dev
git clone https://github.com/cyw0927/backend_temporary.git
cd backend_temporary
```

### 가상환경과 패키지 설치

PowerShell 실행 정책 때문에 활성화가 차단되더라도 사용할 수 있도록 가상환경의 Python을 직접 호출한다.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

가상환경을 활성화하려면 현재 PowerShell 창에서만 실행 정책을 완화한다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### PostgreSQL 준비

`.env.example`의 기본 설정은 다음과 같다.

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/cat_game
```

PostgreSQL에 `cat_game` 데이터베이스를 만들고, 실제 사용자명과 비밀번호에 맞게 `.env`를 수정한다. 실제 비밀번호가 들어간 `.env`는 Git에 commit하지 않는다.

### Migration과 서버 실행

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

실행 후 확인 주소:

- 서버 상태: `http://127.0.0.1:8000/health`
- DB 상태: `http://127.0.0.1:8000/health/db`
- API 문서: `http://127.0.0.1:8000/docs`

`http://127.0.0.1:8000/`에는 별도 화면이 없으므로 `{"detail":"Not Found"}`가 나오는 것이 정상이다.

### 테스트

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

현재 자동화 테스트는 SQLite를 이용하므로 PostgreSQL이나 Docker 없이 실행할 수 있다.

## 5. 데이터 안전성과 transaction 정책

- 제출 API는 `attempts`에 `PENDING` 행을 먼저 commit한 후 HTTP 202를 반환한다.
- 외부 평가기 실행 중에는 DB transaction이나 row lock을 유지하지 않는다.
- 프로세스 내부 semaphore가 동시 채점 작업을 최대 4개로 제한한다.
- `reward_ledger.attempt_id` UNIQUE 제약으로 동일 attempt의 보상 중복 지급을 막는다.
- 정답 보상 잔액 증가는 원자적 `UPDATE`로 처리한다.
- 구매 시 `balance >= price` 조건이 포함된 원자적 `UPDATE`로 잔액을 차감한다.
- 잔액 차감과 inventory 반영은 같은 transaction에서 처리한다.
- 사용자가 실제로 보유한 `furniture`만 housing에 배치할 수 있다.

## 6. 현재 채점기의 범위

현재 `DeterministicEvaluator`는 제출된 Python 코드를 직접 실행하지 않는다. 제출 코드와 문제의 기준 답안을 정규화한 뒤 문자열로 비교하는 개발용 fake evaluator이다.

따라서 현재 구현은 제출 기록의 선행 commit, 백그라운드 채점 호출, 상태·결과 저장, polling, 정답 보상의 1회 지급 흐름을 검증한다.

실제 Python 실행 채점기는 후속 개발에서 Docker adapter로 교체해야 한다. 그때 실제로 적용·검증해야 할 제한은 다음과 같다.

- 네트워크 차단
- 읽기 전용 파일 시스템 적용 범위
- 프로세스 생성 제한
- 약 128MB 메모리와 약 0.5 CPU 제한
- 실행 시간 및 출력 크기 제한
- 실행 종료 후 컨테이너 폐기

`import os` 자체가 자동으로 차단된다고 설명해서는 안 된다. 허용·차단 범위는 실제 sandbox 정책과 검증 결과에 따라 문서화해야 한다.

## 7. 비동기 처리의 현재 한계

현재 구현은 FastAPI `BackgroundTasks`와 프로세스 내부 semaphore를 사용한다.

- 서버 재시작 시 진행 중인 작업이 유실될 수 있다.
- 여러 worker 사이에서 작업을 공유하지 않는다.
- 영속적인 재시도와 장애 복구 기능이 없다.

운영·멀티워커 환경에서는 Redis Queue, Celery 등의 durable queue로 교체해야 한다.

## 8. 초기 데이터 주의사항

Migration은 테이블 구조만 생성한다. 사용자, 문제, 상품을 자동 등록하지 않으므로 새 DB에서는 `/tasks`와 `/shop/items`가 빈 목록을 반환한다.

전체 흐름을 수동으로 시험하려면 최소한 사용자 1명, 학습 문제 1개, 활성 상점 상품 1개가 필요하다. 개발용 seed 데이터는 실제 제품 정책과 분리하여 후속 작업으로 추가한다.

## 9. 검증 완료 항목

- FastAPI 애플리케이션 import
- Python 문법 및 모듈 import 검사
- 핵심 자동화 테스트
- Alembic 단일 head 확인
- 빈 테스트 DB에 migration 적용
- SQLAlchemy metadata와 migration 정합성 검사
- 전체 downgrade 후 재적용
- PostgreSQL dialect용 migration SQL 생성

마지막 검증 결과:

```text
pytest -q
7 passed
```

SQLite 기반 자동화 검증은 완료했다. 실제 PostgreSQL 접속과 Docker 컨테이너 실행은 구현 환경에서 검증하지 못했으므로 성공했다고 주장하지 않는다.

## 10. 아직 구현되지 않은 PRD 범위

- 회원가입·로그인·인증
- 선택형·O/X·실행 결과 예측 퀴즈
- 개념 태그와 기초·응용·도전 난이도
- 오프라인 학습 이력 연동
- 개념별 숙련도 계산과 문제 추천
- 단계별 힌트와 상세 피드백
- 실제 테스트 케이스 기반 Python sandbox 채점
- 고양이 모델·수집·단일 및 10+1 뽑기
- 희귀도·확률·천장·중복 교환 정책
- 격자 기반 가구 이동·회전·삭제
- 벽지·바닥 적용
- 고양이 대화·기억 관리
- 공개 하우스 방문·돌봄
- 그룹 순위와 신고·숨김·제재
- 게임 프런트엔드와 Tauri 앱

가챠 비용·확률·천장, battle 점수, ranking 규칙, daily mission 보상량, proficiency 공식, hint 정책, AI provider, mileage 의미는 제품 정책이 확정되지 않아 TBD로 유지한다.

## 11. 폴더 안내

| 폴더 | 설명 |
| --- | --- |
| [`app/`](app/README.md) | FastAPI 애플리케이션 코드 |
| [`app/api/`](app/api/README.md) | 공통 API |
| [`app/core/`](app/core/README.md) | 환경설정 등 공통 핵심 설정 |
| [`app/db/`](app/db/README.md) | SQLAlchemy Base, engine, session |
| [`app/integrations/`](app/integrations/README.md) | 외부 AI·queue adapter 연결 지점 |
| [`app/modules/`](app/modules/README.md) | 기능별 도메인 모듈 |
| [`migrations/`](migrations/README.md) | Alembic migration 환경 |
| [`tests/`](tests/README.md) | 자동화 테스트 |
| [`docs/`](docs/README.md) | 설계·분석 문서 보관 위치 |
| [`infra/`](infra/README.md) | 향후 배포·인프라 설정 위치 |

각 기능 폴더의 세부 역할은 해당 폴더 안의 `README.md`에서 확인할 수 있다.
