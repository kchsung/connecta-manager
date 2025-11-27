-- ============================================================================
-- 캠페인 분석 결과 테이블 RLS 정책
-- ============================================================================

-- RLS 활성화 (이미 활성화되어 있으면 무시됨)
ALTER TABLE public.campaign_analyses ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 (있는 경우)
DROP POLICY IF EXISTS "Users can view their own campaign analyses" ON public.campaign_analyses;
DROP POLICY IF EXISTS "Users can create campaign analyses for their campaigns" ON public.campaign_analyses;
DROP POLICY IF EXISTS "Users can update their own campaign analyses" ON public.campaign_analyses;
DROP POLICY IF EXISTS "Users can delete their own campaign analyses" ON public.campaign_analyses;

-- 정책: 사용자는 자신이 생성한 분석 결과만 조회 가능
CREATE POLICY "Users can view their own campaign analyses"
  ON public.campaign_analyses
  FOR SELECT
  USING (
    -- created_by가 null이면 모든 사용자가 조회 가능 (인증되지 않은 경우)
    created_by IS NULL 
    OR auth.uid() = created_by
    -- 또는 자신의 캠페인에 대한 분석 결과 조회 가능
    OR EXISTS (
      SELECT 1 FROM public.campaigns 
      WHERE campaigns.id = campaign_analyses.campaign_id 
      AND (campaigns.created_by IS NULL OR campaigns.created_by = auth.uid())
    )
  );

-- 정책: 사용자는 자신의 캠페인에 대한 분석 결과를 생성 가능
CREATE POLICY "Users can create campaign analyses for their campaigns"
  ON public.campaign_analyses
  FOR INSERT
  WITH CHECK (
    -- created_by가 null이거나 자신의 ID와 일치
    (created_by IS NULL OR auth.uid() = created_by)
    -- 그리고 자신의 캠페인에 대한 것만
    AND EXISTS (
      SELECT 1 FROM public.campaigns 
      WHERE campaigns.id = campaign_analyses.campaign_id 
      AND (campaigns.created_by IS NULL OR campaigns.created_by = auth.uid())
    )
  );

-- 정책: 사용자는 자신이 생성한 분석 결과만 업데이트 가능
CREATE POLICY "Users can update their own campaign analyses"
  ON public.campaign_analyses
  FOR UPDATE
  USING (
    -- created_by가 null이거나 자신의 ID와 일치
    created_by IS NULL 
    OR auth.uid() = created_by
    -- 또는 자신의 캠페인에 대한 분석 결과
    OR EXISTS (
      SELECT 1 FROM public.campaigns 
      WHERE campaigns.id = campaign_analyses.campaign_id 
      AND (campaigns.created_by IS NULL OR campaigns.created_by = auth.uid())
    )
  )
  WITH CHECK (
    created_by IS NULL 
    OR auth.uid() = created_by
  );

-- 정책: 사용자는 자신이 생성한 분석 결과만 삭제 가능
CREATE POLICY "Users can delete their own campaign analyses"
  ON public.campaign_analyses
  FOR DELETE
  USING (
    created_by IS NULL 
    OR auth.uid() = created_by
    OR EXISTS (
      SELECT 1 FROM public.campaigns 
      WHERE campaigns.id = campaign_analyses.campaign_id 
      AND (campaigns.created_by IS NULL OR campaigns.created_by = auth.uid())
    )
  );



