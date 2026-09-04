# Part 2 ↔ 최신 main 호환성 검토

기준일: 2026-09-04

## 결론

Part 2 수정본은 최신 `KANT-2/cat-game-backend` main의 Part 3 공통 기반과 호환된다. Part 3 기능 구현 파일 자체는 변경하지 않았다.

## 실제 변경 범위

최신 main ZIP을 기준으로 작업본을 비교했을 때 변경 파일은 다음 Part 2 범위로 제한된다.

- `app/modules/learning/router.py`
- `app/modules/grading/lifecycle.py`
- `app/schemas/task_attempt.py`
- `app/schemas/user.py`
- `docs/api/README.md`
- `docs/features/README.md`
- `docs/features/part2-integration-contract.md`
- `tests/test_client_integration.py`
- `tests/unit/test_part2_learning.py`
- `tests/unit/test_part2_response_contracts.py`

`cats`, `gacha`, `housing`, `shop`, Part 3 repository/UoW, Part 3 migration 내용은 수정하지 않았다.

## 공통 기반 호환성 확인

### API 조합

최신 main은 `app/api/router.py`에서 identity, grading, learning, cats, gacha, shop, housing, daily, battle router를 한 `api_router`에 합치고 `app/main.py`가 `/api/v1` prefix로 노출한다. Part 2의 신규 `GET /learning/tasks`는 기존 learning router 내부에 추가되므로 이 구조를 깨지 않는다.

### 인증

모든 Part 2 보호 API는 공통 `CurrentUser`를 사용한다. 운영/통합 환경은 Django `sessionid`를 Auth Bridge로 전달하며, 로컬/테스트에서만 `X-User-Public-ID`를 허용하는 최신 main 구조를 그대로 사용한다.

`users.homepage_user_id` DB 매핑은 유지하되 `UserRead` 공개 DTO에서는 제거했다. 따라서 Django 사용자 연결에는 영향이 없고 내부 홈페이지 정수 ID만 외부 응답에서 숨긴다.

### DB 식별자

최신 main의 공통 Base는 내부 INTEGER PK와 외부 UUID `public_id` 구조다. Part 2 수정은 이를 변경하지 않는다. 새 `/learning/tasks`도 `concept_public_id` UUID를 받아 내부 `concept.id`로 조회한다.

### 마이그레이션

Part 2 작업에서 신규 migration을 추가하지 않았다. 기존 Part 2 분류 migration과 Part 2/Part 3 merge-head migration은 최신 main 버전을 그대로 유지한다. 따라서 Part 3 migration chain을 건드리지 않는다.

### 채점 runner

최신 main의 `GradeResult`는 `verdict`, `passed`, `total`, `detail`을 이미 제공한다. Part 2 lifecycle은 이 값을 기존 `result_detail` TEXT(JSON 문자열)에 함께 저장하고 API DTO에서 구조화된 객체로 변환한다. DB 컬럼 타입 변경이나 migration은 필요 없다.

## 검증 결과

로컬 작업본에서 최신 main 전체 파일을 베이스로 두고 Part 2 변경만 적용한 상태로 검증했다.

```text
Part 2 직접 관련 테스트: 23 passed
전체 테스트: 248 passed, 20 skipped
```

현재 실행 환경에는 실제 `psycopg` 패키지/SQL grader PostgreSQL이 없어서 SQL 연결이 필요한 통합 테스트는 임시 import stub으로 수집 가능하게 한 뒤 정상적으로 skip되도록 했다. 따라서 위 전체 테스트 결과의 20 skipped에는 실제 PostgreSQL/Docker 등 외부 실행환경이 필요한 테스트가 포함된다.

Python 문법 컴파일은 정상 통과했다.

## 이번 Part 2 마무리에서 추가된 계약

- `GET /api/v1/learning/tasks`
  - `type`
  - `domain`
  - `concept_public_id`
  - `difficulty`
  - `limit`
- 이미 정답 처리한 문제의 `completed=true`
- `homepage_user_id` 공개 DTO 비노출
- `result_detail` API 응답 구조화
- DAILY/BATTLE 요청·응답·오류 계약 문서화
- `401/403/404/409/422/503` 오류 행렬
- async grading polling 규칙

## 남은 외부 의존 작업

Part 2 코드 자체와 Part 3 호환성에는 현재 추가 수정이 필요하지 않다. 남은 항목은 외부 통합 단계다.

- Django 홈페이지 `/api/auth/me/` 실제 구현 후 로그인 E2E
- Integration/Production URL 및 reverse proxy 확정
- DAILY 보상액, BATTLE 점수 정책값 확정
- 운영 환경에서 실제 Docker/Python grader 및 PostgreSQL SQL grader 재검증

이 항목들은 Part 3 기능 구현과는 별개이며, Part 2 코드 변경 없이 환경/외부 계약이 준비된 뒤 종단간 검증할 수 있다.
