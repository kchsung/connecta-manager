#!/usr/bin/env python3
"""
데이터베이스 연결 테스트 스크립트
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

# 환경 변수 확인
print("\n[INFO] 환경 변수 확인:")
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

print(f"  - SUPABASE_URL: {'설정됨' if supabase_url else '없음'}")
if supabase_url:
    print(f"    값: {supabase_url[:50]}...")
else:
    print("    [ERROR] SUPABASE_URL이 설정되지 않았습니다!")

print(f"  - SUPABASE_ANON_KEY: {'설정됨' if supabase_anon_key else '없음'}")
if supabase_anon_key:
    print(f"    값: {supabase_anon_key[:20]}...")
else:
    print("    [ERROR] SUPABASE_ANON_KEY가 설정되지 않았습니다!")

# Supabase 클라이언트 테스트
if supabase_url and supabase_anon_key:
    try:
        from supabase import create_client, Client
        
        print("\n[INFO] Supabase 클라이언트 생성 시도...")
        client = create_client(supabase_url, supabase_anon_key)
        print("[OK] Supabase 클라이언트 생성 성공")
        
        # 간단한 쿼리 테스트
        print("\n[INFO] 데이터베이스 쿼리 테스트...")
        
        # campaigns 테이블 조회
        try:
            response = client.table("campaigns").select("*").limit(5).execute()
            print(f"[OK] campaigns 테이블 조회 성공: {len(response.data)}개 레코드")
            if response.data:
                print(f"  첫 번째 레코드: {response.data[0]}")
        except Exception as e:
            print(f"[ERROR] campaigns 테이블 조회 실패: {e}")
        
        # connecta_influencers 테이블 조회
        try:
            response = client.table("connecta_influencers").select("*").limit(5).execute()
            print(f"[OK] connecta_influencers 테이블 조회 성공: {len(response.data)}개 레코드")
            if response.data:
                print(f"  첫 번째 레코드: {response.data[0]}")
        except Exception as e:
            print(f"[ERROR] connecta_influencers 테이블 조회 실패: {e}")
        
        # campaign_influencer_participations 테이블 조회
        try:
            response = client.table("campaign_influencer_participations").select("*").limit(5).execute()
            print(f"[OK] campaign_influencer_participations 테이블 조회 성공: {len(response.data)}개 레코드")
            if response.data:
                print(f"  첫 번째 레코드: {response.data[0]}")
        except Exception as e:
            print(f"[ERROR] campaign_influencer_participations 테이블 조회 실패: {e}")
        
        # campaign_influencer_contents 테이블 조회
        try:
            response = client.table("campaign_influencer_contents").select("*").limit(5).execute()
            print(f"[OK] campaign_influencer_contents 테이블 조회 성공: {len(response.data)}개 레코드")
            if response.data:
                print(f"  첫 번째 레코드: {response.data[0]}")
        except Exception as e:
            print(f"[ERROR] campaign_influencer_contents 테이블 조회 실패: {e}")
            
    except Exception as e:
        print(f"[ERROR] Supabase 클라이언트 생성 실패: {e}")
else:
    print("\n[ERROR] 환경 변수가 설정되지 않아 테스트를 진행할 수 없습니다.")
    print("\n[INFO] 해결 방법:")
    print("1. .env 파일을 프로젝트 루트에 생성하세요")
    print("2. 다음 내용을 추가하세요:")
    print("   SUPABASE_URL=your_supabase_url_here")
    print("   SUPABASE_ANON_KEY=your_supabase_anon_key_here")

print("\n" + "="*50)
print("테스트 완료")
