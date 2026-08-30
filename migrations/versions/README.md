# `migrations/versions` 폴더

실제 DB schema 변경 순서를 기록한다.

| Revision | 내용 |
| --- | --- |
| `0001_create_users.py` | `users` 테이블 생성 |
| `0002_mvp_vertical_slice.py` | `learning_tasks`, `attempts`, `reward_ledger`, `shop_items`, `inventory_items`, `housing_placements` 생성 |

`learning_tasks`는 ERD의 `tasks`, `attempts`는 ERD의 `task_attempts`에 대응한다. 명칭을 통일할 경우 기존 파일을 수정하지 말고 새 rename migration을 추가해야 한다.
