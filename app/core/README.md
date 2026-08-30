# `app/core` 폴더

여러 모듈이 공통으로 사용하는 애플리케이션 설정을 관리한다.

현재 `config.py`의 `Settings`가 `.env`에서 `DATABASE_URL`을 읽는다. 기본 개발값은 PostgreSQL의 `cat_game` 데이터베이스를 가리킨다.

실제 비밀번호나 API 키는 코드에 적거나 commit하지 않고 `.env` 또는 배포 환경변수로 주입한다.
