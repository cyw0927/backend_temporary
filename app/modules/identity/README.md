# `identity` 모듈

사용자 기본 정보와 조회 기능을 담당한다.

| 파일 | 역할 |
| --- | --- |
| `models.py` | `users` 테이블 ORM 모델 |
| `service.py` | DB·FastAPI에 직접 종속되지 않는 사용자 조회 규칙 |
| `router.py` | `GET /users/{user_id}` endpoint |

현재 로그인, 회원가입, 토큰 인증은 구현되지 않았다. URL이나 요청 본문의 `user_id`를 신뢰하는 개발용 단계이므로 운영 전에 인증·인가가 필요하다.

`balance`는 학습 재화 잔액이며 구매와 정답 보상에서 변경된다. `mileage`의 제품 의미는 아직 TBD이다.
