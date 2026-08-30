# `app/modules` 폴더

기능별 도메인 코드를 분리한다. 구현된 모듈과 빈 골격을 구분해야 한다.

| 모듈 | 역할 | 상태 |
| --- | --- | --- |
| `identity/` | 사용자 정보 | MVP 구현 |
| `learning/` | 문제 원본 조회 | MVP 구현 |
| `grading/` | 제출·채점 상태·결과 | MVP 구현 |
| `economy/` | 보상 지급 원장 | MVP 구현 |
| `shop/` | 상품·구매·inventory | MVP 구현 |
| `housing/` | 보유 가구 조회·슬롯 배치 | MVP 구현 |
| `cats/` | 고양이 수집·상호작용 | 골격만 존재 |
| `gacha/` | 고양이 뽑기 | 골격만 존재 |
| `battle/` | battle 기능 | 골격만 존재 |
| `daily_mission/` | 일일 미션 | 골격만 존재 |
| `ranking/` | 선택형 그룹 순위 | 골격만 존재 |

일반적인 파일 역할:

- `models.py`: SQLAlchemy ORM 모델
- `router.py`: HTTP endpoint와 요청·응답 처리
- `service.py`: FastAPI와 분리 가능한 업무 규칙
- `evaluator.py`: 교체 가능한 채점 adapter

router는 HTTP 처리에 집중하고, 재사용하거나 단위 테스트할 업무 규칙은 service로 분리한다.
