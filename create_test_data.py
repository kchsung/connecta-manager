#!/usr/bin/env python3
"""
테스트 데이터 생성 스크립트
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
try:
    load_dotenv()
    print("[OK] .env 파일 로드됨")
except Exception as e:
    print(f"[WARNING] .env 파일 로드 실패: {e}")

# 환경 변수 확인
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_anon_key:
    print("[ERROR] 환경 변수가 설정되지 않았습니다.")
    exit(1)

try:
    from supabase import create_client, Client
    
    print("[INFO] Supabase 클라이언트 생성...")
    client = create_client(supabase_url, supabase_anon_key)
    print("[OK] 클라이언트 생성 성공")
    
    # 테스트 데이터 생성
    print("\n[INFO] 테스트 데이터 생성 시작...")
    
    # 1. 캠페인 데이터 생성
    print("\n[INFO] 캠페인 데이터 생성...")
    campaign_data = {
        "campaign_name": "테스트 캠페인 1",
        "campaign_description": "개발 테스트용 캠페인입니다.",
        "campaign_type": "brand_awareness",  # 스키마에서 확인된 값 사용
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "status": "planned",  # 스키마에서 확인된 기본값 사용
        "campaign_instructions": "테스트용 캠페인 지시사항",
        "tags": "테스트,개발"
    }
    
    try:
        response = client.table("campaigns").insert(campaign_data).execute()
        if response.data:
            campaign_id = response.data[0]["id"]
            print(f"[OK] 캠페인 생성 성공: {campaign_id}")
        else:
            print("[ERROR] 캠페인 생성 실패")
            campaign_id = None
    except Exception as e:
        print(f"[ERROR] 캠페인 생성 실패: {e}")
        campaign_id = None
    
    # 2. 인플루언서 데이터 생성
    print("\n[INFO] 인플루언서 데이터 생성...")
    influencer_data = {
        "platform": "instagram",
        "content_category": "뷰티",
        "influencer_name": "테스트 인플루언서",
        "sns_id": "test_influencer_001",
        "sns_url": "https://instagram.com/test_influencer_001",
        "contact_method": "dm",
        "followers_count": 10000,
        "phone_number": "010-1234-5678",
        "email": "test@example.com",
        "shipping_address": "서울시 강남구 테헤란로 123, 456호",
        "owner_comment": "테스트용 인플루언서",
        "manager_rating": 4,
        "content_rating": 5,
        "comments_count": 100,
        "foreign_followers_ratio": 20.5,
        "activity_score": 85.0,
        "preferred_mode": "brand_awareness",  # 스키마에서 확인된 값 사용
        "price_krw": 500000,
        "tags": "뷰티,테스트",
        "active": True,
        "post_count": 50,
        "profile_text": "뷰티 전문 인플루언서입니다.",
        "profile_image_url": "https://example.com/profile.jpg",
        "first_crawled": True
    }
    
    try:
        response = client.table("connecta_influencers").insert(influencer_data).execute()
        if response.data:
            influencer_id = response.data[0]["id"]
            print(f"[OK] 인플루언서 생성 성공: {influencer_id}")
        else:
            print("[ERROR] 인플루언서 생성 실패")
            influencer_id = None
    except Exception as e:
        print(f"[ERROR] 인플루언서 생성 실패: {e}")
        influencer_id = None
    
    # 3. 캠페인 참여 데이터 생성 (캠페인과 인플루언서가 모두 생성된 경우)
    if campaign_id and influencer_id:
        print("\n[INFO] 캠페인 참여 데이터 생성...")
        participation_data = {
            "campaign_id": campaign_id,
            "influencer_id": influencer_id,
            "manager_comment": "테스트용 매니저 코멘트",
            "influencer_requests": "테스트용 인플루언서 요청사항",
            "memo": "테스트용 메모",
            "sample_status": "요청",
            "influencer_feedback": "테스트용 피드백",
            "content_uploaded": False,
            "cost_krw": 300000,
            "content_links": ["https://example.com/content1", "https://example.com/content2"]
        }
        
        try:
            response = client.table("campaign_influencer_participations").insert(participation_data).execute()
            if response.data:
                participation_id = response.data[0]["id"]
                print(f"[OK] 캠페인 참여 생성 성공: {participation_id}")
                
                # 4. 콘텐츠 데이터 생성
                print("\n[INFO] 콘텐츠 데이터 생성...")
                content_data = {
                    "participation_id": participation_id,
                    "content_url": "https://instagram.com/p/test_content_001",
                    "posted_at": "2024-01-15T10:00:00Z",
                    "caption": "테스트용 콘텐츠 캡션입니다.",
                    "qualitative_note": "테스트용 정성적 노트",
                    "likes": 150,
                    "comments": 25,
                    "shares": 10,
                    "views": 5000,
                    "clicks": 100,
                    "conversions": 5
                }
                
                try:
                    response = client.table("campaign_influencer_contents").insert(content_data).execute()
                    if response.data:
                        content_id = response.data[0]["id"]
                        print(f"[OK] 콘텐츠 생성 성공: {content_id}")
                    else:
                        print("[ERROR] 콘텐츠 생성 실패")
                except Exception as e:
                    print(f"[ERROR] 콘텐츠 생성 실패: {e}")
            else:
                print("[ERROR] 캠페인 참여 생성 실패")
        except Exception as e:
            print(f"[ERROR] 캠페인 참여 생성 실패: {e}")
    
    print("\n[INFO] 테스트 데이터 생성 완료!")
    
    # 생성된 데이터 확인
    print("\n[INFO] 생성된 데이터 확인...")
    
    try:
        response = client.table("campaigns").select("*").execute()
        print(f"[OK] 캠페인: {len(response.data)}개")
    except Exception as e:
        print(f"[ERROR] 캠페인 조회 실패: {e}")
    
    try:
        response = client.table("connecta_influencers").select("*").execute()
        print(f"[OK] 인플루언서: {len(response.data)}개")
    except Exception as e:
        print(f"[ERROR] 인플루언서 조회 실패: {e}")
    
    try:
        response = client.table("campaign_influencer_participations").select("*").execute()
        print(f"[OK] 캠페인 참여: {len(response.data)}개")
    except Exception as e:
        print(f"[ERROR] 캠페인 참여 조회 실패: {e}")
    
    try:
        response = client.table("campaign_influencer_contents").select("*").execute()
        print(f"[OK] 콘텐츠: {len(response.data)}개")
    except Exception as e:
        print(f"[ERROR] 콘텐츠 조회 실패: {e}")
        
except Exception as e:
    print(f"[ERROR] 스크립트 실행 실패: {e}")

print("\n" + "="*50)
print("테스트 데이터 생성 완료")
