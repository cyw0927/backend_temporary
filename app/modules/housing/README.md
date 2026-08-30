# `housing` 모듈

사용자가 보유한 가구와 현재 슬롯 배치를 조회·변경한다.

| 파일 | 역할 |
| --- | --- |
| `models.py` | 사용자·슬롯별 배치를 저장하는 `housing_placements` 모델 |
| `router.py` | 하우징 조회와 가구 배치 endpoint |

제공 API:

- `GET /users/{user_id}/housing`
- `PUT /users/{user_id}/housing/{slot}`

배치 전에 inventory 소유 여부와 `item_type == "furniture"`를 검사한다. 현재 `slot` 문자열 기반의 단순 배치이며, PRD의 격자 좌표, 이동, 회전, 삭제, 충돌 검사, 벽지·바닥 적용, 공개 방문은 구현되지 않았다.
