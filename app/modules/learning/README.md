# `learning` 모듈

학습자가 풀 문제의 원본을 저장하고 조회한다.

## 테이블 역할

`LearningTask.__tablename__ = "learning_tasks"`이며, 팀 ERD에서 말하는 `tasks` 역할에 대응한다.

`learning_tasks`는 비동기 처리 상태를 저장하는 테이블이 아니다. 문제 제목, 설명, 시작 코드, 기준 답안, 보상량 등 여러 사용자가 공통으로 조회하는 문제 정의를 저장한다.

| 파일 | 역할 |
| --- | --- |
| `models.py` | `learning_tasks` ORM 모델 |
| `router.py` | `GET /tasks`, `GET /tasks/{task_id}` endpoint |

API 응답에는 `reference_solution`을 포함하지 않아 정답 코드가 학습자에게 노출되지 않도록 한다.

현재 개념 태그, 난이도, 문제 유형, 테스트 케이스, 승인 상태, 추천 기능은 구현되지 않았다.
