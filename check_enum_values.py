#!/usr/bin/env python3
"""
데이터베이스 enum 값 확인 스크립트
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
    
    # enum 값 확인을 위한 쿼리
    print("\n[INFO] 데이터베이스 enum 값 확인...")
    
    # PostgreSQL에서 enum 타입 확인
    enum_query = """
    SELECT t.typname as enum_name, e.enumlabel as enum_value
    FROM pg_type t 
    JOIN pg_enum e ON t.oid = e.enumtypid  
    WHERE t.typname IN ('campaign_type', 'campaign_status', 'sample_status', 'contact_method', 'preferred_mode', 'platform', 'data_type')
    ORDER BY t.typname, e.enumsortorder;
    """
    
    try:
        response = client.rpc('exec_sql', {'sql': enum_query}).execute()
        if response.data:
            print("[OK] Enum 값들:")
            current_enum = None
            for row in response.data:
                if row['enum_name'] != current_enum:
                    current_enum = row['enum_name']
                    print(f"\n{current_enum}:")
                print(f"  - {row['enum_value']}")
        else:
            print("[WARNING] Enum 값 조회 실패, 직접 테이블 구조 확인...")
            
            # 테이블 구조 확인
            tables = ['campaigns', 'connecta_influencers', 'campaign_influencer_participations']
            for table in tables:
                try:
                    response = client.table(table).select("*").limit(1).execute()
                    print(f"\n{table} 테이블 구조 (첫 번째 레코드):")
                    if response.data:
                        for key, value in response.data[0].items():
                            print(f"  {key}: {type(value).__name__} = {value}")
                    else:
                        print(f"  테이블이 비어있음")
                except Exception as e:
                    print(f"[ERROR] {table} 테이블 조회 실패: {e}")
                    
    except Exception as e:
        print(f"[ERROR] Enum 값 조회 실패: {e}")
        print("직접 테이블 구조를 확인해보겠습니다...")
        
        # 테이블 구조 확인
        tables = ['campaigns', 'connecta_influencers', 'campaign_influencer_participations']
        for table in tables:
            try:
                response = client.table(table).select("*").limit(1).execute()
                print(f"\n{table} 테이블 구조 (첫 번째 레코드):")
                if response.data:
                    for key, value in response.data[0].items():
                        print(f"  {key}: {type(value).__name__} = {value}")
                else:
                    print(f"  테이블이 비어있음")
            except Exception as e:
                print(f"[ERROR] {table} 테이블 조회 실패: {e}")
        
except Exception as e:
    print(f"[ERROR] 스크립트 실행 실패: {e}")

print("\n" + "="*50)
print("Enum 값 확인 완료")

