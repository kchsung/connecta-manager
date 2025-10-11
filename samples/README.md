# 샘플 파일 폴더

이 폴더는 Connecta Manager 프로젝트의 샘플 데이터, 스크립트, 설정 파일들을 포함합니다.

## 폴더 구조

```
samples/
├── data/                   # 샘플 데이터 파일
│   ├── influencers.xlsx   # 인플루언서 샘플 데이터
│   ├── campaigns.xlsx     # 캠페인 샘플 데이터
│   ├── participations.xlsx # 참여 정보 샘플 데이터
│   └── contents.xlsx      # 콘텐츠 성과 샘플 데이터
├── scripts/               # 샘플 스크립트
│   ├── create_test_data.py # 테스트 데이터 생성 스크립트
│   ├── import_sample.py   # 샘플 데이터 임포트 스크립트
│   └── cleanup_data.py    # 데이터 정리 스크립트
├── configs/               # 샘플 설정 파일
│   ├── .env.example       # 환경 변수 예시
│   ├── streamlit_config.toml # Streamlit 설정 예시
│   └── supabase_config.json # Supabase 설정 예시
└── README.md              # 이 파일
```

## 사용 방법

### 1. 샘플 데이터 사용
```bash
# 인플루언서 샘플 데이터 확인
python samples/scripts/import_sample.py --type influencers

# 캠페인 샘플 데이터 확인
python samples/scripts/import_sample.py --type campaigns
```

### 2. 테스트 데이터 생성
```bash
# 테스트용 데이터 생성
python samples/scripts/create_test_data.py --count 100

# 특정 타입의 테스트 데이터 생성
python samples/scripts/create_test_data.py --type influencers --count 50
```

### 3. 설정 파일 사용
```bash
# 환경 변수 설정
cp samples/configs/.env.example .env
# .env 파일을 편집하여 실제 값 입력

# Streamlit 설정
cp samples/configs/streamlit_config.toml .streamlit/config.toml
```

## 파일 설명

### 데이터 파일 (data/)
- **influencers.xlsx**: 인플루언서 정보 샘플 데이터
- **campaigns.xlsx**: 캠페인 정보 샘플 데이터
- **participations.xlsx**: 캠페인 참여 정보 샘플 데이터
- **contents.xlsx**: 콘텐츠 성과 정보 샘플 데이터

### 스크립트 파일 (scripts/)
- **create_test_data.py**: 테스트용 데이터 생성
- **import_sample.py**: 샘플 데이터 임포트
- **cleanup_data.py**: 테스트 데이터 정리

### 설정 파일 (configs/)
- **.env.example**: 환경 변수 설정 예시
- **streamlit_config.toml**: Streamlit 설정 예시
- **supabase_config.json**: Supabase 설정 예시

## 주의사항

- 샘플 데이터는 개발/테스트 목적으로만 사용
- 프로덕션 환경에서는 실제 데이터 사용
- 민감한 정보는 샘플 파일에 포함하지 않음
- 샘플 스크립트 실행 전 환경 설정 확인
