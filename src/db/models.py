from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

# 크롤링 관련 모델들이 제거되었습니다.

class UserStats(BaseModel):
    """사용자 통계 데이터 모델"""
    user_id: str
    email: str
    total_sessions: int = 0
    total_posts: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    total_likes: int = 0
    total_comments: int = 0
    last_crawl_date: Optional[datetime] = None

class Campaign(BaseModel):
    """캠페인 데이터 모델"""
    # id 필드는 제거 - 데이터베이스에서 자동으로 생성됨
    # created_by 필드는 제거 - 데이터베이스에서 자동으로 설정됨
    campaign_name: str
    campaign_description: Optional[str] = None
    campaign_type: str  # seeding, promotion, sales
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "planned"  # planned, active, paused, completed, cancelled
    campaign_instructions: Optional[str] = None  # 캠페인 지시사항
    tags: Optional[str] = None  # 관련 Tag정보(쉼표로 구분된 문자열)
    # created_at, updated_at 필드는 제거 - 데이터베이스에서 자동으로 설정됨
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class Influencer(BaseModel):
    """인플루언서 데이터 모델"""
    # id 필드는 제거 - 데이터베이스에서 자동으로 생성됨
    platform: str  # instagram, youtube, tiktok, twitter
    content_category: str
    influencer_name: Optional[str] = ""
    sns_id: str
    sns_url: str
    contact_method: Optional[str] = "dm"  # dm, email, phone, kakao, form, other
    contacts_method_etc: Optional[str] = None  # 연락방법이 'other'일 때 추가 정보
    followers_count: Optional[int] = 0
    phone_number: Optional[str] = None
    kakao_channel_id: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[str] = None
    interested_products: Optional[str] = None
    owner_comment: Optional[str] = None
    manager_rating: Optional[int] = None  # 1-5
    content_rating: Optional[int] = None  # 1-5
    comments_count: Optional[int] = 0
    foreign_followers_ratio: Optional[float] = None  # 0-100
    activity_score: Optional[float] = None
    preferred_mode: Optional[str] = None  # influencer_pref enum
    price_krw: Optional[float] = None
    tags: Optional[str] = None  # text field
    created_by: Optional[str] = None  # 등록자 정보
    # created_at, updated_at 필드는 제거 - 데이터베이스에서 자동으로 설정됨
    active: Optional[bool] = True
    post_count: Optional[int] = 0
    profile_text: Optional[str] = None
    profile_image_url: Optional[str] = None
    first_crawled: Optional[bool] = False
    dm_reply: Optional[str] = None

class CampaignInfluencer(BaseModel):
    """캠페인-인플루언서 연결 데이터 모델"""
    id: Optional[str] = None
    campaign_id: str
    influencer_id: str
    status: str = "assigned"  # assigned, in_progress, completed, cancelled
    final_output_url: Optional[str] = None
    notes: Optional[str] = None
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CampaignInfluencerParticipation(BaseModel):
    """캠페인 인플루언서 참여 데이터 모델"""
    id: Optional[str] = None
    campaign_id: str
    influencer_id: str
    manager_comment: Optional[str] = None
    influencer_requests: Optional[str] = None
    memo: Optional[str] = None
    sample_status: str = "요청"  # 요청, 발송준비, 발송완료, 수령
    influencer_feedback: Optional[str] = None
    content_uploaded: bool = False
    cost_krw: float = 0.0
    content_links: List[str] = []
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PerformanceMetric(BaseModel):
    """성과 지표 데이터 모델"""
    id: Optional[str] = None
    participation_id: str  # campaign_influencer_participations 테이블의 id
    content_link: Optional[str] = None  # 컨텐츠별 성과 입력을 위한 링크
    metric_type: str  # likes, comments, is_rels, views, clicks, conversions
    metric_value: int = 0
    qualitative_evaluation: Optional[str] = None  # 정성평가 (매우 좋음, 좋음, 보통, 나쁨, 매우 나쁨)
    measurement_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None