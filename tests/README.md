# 테스트 폴더

이 폴더는 Connecta Manager 프로젝트의 모든 테스트 파일들을 포함합니다.

## 폴더 구조

```
tests/
├── unit/                    # 단위 테스트
│   ├── test_models.py      # 모델 테스트
│   ├── test_utils.py       # 유틸리티 함수 테스트
│   └── test_auth.py        # 인증 관련 테스트
├── integration/            # 통합 테스트
│   ├── test_database.py    # 데이터베이스 통합 테스트
│   ├── test_api.py         # API 통합 테스트
│   └── test_supabase.py    # Supabase 통합 테스트
├── e2e/                    # End-to-End 테스트
│   ├── test_user_flow.py   # 사용자 플로우 테스트
│   ├── test_campaign.py    # 캠페인 관리 E2E 테스트
│   └── test_influencer.py  # 인플루언서 관리 E2E 테스트
└── README.md               # 이 파일
```

## 테스트 실행 방법

### 단위 테스트
```bash
python -m pytest tests/unit/ -v
```

### 통합 테스트
```bash
python -m pytest tests/integration/ -v
```

### E2E 테스트
```bash
python -m pytest tests/e2e/ -v
```

### 전체 테스트
```bash
python -m pytest tests/ -v
```

## 테스트 작성 가이드

### 1. 단위 테스트 (unit/)
- 개별 함수나 클래스의 동작을 테스트
- 외부 의존성은 모킹 처리
- 빠른 실행 속도

### 2. 통합 테스트 (integration/)
- 여러 컴포넌트 간의 상호작용 테스트
- 실제 데이터베이스나 API 사용
- 중간 수준의 실행 속도

### 3. E2E 테스트 (e2e/)
- 전체 사용자 시나리오 테스트
- 실제 브라우저나 앱 환경에서 테스트
- 느린 실행 속도, 하지만 가장 실제적

## 주의사항

- 모든 테스트 파일은 `test_` 접두사로 시작
- 테스트 데이터는 `samples/data/` 폴더 사용
- 테스트 실행 전 환경 변수 설정 확인
- 테스트 후 정리 작업 수행
