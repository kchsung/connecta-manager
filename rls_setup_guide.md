# RLS (Row Level Security) 설정 가이드

## 문제 상황
Supabase RLS를 활성화한 후 데이터베이스 접근이 안 되는 문제가 발생했습니다.

## 원인 분석
1. **인증 토큰이 데이터베이스 쿼리에 전달되지 않음**
2. **Supabase 클라이언트가 인증된 사용자 컨텍스트로 초기화되지 않음**
3. **기존 테이블들에 대한 RLS 정책이 누락됨**

## 해결 방법

### 1. 코드 수정 완료
- `src/supabase/config.py`: 인증 토큰이 포함된 클라이언트 반환
- `src/db/database.py`: RLS 오류 처리 및 인증된 클라이언트 사용
- `src/supabase/auth.py`: 토큰을 클라이언트에 자동 설정

### 2. 데이터베이스 RLS 정책 설정
`rls_policies.sql` 파일을 Supabase SQL Editor에서 실행하세요:

```sql
-- 기존 테이블들에 대한 RLS 정책 설정
-- connecta_influencers, connecta_influencer_crawl_raw 등
```

### 3. 테이블 구조 확인
다음 테이블들이 `user_id` 컬럼을 가지고 있는지 확인:
- `connecta_influencers`
- `connecta_influencer_crawl_raw`
- `campaigns` (created_by 컬럼)
- `campaign_influencer_participations`
- `campaign_influencer_contents`

### 4. 테스트 방법
1. 애플리케이션에서 로그인
2. 데이터 조회/생성/수정/삭제 테스트
3. 브라우저 개발자 도구에서 네트워크 탭 확인
4. Supabase 대시보드에서 Authentication > Users 확인

## 주의사항
- RLS 정책은 즉시 적용됩니다
- 기존 데이터에 `user_id`가 없다면 접근할 수 없습니다
- 테스트 전에 백업을 권장합니다

## 문제 해결 체크리스트
- [ ] 로그인 상태 확인
- [ ] 토큰이 session_state에 저장되는지 확인
- [ ] RLS 정책이 올바르게 설정되었는지 확인
- [ ] 테이블에 user_id 컬럼이 있는지 확인
- [ ] 데이터베이스 쿼리에서 인증 오류가 발생하는지 확인
