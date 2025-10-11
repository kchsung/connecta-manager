-- ============================================================================
-- ENUM 타입 정의
-- ============================================================================

-- 플랫폼 타입
CREATE TYPE platform_type AS ENUM ('instagram', 'youtube', 'tiktok', 'twitter');

-- 캠페인 타입
CREATE TYPE campaign_type AS ENUM ('seeding', 'promotion', 'sales');

-- 캠페인 상태
CREATE TYPE campaign_status AS ENUM ('planned', 'active', 'paused', 'completed', 'cancelled');

-- 연락 방법
CREATE TYPE contact_method AS ENUM ('dm', 'email', 'phone', 'kakao', 'form', 'other');

-- 샘플 상태
CREATE TYPE sample_status AS ENUM ('요청', '발송준비', '발송완료', '수령');
