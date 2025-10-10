#!/usr/bin/env python3
"""
phone_number와 shipping_address 필드 조회 테스트
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.db.database import DatabaseManager

def test_phone_shipping_fields():
    """phone_number와 shipping_address 필드가 제대로 조회되는지 테스트"""
    print("phone_number와 shipping_address 필드 조회 테스트 시작...")
    
    try:
        # 데이터베이스 매니저 초기화
        db_manager = DatabaseManager()
        
        # 인플루언서 목록 조회
        print("인플루언서 목록 조회 중...")
        influencers = db_manager.get_influencers()
        
        if not influencers:
            print("인플루언서가 없습니다.")
            return
        
        print(f"총 {len(influencers)}명의 인플루언서 조회됨")
        
        # 첫 번째 인플루언서의 필드들 확인
        first_influencer = influencers[0]
        print(f"\n첫 번째 인플루언서 정보:")
        print(f"  - ID: {first_influencer.get('id')}")
        print(f"  - SNS ID: {first_influencer.get('sns_id')}")
        print(f"  - 이름: {first_influencer.get('influencer_name')}")
        
        # phone_number 필드 확인
        phone_number = first_influencer.get('phone_number')
        print(f"  - Phone Number: {phone_number} (타입: {type(phone_number)})")
        
        # shipping_address 필드 확인
        shipping_address = first_influencer.get('shipping_address')
        print(f"  - Shipping Address: {shipping_address} (타입: {type(shipping_address)})")
        
        # 모든 필드명 출력
        print(f"\n사용 가능한 모든 필드명:")
        for key in sorted(first_influencer.keys()):
            value = first_influencer[key]
            value_type = type(value).__name__
            value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"  - {key}: {value_preview} ({value_type})")
        
        # phone_number와 shipping_address가 있는 인플루언서 찾기
        print(f"\nphone_number가 있는 인플루언서:")
        phone_count = 0
        for inf in influencers:
            if inf.get('phone_number'):
                phone_count += 1
                print(f"  - {inf.get('sns_id')}: {inf.get('phone_number')}")
        
        print(f"phone_number가 있는 인플루언서: {phone_count}명")
        
        print(f"\nshipping_address가 있는 인플루언서:")
        shipping_count = 0
        for inf in influencers:
            if inf.get('shipping_address'):
                shipping_count += 1
                print(f"  - {inf.get('sns_id')}: {inf.get('shipping_address')[:50]}...")
        
        print(f"shipping_address가 있는 인플루언서: {shipping_count}명")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_phone_shipping_fields()
