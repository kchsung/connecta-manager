# Connecta Manager - 인플루언서 관리 시스템 📋

인플루언서 캠페인 관리를 위한 종합적인 Streamlit 웹 애플리케이션입니다.

## 🏗️ 프로젝트 구조

```
connecta-manager/
├── src/                    # 소스 코드
│   ├── ui/                 # UI 컴포넌트
│   │   ├── auth_components.py
│   │   ├── project_components.py
│   │   └── __init__.py
│   ├── db/                 # 데이터베이스 관련
│   │   ├── models.py
│   │   ├── database.py
│   │   └── __init__.py
│   └── supabase/           # Supabase 연동
│       ├── config.py
│       ├── auth.py
│       └── __init__.py
├── css/                    # 스타일시트
│   └── main.css
├── app.py                  # 메인 애플리케이션
├── requirements.txt        # 의존성
├── supabase_schema.sql     # 데이터베이스 스키마
└── README.md
```

## ✨ 주요 기능

### 🔐 사용자 인증
- Supabase Email Provider를 통한 회원가입/로그인
- 사용자별 데이터 격리
- 비밀번호 재설정 기능

### 📋 캠페인 관리
- **캠페인 생성**: 시딩, 홍보, 판매 캠페인 생성
- **캠페인 수정**: 기존 캠페인 정보 수정 및 삭제
- **캠페인 목록**: 모든 캠페인 조회 및 필터링
- **캠페인 상태 관리**: 계획됨, 진행중, 일시정지, 완료, 취소 상태 관리

### 👥 인플루언서 관리
- **인플루언서 등록**: 플랫폼별 인플루언서 등록 및 관리
- **인플루언서 목록**: 등록된 인플루언서 조회 및 필터링
- **인플루언서 정보 수정**: 기존 인플루언서 정보 수정 및 삭제

### 📊 캠페인 참여 관리
- **인플루언서 추가**: 캠페인에 인플루언서 참여 추가
- **참여 정보 관리**: 담당자 의견, 요청사항, 비용, 샘플 상태 등 관리
- **컨텐츠 링크 관리**: 인플루언서가 업로드한 컨텐츠 링크 관리
- **참여 현황 조회**: 캠페인별 참여 인플루언서 현황 확인

### 📈 성과 관리
- **성과 지표 입력**: 좋아요, 댓글, 공유, 조회수, 클릭수, 전환수 등
- **성과 히스토리**: 시간별 성과 추이 차트 및 데이터 표시
- **성과 분석**: 캠페인별, 인플루언서별 성과 분석

## 🚀 설치 및 실행

### 1. Supabase 프로젝트 설정

1. [Supabase](https://supabase.com)에서 새 프로젝트 생성
2. `supabase_schema.sql` 파일의 내용을 Supabase SQL Editor에서 실행
   - 캠페인 관리 테이블 (campaigns, connecta_influencers)
   - 캠페인 참여 테이블 (campaign_influencer_participations)
   - 성과 관리 테이블 (performance_metrics)
   - RLS (Row Level Security) 정책 설정
3. Authentication > Settings에서 Email Provider 활성화

### 2. 환경 변수 설정

#### 로컬 개발
```bash
# .env 파일에 Supabase 정보 입력
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

#### Streamlit Cloud 배포
1. Streamlit Cloud에서 Secrets 설정
2. `.streamlit/secrets.toml.example`을 참고하여 secrets 설정

### 3. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

```bash
streamlit run app.py
```

### 5. 브라우저에서 확인

애플리케이션이 실행되면 자동으로 브라우저가 열리고 `http://localhost:8501`에서 확인할 수 있습니다.

## 사용 방법

### 📋 캠페인 관리
1. **캠페인 생성**: 
   - 캠페인 이름, 유형(시딩/홍보/판매), 설명 입력
   - 시작일, 종료일, 상태 설정
   - 캠페인 지시사항 및 태그 입력
2. **캠페인 수정**: 기존 캠페인 정보 수정 및 삭제
3. **캠페인 목록**: 필터링을 통한 캠페인 조회

### 👥 인플루언서 관리
1. **인플루언서 등록**:
   - 플랫폼, SNS ID, 표시 이름, 팔로워 수 등 입력
2. **인플루언서 목록**: 플랫폼별 필터링을 통한 인플루언서 조회
3. **인플루언서 정보 수정**: 기존 인플루언서 정보 수정 및 삭제

### 📊 캠페인 참여 관리
1. **인플루언서 추가**: 
   - 캠페인 선택 후 인플루언서 검색
   - 담당자 의견, 요청사항, 비용, 샘플 상태 등 입력
2. **참여 정보 관리**: 참여 인플루언서의 상세 정보 수정
3. **컨텐츠 링크 관리**: 인플루언서가 업로드한 컨텐츠 링크 추가/삭제

### 📈 성과 관리
1. **프로젝트 선택**: 성과를 확인할 캠페인 선택
2. **성과 입력**: 수동으로 성과 지표 입력 (좋아요, 댓글, 공유 등)
3. **성과 분석**: 시간별 성과 추이 차트 및 상세 데이터 확인

## 지원하는 플랫폼

- **Instagram** 📸
- **YouTube** 📺
- **TikTok** 🎵
- **Twitter** 🐦

## 기술 스택

- **Streamlit**: 웹 애플리케이션 프레임워크
- **Supabase**: 백엔드 데이터베이스 및 인증
- **Pandas**: 데이터 처리
- **Pydantic**: 데이터 모델링

## 주의사항

⚠️ **중요**: 이 도구는 교육 및 연구 목적으로만 사용하세요.

- 각 플랫폼의 이용약관을 준수해야 합니다
- 개인정보 보호에 주의하세요
- 상업적 사용 시 관련 법규를 확인하세요

## 라이선스

이 프로젝트는 교육 목적으로만 사용되어야 하며, 상업적 사용은 권장하지 않습니다.