# Streamlit 버전 호환성 가이드

## 문제 상황
`module 'streamlit' has no attribute 'tag'` 오류가 발생하는 경우가 있습니다.

## 원인
- Streamlit 버전에 따라 `st.tag`와 `st.badge` 함수의 지원 여부가 다름
- `st.tag`: Streamlit 1.24+ 버전에서 지원
- `st.badge`: Streamlit 1.28+ 버전에서 지원

## 해결 방법

### 1. Streamlit 버전 업그레이드
```bash
pip install streamlit>=1.28.0
```

### 2. 호환성 유틸리티 사용
`src/ui/streamlit_utils.py`에서 제공하는 호환성 함수들을 사용하세요:

```python
from src.ui.streamlit_utils import display_tags, safe_tag, safe_badge

# 태그 표시
display_tags(['태그1', '태그2', '태그3'])

# 개별 태그/배지 표시
safe_tag("태그")
safe_badge("배지")
```

### 3. 수동 호환성 처리
```python
def safe_tag(text):
    try:
        return st.badge(text)
    except AttributeError:
        try:
            return st.tag(text)
        except AttributeError:
            return st.markdown(f"🏷️ `{text}`")
```

## 지원되는 Streamlit 버전
- **최소 버전**: 1.28.0 (st.badge 지원)
- **권장 버전**: 1.39.0 이상
- **최신 버전**: 1.40.0 이상

## 버전 확인 방법
```python
import streamlit as st
print(f"Streamlit 버전: {st.__version__}")
```

## 주의사항
- 구버전 Streamlit에서는 일부 UI 컴포넌트가 지원되지 않을 수 있습니다
- 프로덕션 환경에서는 안정적인 버전 사용을 권장합니다
- 새로운 기능 사용 전 버전 호환성을 확인하세요

## 문제 해결 체크리스트
1. ✅ Streamlit 버전 확인
2. ✅ requirements.txt 업데이트
3. ✅ 호환성 유틸리티 함수 사용
4. ✅ 오류 처리 로직 추가
5. ✅ 테스트 환경에서 검증
