"""
활동성/반응성 데이터 디버깅 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.supabase.simple_client import simple_client

def debug_activity_data():
    """활동성/반응성 데이터 디버깅"""
    print("🔍 활동성/반응성 데이터 디버깅 시작...")
    
    try:
        client = simple_client.get_client()
        if not client:
            print("❌ Supabase 클라이언트를 가져올 수 없습니다.")
            return
        
        # 전체 데이터 조회
        response = client.table("ai_influencer_analyses").select(
            "id, follow_network_analysis, comment_authenticity_analysis, evaluation, content_analysis"
        ).execute()
        
        print(f"📊 총 분석 데이터 수: {len(response.data)}")
        
        if not response.data:
            print("❌ 분석 데이터가 없습니다.")
            return
        
        # 데이터 분석
        network_analysis_count = 0
        comment_analysis_count = 0
        
        engagement_rates = []
        likes = []
        comments = []
        recency_spans = []
        posting_paces = []
        
        print("\n📋 각 레코드별 데이터 분석:")
        for i, item in enumerate(response.data[:5]):  # 처음 5개만 상세 분석
            print(f"\n--- 레코드 {i+1} ---")
            print(f"ID: {item.get('id')}")
            
            network_analysis = item.get("follow_network_analysis", {})
            comment_analysis = item.get("comment_authenticity_analysis", {})
            
            if isinstance(network_analysis, dict) and network_analysis:
                network_analysis_count += 1
                print("✅ 네트워크 분석 데이터 있음")
                print(f"  - 전체 JSON 구조: {list(network_analysis.keys())}")
                
                # 각 필드 확인
                avg_likes = network_analysis.get("avg_likes_last5")
                recency_span = network_analysis.get("recency_span_last5_days")
                posting_pace = network_analysis.get("posting_pace_last5")
                engagement_rate = network_analysis.get("est_engagement_rate_last5")
                
                print(f"  - avg_likes_last5: {avg_likes}")
                print(f"  - recency_span_last5_days: {recency_span}")
                print(f"  - posting_pace_last5: {posting_pace}")
                print(f"  - est_engagement_rate_last5: {engagement_rate}")
                
                # 다른 가능한 필드명들도 확인
                print("  - 다른 필드들:")
                for key, value in network_analysis.items():
                    if key not in ["avg_likes_last5", "recency_span_last5_days", "posting_pace_last5", "est_engagement_rate_last5"]:
                        print(f"    {key}: {value}")
                
                # 데이터 수집
                if avg_likes is not None:
                    try:
                        likes.append(float(avg_likes))
                    except (ValueError, TypeError):
                        pass
                
                if recency_span is not None:
                    try:
                        recency_spans.append(float(recency_span))
                    except (ValueError, TypeError):
                        pass
                
                if posting_pace:
                    posting_paces.append(posting_pace)
                
                if engagement_rate is not None:
                    try:
                        engagement_rates.append(float(engagement_rate))
                    except (ValueError, TypeError):
                        pass
            else:
                print("❌ 네트워크 분석 데이터 없음")
            
            if isinstance(comment_analysis, dict) and comment_analysis:
                comment_analysis_count += 1
                print("✅ 댓글 분석 데이터 있음")
                print(f"  - 전체 JSON 구조: {list(comment_analysis.keys())}")
                
                avg_comments = comment_analysis.get("avg_comments_last5")
                print(f"  - avg_comments_last5: {avg_comments}")
                
                # 다른 가능한 필드명들도 확인
                print("  - 다른 필드들:")
                for key, value in comment_analysis.items():
                    if key not in ["avg_comments_last5"]:
                        print(f"    {key}: {value}")
                
                if avg_comments is not None:
                    try:
                        comments.append(float(avg_comments))
                    except (ValueError, TypeError):
                        pass
            else:
                print("❌ 댓글 분석 데이터 없음")
        
        print(f"\n📊 전체 데이터 요약:")
        print(f"  - 네트워크 분석 데이터가 있는 레코드: {network_analysis_count}/{len(response.data)}")
        print(f"  - 댓글 분석 데이터가 있는 레코드: {comment_analysis_count}/{len(response.data)}")
        print(f"  - 수집된 참여율 데이터: {len(engagement_rates)}개")
        print(f"  - 수집된 좋아요 데이터: {len(likes)}개")
        print(f"  - 수집된 댓글 데이터: {len(comments)}개")
        print(f"  - 수집된 활동 주기 데이터: {len(recency_spans)}개")
        print(f"  - 수집된 게시 빈도 데이터: {len(posting_paces)}개")
        
        if engagement_rates:
            print(f"  - 참여율 범위: {min(engagement_rates):.2f} ~ {max(engagement_rates):.2f}")
        if likes:
            print(f"  - 좋아요 범위: {min(likes):.0f} ~ {max(likes):.0f}")
        if comments:
            print(f"  - 댓글 범위: {min(comments):.0f} ~ {max(comments):.0f}")
        
        # 문제 진단
        print(f"\n🔍 문제 진단:")
        if not engagement_rates and not likes and not comments:
            print("❌ 모든 활동성 데이터가 없습니다.")
            print("💡 AI 분석이 완료되지 않았거나 데이터 구조가 다를 수 있습니다.")
        else:
            print("✅ 일부 활동성 데이터가 있습니다.")
            if not engagement_rates:
                print("⚠️ 참여율 데이터가 없습니다.")
            if not likes:
                print("⚠️ 좋아요 데이터가 없습니다.")
            if not comments:
                print("⚠️ 댓글 데이터가 없습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    debug_activity_data()
