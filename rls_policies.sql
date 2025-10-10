-- RLS 정책 설정 SQL
-- 기존 테이블들에 대한 RLS 정책 추가

-- connecta_influencers 테이블 RLS 활성화 및 정책 설정
ALTER TABLE connecta_influencers ENABLE ROW LEVEL SECURITY;

-- connecta_influencers 정책 (모든 사용자가 읽기 가능, 소유자만 수정 가능)
CREATE POLICY "Anyone can view influencers" ON connecta_influencers
    FOR SELECT USING (true);

CREATE POLICY "Users can insert own influencers" ON connecta_influencers
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own influencers" ON connecta_influencers
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own influencers" ON connecta_influencers
    FOR DELETE USING (auth.uid() = user_id);

-- connecta_influencer_crawl_raw 테이블 RLS 활성화 및 정책 설정
ALTER TABLE connecta_influencer_crawl_raw ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own crawl data" ON connecta_influencer_crawl_raw
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own crawl data" ON connecta_influencer_crawl_raw
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own crawl data" ON connecta_influencer_crawl_raw
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own crawl data" ON connecta_influencer_crawl_raw
    FOR DELETE USING (auth.uid() = user_id);

-- campaigns 테이블 RLS 활성화 및 정책 설정 (이미 있다면 무시)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'campaigns' AND policyname = 'Users can view own campaigns') THEN
        ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view own campaigns" ON campaigns
            FOR SELECT USING (auth.uid() = created_by);
        
        CREATE POLICY "Users can insert own campaigns" ON campaigns
            FOR INSERT WITH CHECK (auth.uid() = created_by);
        
        CREATE POLICY "Users can update own campaigns" ON campaigns
            FOR UPDATE USING (auth.uid() = created_by);
        
        CREATE POLICY "Users can delete own campaigns" ON campaigns
            FOR DELETE USING (auth.uid() = created_by);
    END IF;
END $$;

-- campaign_influencer_participations 테이블 RLS 정책 (이미 있다면 무시)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'campaign_influencer_participations' AND policyname = 'Users can view own participations') THEN
        ALTER TABLE campaign_influencer_participations ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view own participations" ON campaign_influencer_participations
            FOR SELECT USING (auth.uid() = (SELECT created_by FROM campaigns WHERE id = campaign_id));
        
        CREATE POLICY "Users can insert own participations" ON campaign_influencer_participations
            FOR INSERT WITH CHECK (auth.uid() = (SELECT created_by FROM campaigns WHERE id = campaign_id));
        
        CREATE POLICY "Users can update own participations" ON campaign_influencer_participations
            FOR UPDATE USING (auth.uid() = (SELECT created_by FROM campaigns WHERE id = campaign_id));
        
        CREATE POLICY "Users can delete own participations" ON campaign_influencer_participations
            FOR DELETE USING (auth.uid() = (SELECT created_by FROM campaigns WHERE id = campaign_id));
    END IF;
END $$;

-- campaign_influencer_contents 테이블 RLS 정책 (이미 있다면 무시)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'campaign_influencer_contents' AND policyname = 'Users can view own contents') THEN
        ALTER TABLE campaign_influencer_contents ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view own contents" ON campaign_influencer_contents
            FOR SELECT USING (auth.uid() = (SELECT created_by FROM campaigns WHERE id = (SELECT campaign_id FROM campaign_influencer_participations WHERE id = participation_id)));
        
        CREATE POLICY "Users can insert own contents" ON campaign_influencer_contents
            FOR INSERT WITH CHECK (auth.uid() = (SELECT created_by FROM campaigns WHERE id = (SELECT campaign_id FROM campaign_influencer_participations WHERE id = participation_id)));
        
        CREATE POLICY "Users can update own contents" ON campaign_influencer_contents
            FOR UPDATE USING (auth.uid() = (SELECT created_by FROM campaigns WHERE id = (SELECT campaign_id FROM campaign_influencer_participations WHERE id = participation_id)));
        
        CREATE POLICY "Users can delete own contents" ON campaign_influencer_contents
            FOR DELETE USING (auth.uid() = (SELECT created_by FROM campaigns WHERE id = (SELECT campaign_id FROM campaign_influencer_participations WHERE id = participation_id)));
    END IF;
END $$;

-- user_id 컬럼이 없는 테이블들에 user_id 컬럼 추가 (필요한 경우)
DO $$ 
BEGIN
    -- connecta_influencers 테이블에 user_id 컬럼이 없다면 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'connecta_influencers' AND column_name = 'user_id') THEN
        ALTER TABLE connecta_influencers ADD COLUMN user_id UUID REFERENCES auth.users(id);
        
        -- 기존 데이터에 대해 기본 사용자 ID 설정 (필요시 수정)
        -- UPDATE connecta_influencers SET user_id = (SELECT id FROM auth.users LIMIT 1) WHERE user_id IS NULL;
    END IF;
    
    -- connecta_influencer_crawl_raw 테이블에 user_id 컬럼이 없다면 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'connecta_influencer_crawl_raw' AND column_name = 'user_id') THEN
        ALTER TABLE connecta_influencer_crawl_raw ADD COLUMN user_id UUID REFERENCES auth.users(id);
    END IF;
END $$;

