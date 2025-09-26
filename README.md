# Connecta Manager

인플루언서 캠페인 관리 시스템

## 기능

### 📋 캠페인 관리
- 시딩, 홍보, 판매 캠페인 생성 및 관리
- 캠페인별 참여 인플루언서 관리
- 샘플 발송 상태 추적

### 👥 인플루언서 관리
- 인플루언서 정보 등록 및 관리
- 플랫폼별 인플루언서 분류
- 팔로워 수, 활동 점수 등 상세 정보 관리

### 📈 성과 관리
- **성과 관리 탭**: 개별 인플루언서 성과 입력 및 관리
- **리포트 탭**: 종합 성과 분석 대시보드
  - 캠페인별 성과 요약
  - 인플루언서별 성과 랭킹
  - 성과 트렌드 분석
  - 샘플 상태별 분석
  - ROI 계산

## 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Streamlit Cloud

## 설치 및 실행

### 로컬 개발 환경

1. 저장소 클론
```bash
git clone https://github.com/kchsung/connecta-manager.git
cd connecta-manager
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 Supabase 설정을 추가하세요:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

5. 애플리케이션 실행
```bash
streamlit run app.py
```

### Streamlit Cloud 배포

1. [Streamlit Cloud](https://share.streamlit.io/)에 접속
2. GitHub 저장소 연결: `kchsung/connecta-manager`
3. Secrets에서 다음 환경 변수 설정:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

## 데이터베이스 스키마

### 주요 테이블
- `campaigns`: 캠페인 정보
- `connecta_influencers`: 인플루언서 정보
- `campaign_influencer_participations`: 캠페인 참여 정보
- `campaign_influencer_contents`: 성과 지표 데이터

## 라이선스

MIT License

## 기여

이슈나 풀 리퀘스트를 통해 기여해주세요.