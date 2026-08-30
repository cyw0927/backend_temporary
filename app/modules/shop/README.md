# `shop` 모듈

상점 상품, 구매, 사용자 inventory를 관리한다.

| 모델 | 테이블 | 역할 |
| --- | --- | --- |
| `ShopItem` | `shop_items` | 상품명, 유형, 가격, 활성 상태 |
| `InventoryItem` | `inventory_items` | 사용자가 보유한 상품과 수량 |

제공 API:

- `GET /shop/items`: 활성 상품 목록
- `POST /shop/items/{item_id}/purchase`: 상품 구매

구매는 `user_id`가 존재하고 잔액이 가격 이상일 때만 `balance = balance - price`가 실행되는 조건부 원자적 `UPDATE`를 사용한다. 잔액 차감과 inventory 반영은 같은 transaction에서 commit된다.

현재 환불, 선물, 거래, 유료 재화는 구현되지 않았다.
