#!/usr/bin/env python3
"""
페이지네이션 수정 후 테스트
"""

import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
try:
    load_dotenv()
    print("[OK] .env 파일 로드됨")
except Exception as e:
    print(f"[WARNING] .env 파일 로드 실패: {e}")

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.supabase.simple_client import simple_client
    
    print("\n[INFO] 수정된 get_influencers 메서드 테스트...")
    
    # 전체 인플루언서 조회
    print("\n1. 전체 인플루언서 조회:")
    all_influencers = simple_client.get_influencers()
    print(f"   조회된 총 인플루언서 수: {len(all_influencers)}개")
    
    # 플랫폼별 분포 확인
    platform_counts = {}
    for influencer in all_influencers:
        platform = influencer.get('platform', 'unknown')
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    print("\n   플랫폼별 분포:")
    for platform, count in platform_counts.items():
        print(f"     {platform}: {count}개")
    
    # Instagram 인플루언서만 조회
    print("\n2. Instagram 인플루언서만 조회:")
    instagram_influencers = simple_client.get_influencers(platform="instagram")
    print(f"   Instagram 인플루언서 수: {len(instagram_influencers)}개")
    
    # TikTok 인플루언서만 조회
    print("\n3. TikTok 인플루언서만 조회:")
    tiktok_influencers = simple_client.get_influencers(platform="tiktok")
    print(f"   TikTok 인플루언서 수: {len(tiktok_influencers)}개")
    
    # YouTube 인플루언서만 조회
    print("\n4. YouTube 인플루언서만 조회:")
    youtube_influencers = simple_client.get_influencers(platform="youtube")
    print(f"   YouTube 인플루언서 수: {len(youtube_influencers)}개")
    
    # 검증
    total_by_platform = sum(platform_counts.values())
    print(f"\n[검증] 플랫폼별 합계: {total_by_platform}개")
    print(f"[검증] 전체 조회 수: {len(all_influencers)}개")
    
    if total_by_platform == len(all_influencers):
        print("[OK] 검증 성공: 모든 데이터가 정상적으로 조회되었습니다!")
    else:
        print("[ERROR] 검증 실패: 데이터 불일치가 있습니다.")
        
except Exception as e:
    print(f"[ERROR] 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("테스트 완료")
