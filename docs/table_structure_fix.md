# 테이블 구조 불일치 문제 해결

## 문제 상황
- 테이블 정의에는 `recommendation` 컬럼이 있지만, 실제 데이터베이스에는 해당 컬럼이 존재하지 않음
- `ERROR: 42703: column "recommendation" of relation "ai_influencer_analyses" does not exist` 오류 발생

## 해결 방법

### 1. 코드 수정 완료
- `src/ui/ai_analysis_results.py`: recommendation 필터 비활성화
- `src/ui/ai_analysis_common.py`: recommendation 필드 제거
- `src/ui/ai_analysis_statistics.py`: recommendation 분포 조회 비활성화

### 2. 수정된 기능들

#### **AI 분석 결과 조회**
- ✅ 추천도 필터 비활성화 (사용자에게 안내 메시지 표시)
- ✅ 기본 정보에서 추천도 필드 제거
- ✅ expander 제목에서 추천도 제거

#### **AI 분석 공통 함수**
- ✅ 데이터베이스 저장 시 recommendation 필드 제거
- ✅ 디버깅 정보에서 recommendation 제거

#### **AI 분석 통계**
- ✅ 추천도 분포 조회 비활성화
- ✅ 사용자에게 안내 메시지 표시

### 3. 현재 작동하는 기능들
- ✅ 기본 분석 결과 조회
- ✅ 카테고리 필터링
- ✅ 검색 기능
- ✅ 페이징
- ✅ 상세 분석 결과 표시
- ✅ 통계 기능 (추천도 제외)

### 4. 비활성화된 기능들
- ❌ 추천도 필터링
- ❌ 추천도 분포 통계
- ❌ 추천도 기반 정렬

### 5. 향후 해결 방안

#### **옵션 1: 테이블에 recommendation 컬럼 추가**
```sql
-- Supabase SQL Editor에서 실행
ALTER TABLE ai_influencer_analyses 
ADD COLUMN recommendation text DEFAULT '보통';

-- 또는 enum 타입으로 추가
CREATE TYPE recommendation_ko AS ENUM ('매우 추천', '추천', '보통', '비추천', '매우 비추천', '조건부');
ALTER TABLE ai_influencer_analyses 
ADD COLUMN recommendation recommendation_ko DEFAULT '보통';
```

#### **옵션 2: evaluation JSON에서 추천도 추출**
```python
# evaluation JSON에서 추천도 정보를 추출하여 사용
recommendation = evaluation.get("recommendation", "보통")
```

### 6. 테스트 방법
1. AI 분석 결과 조회 기능 테스트
2. 카테고리 필터링 테스트
3. 검색 기능 테스트
4. 통계 기능 테스트

### 7. 주의사항
- 현재 코드는 recommendation 컬럼이 없는 상황에 맞춰 수정됨
- 테이블에 recommendation 컬럼을 추가하면 코드를 다시 수정해야 함
- AI 분석 시 recommendation 정보는 evaluation JSON에 저장됨
