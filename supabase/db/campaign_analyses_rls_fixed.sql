-- ============================================================================
-- 캠페인 분석 결과 테이블 RLS 정책 (ANON_KEY 사용 시)
-- ============================================================================

-- RLS 활성화 (이미 활성화되어 있으면 무시됨)
ALTER TABLE public.campaign_analyses ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 (있는 경우)
DROP POLICY IF EXISTS "Users can view their own campaign analyses" ON public.campaign_analyses;
DROP POLICY IF EXISTS "Users can create campaign analyses for their campaigns" ON public.campaign_analyses;
DROP POLICY IF EXISTS "Users can update their own campaign analyses" ON public.campaign_analyses;
DROP POLICY IF EXISTS "Users can delete their own campaign analyses" ON public.campaign_analyses;
DROP POLICY IF EXISTS "Allow authenticated users to manage campaign analyses" ON public.campaign_analyses;

-- 정책: 인증된 사용자는 자신의 캠페인에 대한 분석 결과를 조회/생성/수정/삭제 가능
-- Edge Function에서 ANON_KEY를 사용하므로, 캠페인의 created_by와 일치하면 접근 허용
CREATE POLICY "Allow authenticated users to manage campaign analyses"
  ON public.campaign_analyses
  FOR ALL
  USING (
    -- 캠페인의 소유자이면 접근 가능
    EXISTS (
      SELECT 1 FROM public.campaigns 
      WHERE campaigns.id = campaign_analyses.campaign_id 
      AND (
        campaigns.created_by IS NULL 
        OR campaigns.created_by = auth.uid()
        OR auth.uid() IS NOT NULL  -- 인증된 사용자는 모두 접근 가능 (필요시 제거)
      )
    )
  )
  WITH CHECK (
    -- 캠페인의 소유자이면 접근 가능
    EXISTS (
      SELECT 1 FROM public.campaigns 
      WHERE campaigns.id = campaign_analyses.campaign_id 
      AND (
        campaigns.created_by IS NULL 
        OR campaigns.created_by = auth.uid()
        OR auth.uid() IS NOT NULL  -- 인증된 사용자는 모두 접근 가능 (필요시 제거)
      )
    )
  );



