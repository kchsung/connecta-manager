# Supabase Edge Functions

이 디렉토리는 Connecta Manager를 위한 Supabase Edge Functions를 포함합니다.

## 함수 목록

### 1. 캠페인 관리 (`/campaigns`)
- **GET** `/campaigns` - 캠페인 목록 조회
- **GET** `/campaigns?id={id}` - 특정 캠페인 조회
- **POST** `/campaigns` - 새 캠페인 생성
- **PUT** `/campaigns?id={id}` - 캠페인 업데이트
- **DELETE** `/campaigns?id={id}` - 캠페인 삭제

### 2. 인플루언서 관리 (`/influencers`)
- **GET** `/influencers` - 인플루언서 목록 조회
- **GET** `/influencers?id={id}` - 특정 인플루언서 조회
- **GET** `/influencers?platform={platform}` - 플랫폼별 인플루언서 조회
- **GET** `/influencers?search={term}` - 인플루언서 검색
- **POST** `/influencers` - 새 인플루언서 생성
- **PUT** `/influencers?id={id}` - 인플루언서 업데이트
- **DELETE** `/influencers?id={id}` - 인플루언서 삭제

### 3. 캠페인 참여 관리 (`/campaign-participations`)
- **GET** `/campaign-participations` - 참여 목록 조회
- **GET** `/campaign-participations?id={id}` - 특정 참여 조회
- **GET** `/campaign-participations?campaign_id={id}` - 캠페인별 참여자 조회
- **POST** `/campaign-participations` - 새 참여 생성
- **PUT** `/campaign-participations?id={id}` - 참여 정보 업데이트
- **DELETE** `/campaign-participations?id={id}` - 참여 삭제

### 4. 캠페인 콘텐츠 관리 (`/campaign-contents`)
- **GET** `/campaign-contents` - 콘텐츠 목록 조회
- **GET** `/campaign-contents?id={id}` - 특정 콘텐츠 조회
- **GET** `/campaign-contents?participation_id={id}` - 참여별 콘텐츠 조회
- **POST** `/campaign-contents` - 새 콘텐츠 생성
- **PUT** `/campaign-contents?id={id}` - 콘텐츠 업데이트
- **DELETE** `/campaign-contents?id={id}` - 콘텐츠 삭제

### 5. 분석 및 통계 (`/analytics`)
- **GET** `/analytics?type=overview` - 전체 개요 통계
- **GET** `/analytics?type=campaign&campaign_id={id}` - 캠페인별 통계
- **GET** `/analytics?type=influencer` - 인플루언서별 통계
- **GET** `/analytics?type=performance` - 성과 통계

## 배포 방법

### 1. Supabase CLI 설치
```bash
npm install -g supabase
```

### 2. 로그인 및 프로젝트 연결
```bash
supabase login
supabase link --project-ref YOUR_PROJECT_REF
```

### 3. 함수 배포
```bash
# 모든 함수 배포
supabase functions deploy

# 특정 함수 배포
supabase functions deploy campaigns
supabase functions deploy influencers
supabase functions deploy campaign-participations
supabase functions deploy campaign-contents
supabase functions deploy analytics
```

## 환경 변수 설정

Supabase 대시보드에서 다음 환경 변수를 설정해야 합니다:

- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_SERVICE_ROLE_KEY`: 서비스 역할 키

## 인증

모든 함수는 JWT 토큰을 통한 인증을 요구합니다. 요청 헤더에 다음을 포함해야 합니다:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

## CORS

모든 함수는 CORS를 지원하며, 다음 헤더를 자동으로 설정합니다:

- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Headers: authorization, x-client-info, apikey, content-type`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`

## RLS (Row Level Security)

모든 데이터베이스 쿼리는 RLS 정책을 준수합니다:
- 사용자는 자신이 생성한 데이터만 접근 가능
- 인증되지 않은 요청은 거부됨
- 모든 테이블에 적절한 RLS 정책이 설정되어야 함

## 에러 처리

모든 함수는 일관된 에러 응답 형식을 사용합니다:

```json
{
  "success": false,
  "error": "Error type",
  "message": "사용자 친화적인 오류 메시지"
}
```

## 로깅

함수 실행 중 발생하는 오류는 Supabase 대시보드의 Functions 로그에서 확인할 수 있습니다.

## 테스트

로컬에서 함수를 테스트하려면:

```bash
# 로컬 개발 서버 시작
supabase functions serve

# 함수 테스트
curl -X GET "http://localhost:54321/functions/v1/campaigns" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

