# `economy` 모듈

학습 재화 보상의 지급 이력을 관리한다.

`reward_ledger`는 attempt별 보상 내역을 기록하며 `attempt_id`에 UNIQUE 제약이 있어 동일 제출의 보상이 두 번 지급되는 것을 DB 수준에서 막는다.

정답 보상 시 사용자 잔액은 `balance = balance + reward_amount` 형태의 원자적 `UPDATE`로 증가한다.

현재 보상량은 `learning_tasks.reward_amount` 데이터로 관리한다. 최초 완료 보상, 힌트 사용에 따른 추가 보상, daily mission 보상 정책은 아직 구현되지 않았다.
