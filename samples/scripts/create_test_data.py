#!/usr/bin/env python3
"""
테스트 데이터 생성 스크립트
Connecta Manager 프로젝트의 테스트용 데이터를 생성합니다.
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

def generate_influencer_data(count: int = 10) -> List[Dict[str, Any]]:
    """인플루언서 테스트 데이터 생성"""
    platforms = ['instagram', 'youtube', 'tiktok', 'x', 'blog', 'facebook']
    contact_methods = ['dm', 'email', 'phone', 'kakao', 'form', 'other']
    categories = ['뷰티', '패션', '푸드', '여행', '라이프스타일', '테크', '게임', '스포츠']
    
    influencers = []
    for i in range(count):
        platform = random.choice(platforms)
        sns_id = f"test_user_{i+1:03d}"
        
        influencer = {
            "platform": platform,
            "content_category": random.choice(categories),
            "influencer_name": f"테스트 인플루언서 {i+1}",
            "sns_id": sns_id,
            "sns_url": f"https://{platform}.com/{sns_id}",
            "contact_method": random.choice(contact_methods),
            "followers_count": random.randint(1000, 1000000),
            "phone_number": f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}" if random.random() > 0.5 else None,
            "email": f"test{i+1}@example.com" if random.random() > 0.3 else None,
            "shipping_address": f"서울시 강남구 테스트동 {i+1}번지" if random.random() > 0.4 else None,
            "interested_products": random.choice(['뷰티', '패션', '푸드', '전자제품']),
            "owner_comment": f"테스트용 인플루언서 {i+1}입니다.",
            "manager_rating": random.randint(1, 5) if random.random() > 0.3 else None,
            "content_rating": random.randint(1, 5) if random.random() > 0.3 else None,
            "comments_count": random.randint(0, 1000),
            "foreign_followers_ratio": round(random.uniform(0, 50), 2),
            "activity_score": round(random.uniform(0, 100), 2),
            "preferred_mode": random.choice(['seeding', 'promotion', 'sales']),
            "price_krw": random.randint(100000, 5000000),
            "tags": f"테스트,{random.choice(categories)}",
            "active": random.choice([True, False]),
            "post_count": random.randint(0, 1000),
            "profile_text": f"안녕하세요! 테스트 인플루언서 {i+1}입니다.",
            "profile_image_url": f"https://example.com/profile_{i+1}.jpg" if random.random() > 0.5 else None,
            "first_crawled": random.choice([True, False])
        }
        influencers.append(influencer)
    
    return influencers

def generate_campaign_data(count: int = 5) -> List[Dict[str, Any]]:
    """캠페인 테스트 데이터 생성"""
    campaign_types = ['seeding', 'promotion', 'sales']
    statuses = ['planned', 'active', 'paused', 'completed', 'cancelled']
    
    campaigns = []
    for i in range(count):
        start_date = datetime.now() + timedelta(days=random.randint(-30, 30))
        end_date = start_date + timedelta(days=random.randint(7, 90))
        
        campaign = {
            "campaign_name": f"테스트 캠페인 {i+1}",
            "campaign_description": f"테스트용 캠페인 {i+1}입니다. 인플루언서 마케팅을 위한 샘플 캠페인입니다.",
            "campaign_type": random.choice(campaign_types),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "status": random.choice(statuses),
            "campaign_instructions": f"캠페인 {i+1} 실행 가이드입니다.\n1. 제품 리뷰 작성\n2. 해시태그 사용\n3. 스토리 업로드",
            "tags": f"테스트,{random.choice(['뷰티', '패션', '푸드'])}"
        }
        campaigns.append(campaign)
    
    return campaigns

def main():
    parser = argparse.ArgumentParser(description='Connecta Manager 테스트 데이터 생성')
    parser.add_argument('--type', choices=['influencers', 'campaigns', 'all'], 
                       default='all', help='생성할 데이터 타입')
    parser.add_argument('--count', type=int, default=10, help='생성할 데이터 개수')
    parser.add_argument('--output', help='출력 파일 경로')
    
    args = parser.parse_args()
    
    print(f"테스트 데이터 생성 시작... (타입: {args.type}, 개수: {args.count})")
    
    if args.type in ['influencers', 'all']:
        influencers = generate_influencer_data(args.count)
        output_file = args.output or f"samples/data/test_influencers_{args.count}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(influencers, f, ensure_ascii=False, indent=2)
        print(f"인플루언서 데이터 생성 완료: {output_file}")
    
    if args.type in ['campaigns', 'all']:
        campaigns = generate_campaign_data(min(args.count, 5))  # 캠페인은 최대 5개
        output_file = args.output or f"samples/data/test_campaigns_{min(args.count, 5)}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(campaigns, f, ensure_ascii=False, indent=2)
        print(f"캠페인 데이터 생성 완료: {output_file}")
    
    print("테스트 데이터 생성 완료!")

if __name__ == "__main__":
    main()
