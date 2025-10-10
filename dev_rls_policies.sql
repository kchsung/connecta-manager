-- 개발 모드용 RLS 정책 설정
-- anon key로도 데이터에 접근할 수 있도록 수정

-- 기존 정책 삭제 (있는 경우)
DROP POLICY IF EXISTS "Users can view own campaigns" ON campaigns;
DROP POLICY IF EXISTS "Users can insert own campaigns" ON campaigns;
DROP POLICY IF EXISTS "Users can update own campaigns" ON campaigns;
DROP POLICY IF EXISTS "Users can delete own campaigns" ON campaigns;

DROP POLICY IF EXISTS "Users can view own participations" ON campaign_influencer_participations;
DROP POLICY IF EXISTS "Users can insert own participations" ON campaign_influencer_participations;
DROP POLICY IF EXISTS "Users can update own participations" ON campaign_influencer_participations;
DROP POLICY IF EXISTS "Users can delete own participations" ON campaign_influencer_participations;

DROP POLICY IF EXISTS "Users can view own contents" ON campaign_influencer_contents;
DROP POLICY IF EXISTS "Users can insert own contents" ON campaign_influencer_contents;
DROP POLICY IF EXISTS "Users can update own contents" ON campaign_influencer_contents;
DROP POLICY IF EXISTS "Users can delete own contents" ON campaign_influencer_contents;

DROP POLICY IF EXISTS "Anyone can view influencers" ON connecta_influencers;
DROP POLICY IF EXISTS "Users can insert own influencers" ON connecta_influencers;
DROP POLICY IF EXISTS "Users can update own influencers" ON connecta_influencers;
DROP POLICY IF EXISTS "Users can delete own influencers" ON connecta_influencers;

DROP POLICY IF EXISTS "Users can view own crawl data" ON connecta_influencer_crawl_raw;
DROP POLICY IF EXISTS "Users can insert own crawl data" ON connecta_influencer_crawl_raw;
DROP POLICY IF EXISTS "Users can update own crawl data" ON connecta_influencer_crawl_raw;
DROP POLICY IF EXISTS "Users can delete own crawl data" ON connecta_influencer_crawl_raw;

-- campaigns 테이블 정책 (개발 모드: 모든 사용자 접근 허용)
CREATE POLICY "Dev mode: Anyone can access campaigns" ON campaigns
    FOR ALL USING (true);

-- campaign_influencer_participations 테이블 정책 (개발 모드: 모든 사용자 접근 허용)
CREATE POLICY "Dev mode: Anyone can access participations" ON campaign_influencer_participations
    FOR ALL USING (true);

-- campaign_influencer_contents 테이블 정책 (개발 모드: 모든 사용자 접근 허용)
CREATE POLICY "Dev mode: Anyone can access contents" ON campaign_influencer_contents
    FOR ALL USING (true);

-- connecta_influencers 테이블 정책 (개발 모드: 모든 사용자 접근 허용)
CREATE POLICY "Dev mode: Anyone can access influencers" ON connecta_influencers
    FOR ALL USING (true);

-- connecta_influencer_crawl_raw 테이블 정책 (개발 모드: 모든 사용자 접근 허용)
CREATE POLICY "Dev mode: Anyone can access crawl data" ON connecta_influencer_crawl_raw
    FOR ALL USING (true);

