#!/usr/bin/env python3
"""
campaign_influencer_participations 테이블 구조 확인 스크립트
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.supabase.config import get_supabase_config
from supabase import create_client, Client

def check_participations_table():
    """campaign_influencer_participations 테이블 구조 확인"""
    try:
        # Supabase 클라이언트 생성
        config = get_supabase_config()
        supabase: Client = create_client(config['url'], config['anon_key'])
        
        print("🔍 campaign_influencer_participations 테이블 구조 확인 중...")
        
        # 테이블 존재 여부 확인 (간단한 쿼리로)
        try:
            result = supabase.table('campaign_influencer_participations').select('*').limit(1).execute()
            print("✅ campaign_influencer_participations 테이블이 존재합니다.")
            print(f"📊 현재 레코드 수: {len(result.data)}")
            
            if result.data:
                print("📋 테이블 구조 (샘플 데이터 기반):")
                sample = result.data[0]
                for key, value in sample.items():
                    print(f"  - {key}: {type(value).__name__} = {value}")
            
        except Exception as e:
            print(f"❌ campaign_influencer_participations 테이블 접근 오류: {e}")
            
            # 테이블이 없는 경우 campaigns 테이블 확인
            try:
                campaigns_result = supabase.table('campaigns').select('*').limit(1).execute()
                print("✅ campaigns 테이블은 존재합니다.")
                print(f"📊 campaigns 레코드 수: {len(campaigns_result.data)}")
            except Exception as campaigns_e:
                print(f"❌ campaigns 테이블도 접근 불가: {campaigns_e}")
                
            # connecta_influencers 테이블 확인
            try:
                influencers_result = supabase.table('connecta_influencers').select('*').limit(1).execute()
                print("✅ connecta_influencers 테이블은 존재합니다.")
                print(f"📊 connecta_influencers 레코드 수: {len(influencers_result.data)}")
            except Exception as influencers_e:
                print(f"❌ connecta_influencers 테이블도 접근 불가: {influencers_e}")
        
        # 테이블 생성이 필요한지 확인
        print("\n🔧 테이블 생성이 필요한 경우 campaign_db_updates.sql을 실행하세요.")
        
    except Exception as e:
        print(f"❌ 전체 오류: {e}")

if __name__ == "__main__":
    check_participations_table()
