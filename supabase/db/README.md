# Supabase 데이터베이스 스키마

이 폴더는 Connecta Manager 프로젝트의 Supabase 데이터베이스 스키마를 포함합니다.

## 파일 구조

```
supabase/db/
├── enums.sql                                    # ENUM 타입 정의
├── connecta_influencers.sql                     # 인플루언서 테이블
├── campaigns.sql                                # 캠페인 테이블
├── campaign_influencer_participations.sql       # 캠페인 참여 테이블
├── campaign_influencer_contents.sql             # 콘텐츠 성과 테이블
└── README.md                                    # 이 파일
```

## 테이블 관계

```
campaigns (1) ──→ (N) campaign_influencer_participations (1) ──→ (N) campaign_influencer_contents
     │                                                                    
     └─── (1) ──→ (N) connecta_influencers
```

## 주요 특징

### 1. ENUM 타입 사용
- `platform_type`: 플랫폼 (instagram, youtube, tiktok, twitter)
- `campaign_type`: 캠페인 타입 (seeding, promotion, sales)
- `campaign_status`: 캠페인 상태 (planned, active, paused, completed, cancelled)
- `contact_method`: 연락 방법 (dm, email, phone, kakao, form, other)
- `sample_status`: 샘플 상태 (요청, 발송준비, 발송완료, 수령)

### 2. Row Level Security (RLS)
- 모든 테이블에 RLS 정책 적용
- 사용자는 자신이 생성한 데이터만 접근 가능
- 외래키 관계를 통한 권한 상속

### 3. 인덱스 최적화
- 자주 조회되는 컬럼에 인덱스 생성
- 성능 최적화를 위한 복합 인덱스

### 4. 자동 업데이트
- `updated_at` 필드 자동 업데이트 트리거
- 데이터 변경 시 자동으로 타임스탬프 갱신

## 사용 방법

1. **로컬 개발**: 각 `.sql` 파일을 Supabase 대시보드의 SQL Editor에서 실행
2. **프로덕션**: Supabase CLI를 사용하여 마이그레이션 실행
3. **스키마 확인**: Supabase 대시보드의 Table Editor에서 테이블 구조 확인

## 주의사항

- ENUM 타입은 먼저 생성해야 함 (`enums.sql` 실행)
- 테이블 생성 순서: enums → connecta_influencers → campaigns → campaign_influencer_participations → campaign_influencer_contents
- RLS 정책은 테이블 생성 후 자동으로 적용됨
