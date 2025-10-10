// 캠페인 타입 정의
export interface Campaign {
  id?: string
  campaign_name: string
  campaign_description?: string
  campaign_type: 'seeding' | 'promotion' | 'sales'
  start_date: string
  end_date?: string
  status: 'planned' | 'active' | 'paused' | 'completed' | 'cancelled'
  campaign_instructions?: string
  tags?: string
  created_by?: string
  created_at?: string
  updated_at?: string
}

// 인플루언서 타입 정의
export interface Influencer {
  id?: string
  platform: 'instagram' | 'youtube' | 'tiktok' | 'twitter'
  content_category: string
  influencer_name?: string
  sns_id: string
  sns_url: string
  contact_method: 'dm' | 'email' | 'phone' | 'kakao'
  followers_count?: number
  phone_number?: string
  kakao_channel_id?: string
  email?: string
  shipping_address?: string
  interested_products?: string
  owner_comment?: string
  manager_rating?: number
  content_rating?: number
  comments_count?: number
  foreign_followers_ratio?: number
  activity_score?: number
  preferred_mode?: 'seeding' | 'promotion' | 'sales'
  price_krw?: number
  tags?: string
  created_by?: string
  created_at?: string
  updated_at?: string
  active?: boolean
  post_count?: number
  profile_text?: string
  profile_image_url?: string
  first_crawled?: boolean
}

// 캠페인 참여 타입 정의
export interface CampaignParticipation {
  id?: string
  campaign_id: string
  influencer_id: string
  manager_comment?: string
  influencer_requests?: string
  memo?: string
  sample_status: '요청' | '발송' | '수령' | '완료' | '취소'
  influencer_feedback?: string
  content_uploaded?: boolean
  cost_krw?: number
  content_links?: string[]
  created_by?: string
  created_at?: string
  updated_at?: string
}

// 콘텐츠 성과 타입 정의
export interface CampaignContent {
  id?: string
  participation_id: string
  content_url: string
  posted_at?: string
  caption?: string
  qualitative_note?: string
  likes?: number
  comments?: number
  shares?: number
  views?: number
  clicks?: number
  conversions?: number
  created_by?: string
  created_at?: string
  updated_at?: string
}

// API 응답 타입 정의
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

