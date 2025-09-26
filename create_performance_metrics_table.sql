-- performance_metrics 테이블 생성 및 업데이트
-- 성과 관리 기능을 위한 완전한 테이블 스키마

-- 1) 기존 테이블이 있다면 삭제 (개발용 - 주의!)
-- DROP TABLE IF EXISTS public.performance_metrics CASCADE;

-- 2) performance_metrics 테이블 생성
CREATE TABLE IF NOT EXISTS public.performance_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE,
    influencer_id UUID REFERENCES public.connecta_influencers(id) ON DELETE CASCADE,
    content_link TEXT,  -- 컨텐츠별 성과 입력을 위한 링크
    metric_type TEXT NOT NULL CHECK (metric_type IN ('likes', 'comments', 'shares', 'views', 'clicks', 'conversions')),
    metric_value INTEGER DEFAULT 0,
    qualitative_evaluation TEXT CHECK (qualitative_evaluation IN ('매우 좋음', '좋음', '보통', '나쁨', '매우 나쁨') OR qualitative_evaluation IS NULL),
    measurement_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3) 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_performance_metrics_campaign_id ON public.performance_metrics(campaign_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_influencer_id ON public.performance_metrics(influencer_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_content_link ON public.performance_metrics(content_link);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_qualitative_evaluation ON public.performance_metrics(qualitative_evaluation);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_measurement_date ON public.performance_metrics(measurement_date);

-- 4) RLS (Row Level Security) 정책 설정
ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;

-- 성과 지표 정책 (모든 사용자가 접근 가능하도록 설정)
CREATE POLICY "Anyone can view performance metrics" ON public.performance_metrics
    FOR SELECT USING (true);

CREATE POLICY "Anyone can insert performance metrics" ON public.performance_metrics
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can update performance metrics" ON public.performance_metrics
    FOR UPDATE USING (true);

CREATE POLICY "Anyone can delete performance metrics" ON public.performance_metrics
    FOR DELETE USING (true);

-- 5) 업데이트 시간 트리거
CREATE TRIGGER update_performance_metrics_updated_at
    BEFORE UPDATE ON public.performance_metrics
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
