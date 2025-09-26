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
    id: Optional[str] = None
    created_by: Optional[str] = None
    campaign_name: str
    campaign_description: Optional[str] = None
    campaign_type: str  # seeding, promotion, sales
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "planned"  # planned, active, paused, completed, canceled
    campaign_instructions: Optional[str] = None  # 캠페인 지시사항
    tags: Optional[str] = None  # 관련 Tag정보(쉼표로 구분된 문자열)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Influencer(BaseModel):
    """인플루언서 데이터 모델"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    platform: str  # instagram, youtube, tiktok, twitter
    sns_id: str
    sns_url: str
    influencer_name: str
    owner_comment: Optional[str] = None
    content_category: str = "일반"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
    metric_type: str  # likes, comments, shares, views, clicks, conversions
    metric_value: int = 0
    qualitative_evaluation: Optional[str] = None  # 정성평가 (매우 좋음, 좋음, 보통, 나쁨, 매우 나쁨)
    measurement_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None