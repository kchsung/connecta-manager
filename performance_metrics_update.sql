-- performance_metrics 테이블에 content_link와 qualitative_evaluation 필드 추가
-- 성과 관리 기능 개선을 위한 스키마 업데이트

-- 1) content_link 필드 추가 (컨텐츠별 성과 입력을 위한 링크)
ALTER TABLE public.performance_metrics 
ADD COLUMN IF NOT EXISTS content_link TEXT;

-- 2) qualitative_evaluation 필드 추가 (정성평가)
ALTER TABLE public.performance_metrics 
ADD COLUMN IF NOT EXISTS qualitative_evaluation TEXT 
CHECK (qualitative_evaluation IN ('매우 좋음', '좋음', '보통', '나쁨', '매우 나쁨') OR qualitative_evaluation IS NULL);

-- 3) content_link 인덱스 추가 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_performance_metrics_content_link 
ON public.performance_metrics(content_link);

-- 4) qualitative_evaluation 인덱스 추가 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_performance_metrics_qualitative_evaluation 
ON public.performance_metrics(qualitative_evaluation);
