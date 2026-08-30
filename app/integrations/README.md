# `app/integrations` 폴더

외부 시스템이나 교체 가능한 infrastructure adapter의 연결 지점이다.

| 폴더 | 예정 역할 | 현재 상태 |
| --- | --- | --- |
| `ai/` | Gemini 등 서버 측 AI provider 연결 | 골격만 존재 |
| `queue/` | Redis Queue, Celery 등 durable queue 연결 | 골격만 존재 |

도메인 로직이 특정 외부 서비스에 직접 종속되지 않도록 adapter 경계를 두기 위한 폴더이다.
