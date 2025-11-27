-- ============================================================================
-- 캠페인 분석 결과 테이블
-- ============================================================================

-- 캠페인 분석 결과 저장 테이블
CREATE TABLE IF NOT EXISTS public.campaign_analyses (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL,
  analysis_result JSONB NOT NULL,
  analyzed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_by UUID NULL DEFAULT auth.uid(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  
  CONSTRAINT campaign_analyses_pkey PRIMARY KEY (id),
  CONSTRAINT campaign_analyses_campaign_id_fkey 
    FOREIGN KEY (campaign_id) 
    REFERENCES public.campaigns(id) 
    ON DELETE CASCADE,
  
  -- 캠페인당 하나의 분석 결과만 유지 (최신 것만)
  CONSTRAINT campaign_analyses_campaign_id_unique UNIQUE (campaign_id)
) TABLESPACE pg_default;

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS campaign_analyses_campaign_id_idx 
  ON public.campaign_analyses USING btree (campaign_id) 
  TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS campaign_analyses_analyzed_at_idx 
  ON public.campaign_analyses USING btree (analyzed_at DESC) 
  TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS campaign_analyses_created_by_idx 
  ON public.campaign_analyses USING btree (created_by) 
  TABLESPACE pg_default;

-- JSONB 필드에 대한 GIN 인덱스 (검색 최적화)
CREATE INDEX IF NOT EXISTS campaign_analyses_analysis_result_gin_idx 
  ON public.campaign_analyses USING gin (analysis_result) 
  TABLESPACE pg_default;

-- updated_at 자동 업데이트 트리거
CREATE TRIGGER set_timestamp_campaign_analyses 
  BEFORE UPDATE ON public.campaign_analyses 
  FOR EACH ROW 
  EXECUTE FUNCTION trigger_set_timestamp();

-- ============================================================================
-- Row Level Security (RLS) 정책
-- ============================================================================

-- RLS 활성화
ALTER TABLE public.campaign_analyses ENABLE ROW LEVEL SECURITY;

-- 정책: 사용자는 자신이 생성한 분석 결과만 조회 가능
CREATE POLICY "Users can view their own campaign analyses"
  ON public.campaign_analyses
  FOR SELECT
  USING (auth.uid() = created_by);

-- 정책: 사용자는 자신의 캠페인에 대한 분석 결과를 생성 가능
CREATE POLICY "Users can create campaign analyses for their campaigns"
  ON public.campaign_analyses
  FOR INSERT
  WITH CHECK (
    auth.uid() = created_by 
    AND EXISTS (
      SELECT 1 FROM public.campaigns 
      WHERE campaigns.id = campaign_analyses.campaign_id 
      AND campaigns.created_by = auth.uid()
    )
  );

-- 정책: 사용자는 자신이 생성한 분석 결과만 업데이트 가능
CREATE POLICY "Users can update their own campaign analyses"
  ON public.campaign_analyses
  FOR UPDATE
  USING (auth.uid() = created_by)
  WITH CHECK (auth.uid() = created_by);

-- 정책: 사용자는 자신이 생성한 분석 결과만 삭제 가능
CREATE POLICY "Users can delete their own campaign analyses"
  ON public.campaign_analyses
  FOR DELETE
  USING (auth.uid() = created_by);

-- ============================================================================
-- 코멘트
-- ============================================================================

COMMENT ON TABLE public.campaign_analyses IS '캠페인 분석 결과를 저장하는 테이블';
COMMENT ON COLUMN public.campaign_analyses.id IS '분석 결과 고유 ID';
COMMENT ON COLUMN public.campaign_analyses.campaign_id IS '캠페인 ID (campaigns 테이블 참조)';
COMMENT ON COLUMN public.campaign_analyses.analysis_result IS 'AI 분석 결과 (JSON 형식)';
COMMENT ON COLUMN public.campaign_analyses.analyzed_at IS '분석 수행 일시';
COMMENT ON COLUMN public.campaign_analyses.created_by IS '분석 결과 생성자 (auth.uid())';
COMMENT ON COLUMN public.campaign_analyses.created_at IS '레코드 생성 일시';
COMMENT ON COLUMN public.campaign_analyses.updated_at IS '레코드 수정 일시';



