# Connecta Manager API - 통합 Edge Function

모든 기능을 하나의 Edge Function으로 통합한 API입니다.

## 🚀 Supabase Cloud에 배포하기

### 1. Supabase 대시보드에서 함수 생성

1. **Supabase 대시보드** → **Edge Functions** 탭으로 이동
2. **"Create a new function"** 클릭
3. 함수 이름: `connecta-manager-api`
4. **"Create function"** 클릭

### 2. 코드 복사 및 붙여넣기

1. `connecta-manager-api.ts` 파일의 전체 내용을 복사
2. Supabase 대시보드의 함수 에디터에 붙여넣기
3. **"Deploy"** 클릭

## 📡 API 사용법

### 기본 URL 형식
```
https://YOUR_PROJECT_REF.supabase.co/functions/v1/connecta-manager-api
```

### 인증 헤더 (필수)
```javascript
headers: {
  'Authorization': `Bearer ${jwtToken}`,
  'Content-Type': 'application/json'
}
```

## 🎯 API 엔드포인트

### 1. 캠페인 관리

#### 캠페인 목록 조회
```javascript
GET /connecta-manager-api?path=campaigns
```

#### 특정 캠페인 조회
```javascript
GET /connecta-manager-api?path=campaigns&id=CAMPAIGN_ID
```

#### 새 캠페인 생성
```javascript
POST /connecta-manager-api?path=campaigns
Content-Type: application/json

{
  "campaign_name": "새 캠페인",
  "campaign_type": "seeding",
  "start_date": "2024-01-01",
  "campaign_description": "캠페인 설명"
}
```

#### 캠페인 업데이트
```javascript
PUT /connecta-manager-api?path=campaigns&id=CAMPAIGN_ID
Content-Type: application/json

{
  "campaign_name": "수정된 캠페인명",
  "status": "active"
}
```

#### 캠페인 삭제
```javascript
DELETE /connecta-manager-api?path=campaigns&id=CAMPAIGN_ID
```

### 2. 인플루언서 관리

#### 인플루언서 목록 조회
```javascript
GET /connecta-manager-api?path=influencers
```

#### 플랫폼별 인플루언서 조회
```javascript
GET /connecta-manager-api?path=influencers&platform=instagram
```

#### 인플루언서 검색
```javascript
GET /connecta-manager-api?path=influencers&search=검색어
```

#### 특정 인플루언서 조회
```javascript
GET /connecta-manager-api?path=influencers&id=INFLUENCER_ID
```

#### 새 인플루언서 생성
```javascript
POST /connecta-manager-api?path=influencers
Content-Type: application/json

{
  "platform": "instagram",
  "sns_id": "influencer_id",
  "sns_url": "https://instagram.com/influencer_id",
  "influencer_name": "인플루언서명",
  "content_category": "뷰티"
}
```

### 3. 분석 및 통계

#### 전체 개요 통계
```javascript
GET /connecta-manager-api?path=analytics&type=overview
```

## 🔧 JavaScript 사용 예시

```javascript
// JWT 토큰 가져오기 (Supabase Auth에서)
const { data: { session } } = await supabase.auth.getSession()
const token = session?.access_token

// API 호출 함수
async function callAPI(path, options = {}) {
  const url = new URL('https://YOUR_PROJECT_REF.supabase.co/functions/v1/connecta-manager-api')
  url.searchParams.set('path', path)
  
  // 쿼리 파라미터 추가
  if (options.id) url.searchParams.set('id', options.id)
  if (options.platform) url.searchParams.set('platform', options.platform)
  if (options.search) url.searchParams.set('search', options.search)
  if (options.type) url.searchParams.set('type', options.type)

  const response = await fetch(url, {
    method: options.method || 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: options.body ? JSON.stringify(options.body) : undefined
  })

  return await response.json()
}

// 사용 예시
async function loadCampaigns() {
  const result = await callAPI('campaigns')
  if (result.success) {
    console.log('캠페인 목록:', result.data)
  }
}

async function createCampaign(campaignData) {
  const result = await callAPI('campaigns', {
    method: 'POST',
    body: campaignData
  })
  if (result.success) {
    console.log('캠페인 생성됨:', result.data)
  }
}

async function loadInfluencers(platform) {
  const result = await callAPI('influencers', { platform })
  if (result.success) {
    console.log('인플루언서 목록:', result.data)
  }
}

async function getAnalytics() {
  const result = await callAPI('analytics', { type: 'overview' })
  if (result.success) {
    console.log('통계:', result.data)
  }
}
```

## 🔐 보안 기능

- **JWT 토큰 인증**: 모든 요청에 유효한 토큰 필요
- **RLS 정책**: 사용자는 자신의 데이터만 접근 가능
- **CORS 지원**: 웹 애플리케이션에서 안전한 호출
- **에러 처리**: 일관된 에러 응답 형식

## 📊 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": { ... },
  "message": "성공 메시지"
}
```

### 에러 응답
```json
{
  "success": false,
  "error": "에러 타입",
  "message": "사용자 친화적인 에러 메시지"
}
```

## ⚠️ 주의사항

1. **RLS 정책 설정**: 배포 전에 `rls_policies.sql`을 Supabase SQL Editor에서 실행
2. **인증 토큰**: 모든 API 호출에 JWT 토큰 포함 필요
3. **환경 변수**: Supabase에서 자동으로 설정됨
4. **에러 로깅**: Supabase 대시보드의 Functions 로그에서 확인 가능

## 🎉 장점

- **단일 함수**: 하나의 Edge Function으로 모든 기능 제공
- **간단한 배포**: 한 번만 배포하면 모든 API 사용 가능
- **통합 관리**: 모든 엔드포인트를 하나의 함수에서 관리
- **비용 효율**: 여러 함수 대신 하나의 함수로 비용 절약

