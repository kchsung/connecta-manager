# Supabase Anon Key 설정 완료

## 🔧 **수정된 내용**

### ✅ **1. Anon Key 사용**
- Service Role Key 대신 SUPABASE_ANON_KEY 사용
- .env 파일에서 환경 변수 로드
- Streamlit secrets를 통한 설정 지원

### ✅ **2. 개발 모드 개선**
- anon key를 사용한 가상 사용자 세션
- RLS 정책이 적용된 안전한 데이터 접근
- 실제 인증 없이도 테스트 가능

### ✅ **3. 환경 변수 로딩**
- python-dotenv를 통한 .env 파일 자동 로드
- 환경 변수와 Streamlit secrets 모두 지원
- 상세한 디버깅 정보 제공

## 🎯 **주요 변경사항**

### **Before (Service Role Key)**
```python
# Service Role Key 사용하여 RLS 정책 우회
client = create_client(url, service_key)
```

### **After (Anon Key)**
```python
# Anon Key 사용하여 RLS 정책 적용
client = create_client(url, anon_key)
```

## 🔐 **보안 개선**

### **RLS 정책 적용**
- anon key 사용으로 RLS 정책이 적용됨
- 사용자는 자신의 데이터만 접근 가능
- 개발 모드에서도 보안 정책 준수

### **환경 변수 관리**
- .env 파일을 통한 안전한 키 관리
- Streamlit secrets를 통한 클라우드 배포 지원
- 키가 코드에 하드코딩되지 않음

## 🚀 **개발 모드 특징**

### **가상 사용자 세션**
```python
# 개발 모드에서 가상 사용자 정보 설정
st.session_state.authenticated = True
st.session_state.user = {
    "id": "dev-user-123",
    "email": "dev@example.com"
}
```

### **Anon Key 사용**
```python
# anon key를 사용하여 RLS 정책이 적용된 클라이언트 생성
client = create_client(url, anon_key)
```

### **디버깅 정보**
```
🔍 환경 변수 확인:
  - SUPABASE_URL: 설정됨
  - SUPABASE_ANON_KEY: 설정됨
✅ 환경 변수에서 Supabase 설정 로드됨
✅ Supabase 클라이언트 생성 완료
🔧 개발 모드: anon key 사용, 가상 사용자 세션 설정
✅ 개발 모드: 가상 사용자 세션 설정 완료 (dev-user-123)
```

## 🔧 **환경 설정**

### **방법 1: .env 파일 사용**
프로젝트 루트에 `.env` 파일 생성:
```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
DEV_MODE=true
```

### **방법 2: Streamlit secrets 사용**
`.streamlit/secrets.toml` 파일에 추가:
```toml
[supabase]
url = "your_supabase_url_here"
anon_key = "your_supabase_anon_key_here"

dev_mode = true
```

### **방법 3: 환경 변수 직접 설정**
```bash
# Windows
set SUPABASE_URL=your_supabase_url_here
set SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Linux/Mac
export SUPABASE_URL=your_supabase_url_here
export SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

## 🎯 **사이드바 표시**

### **개발 모드 활성화 시**
```
🔧 개발 모드
dev@example.com
```

또는

```
🔧 개발 모드
Anon Key + 가상 사용자
```

## ✅ **현재 작동하는 기능**

- ✅ **Anon Key 사용**: SUPABASE_ANON_KEY를 통한 안전한 접근
- ✅ **RLS 정책 적용**: 모든 데이터베이스 작업에 보안 정책 적용
- ✅ **환경 변수 로딩**: .env 파일과 Streamlit secrets 지원
- ✅ **개발 모드**: 가상 사용자로 테스트 가능
- ✅ **캠페인 관리**: RLS 정책이 적용된 캠페인 CRUD 작업
- ✅ **인플루언서 관리**: RLS 정책이 적용된 인플루언서 CRUD 작업

## 🔍 **디버깅 정보**

애플리케이션 실행 시 콘솔에서 다음 정보를 확인할 수 있습니다:

```
✅ .env 파일 로드됨
🔍 환경 변수 확인:
  - SUPABASE_URL: 설정됨
  - SUPABASE_ANON_KEY: 설정됨
✅ 환경 변수에서 Supabase 설정 로드됨
✅ Supabase 클라이언트 생성 완료
🔧 개발 모드: anon key 사용, 가상 사용자 세션 설정
✅ 개발 모드: 가상 사용자 세션 설정 완료 (dev-user-123)
```

## ⚠️ **주의사항**

### **보안**
- anon key는 공개되어도 안전하지만, RLS 정책이 적용됨
- Service Role Key는 절대 공개하지 말 것
- .env 파일은 .gitignore에 포함되어야 함

### **RLS 정책**
- anon key 사용 시 RLS 정책이 자동으로 적용됨
- 사용자는 자신의 데이터만 접근 가능
- 개발 모드에서도 보안 정책 준수

## 🎉 **결과**

이제 **Supabase anon key를 사용한 안전한 데이터 접근**이 가능합니다!

### **보안 강화**
- anon key 사용으로 RLS 정책 적용
- 환경 변수를 통한 안전한 키 관리
- 개발 모드에서도 보안 정책 준수

### **사용 방법**
1. `.env` 파일에 Supabase 설정 추가
2. `streamlit run app.py` 실행
3. 자동으로 anon key를 사용한 클라이언트 생성
4. RLS 정책이 적용된 안전한 데이터 접근

Supabase anon key를 사용한 안전하고 효율적인 개발 환경이 준비되었습니다! 🔐

