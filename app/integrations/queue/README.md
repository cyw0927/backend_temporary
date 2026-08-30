# `app/integrations/queue` 폴더

향후 durable queue를 연결하기 위한 adapter 위치이다.

현재 채점은 FastAPI `BackgroundTasks`와 프로세스 내부 semaphore를 사용한다. 서버 재시작 시 작업이 유실될 수 있고 여러 worker가 작업을 공유하지 못하므로, 운영 단계에서는 Redis Queue나 Celery 등으로 교체해야 한다.
