# `grading` 모듈

사용자의 제출 기록, 채점 상태, 채점 결과를 관리한다.

## 테이블 역할 정정

`Attempt.__tablename__ = "attempts"`이며, 팀 ERD의 `task_attempts` 역할에 대응한다.

`attempts`는 비동기 실행 엔진 자체를 저장하는 테이블이 아니다. 제출 한 건마다 다음 정보를 저장하여 백그라운드 채점의 진행 상태와 결과를 나중에 조회할 수 있게 한다.

- 사용자와 문제 ID
- 제출 코드
- `PENDING`, `COMPLETED`, `FAILED` 상태
- 정답 여부와 결과 메시지
- 제출 및 완료 시각

## 파일 역할

| 파일 | 역할 |
| --- | --- |
| `models.py` | `attempts` ORM 모델 |
| `router.py` | 제출과 결과 polling endpoint |
| `service.py` | DB transaction을 분리한 채점·보상 흐름 |
| `evaluator.py` | 현재 개발용 문자열 비교 evaluator |

## 처리 흐름

```text
POST /tasks/{task_id}/submissions
→ attempts에 PENDING 생성 및 commit
→ HTTP 202 응답 생성
→ BackgroundTasks에서 평가
→ 새 DB session으로 결과 저장
→ GET /attempts/{attempt_id}로 조회
```

평가기 실행 중에는 DB transaction이나 lock을 유지하지 않는다. 현재 evaluator는 Python을 실행하지 않으며 실제 Docker sandbox는 미구현이다.
