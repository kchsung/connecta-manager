"""
AI 분석 통계 공통 함수들
"""
import streamlit as st
import pandas as pd
import numpy as np
import time
import statistics
import json
import ast
from collections import Counter
from datetime import datetime, timedelta
from ...supabase.simple_client import simple_client
from ...constants.categories import CATEGORY_OPTIONS


def _parse_json_field(raw):
    """문자열로 저장된 JSON 필드를 dict로 안전하게 변환"""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            try:
                return ast.literal_eval(raw)
            except Exception:
                return {}
    return {}

# 기본 통계 함수들
def get_total_analyses_count():
    """총 분석 수 조회 - count만 사용 (페이징 불필요)"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            client = simple_client.get_client()
            if not client:
                return 0
            
            # count="exact"만 사용하면 모든 레코드 수를 반환 (페이징 불필요)
            print(f"Attempting to get total count from ai_influencer_analyses_new table...")
            response = client.table("ai_influencer_analyses_new").select("id", count="exact").execute()
            
            # 디버깅: 응답 확인
            print(f"Response count: {response.count}")
            
            return response.count if response.count else 0
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error in get_total_analyses_count (attempt {attempt + 1}): {error_msg}")
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return 0
            else:
                return 0
    
    return 0

def get_recent_analyses_count():
    """최근 7일 분석 수 조회"""
    try:
        seven_days_ago = datetime.now() - timedelta(days=7)
        client = simple_client.get_client()
        if not client:
            return 0
        
        # 디버깅: 최근 분석 수 확인
        print(f"Getting recent analyses since: {seven_days_ago.isoformat()}")
        response = client.table("ai_influencer_analyses_new").select("id", count="exact").gte("analyzed_at", seven_days_ago.isoformat()).limit(10000).execute()
        
        print(f"Recent analyses count: {response.count if response.count else 0}")
        return response.count if response.count else 0
    except Exception as e:
        print(f"Error in get_recent_analyses_count: {str(e)}")
        return 0

def get_average_overall_score():
    """평균 종합점수 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        client = simple_client.get_client()
        if not client:
            return 0
        
        all_scores = []
        page_size = 1000
        offset = 0
        
        while True:
            # 페이징으로 데이터 가져오기
            response = client.table("ai_influencer_analyses_new").select("evaluation").range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
            
            # 점수 추출
            page_scores = []
            for item in response.data:
                evaluation = item.get("evaluation", {})
                if isinstance(evaluation, dict):
                    overall_score = evaluation.get("overall_score")
                    if overall_score is not None:
                        try:
                            page_scores.append(float(overall_score))
                        except (ValueError, TypeError):
                            pass
            
            all_scores.extend(page_scores)
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        return avg_score
    except Exception as e:
        print(f"Error in get_average_overall_score: {str(e)}")
        return 0

def get_category_average_scores():
    """카테고리별 평균 종합점수 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        client = simple_client.get_client()
        if not client:
            return {}
        
        category_scores = {}  # {category: [scores]}
        page_size = 1000
        offset = 0
        
        while True:
            # 페이징으로 데이터 가져오기
            response = client.table("ai_influencer_analyses_new").select("category, evaluation").range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
            
            # 점수 추출
            for item in response.data:
                category = item.get("category")
                evaluation = item.get("evaluation", {})
                
                if category and isinstance(evaluation, dict):
                    overall_score = evaluation.get("overall_score")
                    if overall_score is not None:
                        try:
                            score = float(overall_score)
                            if category not in category_scores:
                                category_scores[category] = []
                            category_scores[category].append(score)
                        except (ValueError, TypeError):
                            pass
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        # 카테고리별 평균 계산
        category_averages = {}
        for category, scores in category_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                category_averages[category] = avg_score
        
        return category_averages
    except Exception as e:
        print(f"Error in get_category_average_scores: {str(e)}")
        return {}

def get_recommendation_distribution():
    """추천도 분포 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        client = simple_client.get_client()
        if not client:
            return {}
        
        all_recommendations = []
        page_size = 1000
        offset = 0
        
        print(f"Starting to fetch all recommendations with pagination...")
        
        while True:
            # 페이징으로 데이터 가져오기
            response = client.table("ai_influencer_analyses_new").select("recommendation").range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
                
            # 추천도 추출
            page_recommendations = [item.get("recommendation") for item in response.data if item.get("recommendation")]
            all_recommendations.extend(page_recommendations)
            
            print(f"Fetched page {offset//page_size + 1}: {len(response.data)} records, {len(page_recommendations)} recommendations")
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        print(f"Total recommendations collected: {len(all_recommendations)}")
        
        # 추천도 분포 계산
        distribution = {}
        for rec in all_recommendations:
            distribution[rec] = distribution.get(rec, 0) + 1
        
        print(f"Recommendation distribution: {distribution}")
        return distribution
    except Exception as e:
        print(f"Error in get_recommendation_distribution: {str(e)}")
        return {}

def get_category_distribution():
    """카테고리 분포 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        client = simple_client.get_client()
        if not client:
            return {}
        
        all_categories = []
        page_size = 1000
        offset = 0
        
        print(f"Starting to fetch all categories with pagination...")
        
        while True:
            # 페이징으로 데이터 가져오기
            response = client.table("ai_influencer_analyses_new").select("category").range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
                
            # 카테고리 추출
            page_categories = [item.get("category") for item in response.data if item.get("category")]
            all_categories.extend(page_categories)
            
            print(f"Fetched page {offset//page_size + 1}: {len(response.data)} records, {len(page_categories)} categories")
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        print(f"Total categories collected: {len(all_categories)}")
        
        if all_categories:
            unique_categories = list(set(all_categories))
            print(f"Unique categories found: {unique_categories}")
            print(f"Total unique categories: {len(unique_categories)}")
        
        # 카테고리 분포 계산
        distribution = {}
        for cat in all_categories:
            distribution[cat] = distribution.get(cat, 0) + 1
        
        
        return distribution
    except Exception as e:
        print(f"Error in get_category_distribution: {str(e)}")
        return {}

def get_analysis_rate():
    """분석률 조회 - tb_instagram_crawling 테이블 대비 ai_influencer_analyses 테이블의 비율"""
    try:
        client = simple_client.get_client()
        if not client:
            return 0
        
        # tb_instagram_crawling 테이블의 총 크롤링 수
        crawling_response = client.table("tb_instagram_crawling").select("id", count="exact").limit(10000).execute()
        total_crawling_count = crawling_response.count if crawling_response.count else 0
        
        # ai_influencer_analyses 테이블의 총 분석 수
        analysis_response = client.table("ai_influencer_analyses_new").select("id", count="exact").limit(10000).execute()
        total_analysis_count = analysis_response.count if analysis_response.count else 0
        
        analysis_rate = (total_analysis_count / total_crawling_count) * 100 if total_crawling_count > 0 else 0
        
        return analysis_rate
    except Exception as e:
        print(f"Error in get_analysis_rate: {str(e)}")
        return 0

def get_tags_for_wordcloud():
    """워드클라우드를 위한 tags 데이터 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        client = simple_client.get_client()
        if not client:
            return []
        
        all_tags = []
        page_size = 1000
        offset = 0
        
        print(f"Starting to fetch all tags with pagination...")
        
        while True:
            # 페이징으로 데이터 가져오기
            response = client.table("ai_influencer_analyses_new").select("tags").range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
            
            # 태그 추출
            page_tags = []
            for item in response.data:
                tags = item.get("tags")
                if tags:
                    # tags가 문자열인 경우 쉼표로 분리
                    if isinstance(tags, str):
                        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                        page_tags.extend(tag_list)
                    # tags가 리스트인 경우
                    elif isinstance(tags, list):
                        page_tags.extend([tag.strip() for tag in tags if tag.strip()])
            
            all_tags.extend(page_tags)
            
            print(f"Fetched page {offset//page_size + 1}: {len(response.data)} records, {len(page_tags)} tags")
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        # 디버깅: 태그 통계 확인
        print(f"Total tags collected: {len(all_tags)}")
        if all_tags:
            tag_counts = Counter(all_tags)
            print(f"Unique tags: {len(tag_counts)}")
            print(f"Top 5 tags: {tag_counts.most_common(5)}")
        
        return all_tags
    except Exception as e:
        print(f"Error in get_tags_for_wordcloud: {str(e)}")
        return []

def get_category_tags(category):
    """특정 카테고리의 태그 데이터 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        from collections import Counter
        client = simple_client.get_client()
        if not client:
            return []
        
        all_tags = []
        page_size = 1000
        offset = 0
        
        while True:
            # 특정 카테고리의 데이터만 페이징으로 가져오기
            response = client.table("ai_influencer_analyses_new").select("tags").eq("category", category).range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
            
            # 태그 추출
            page_tags = []
            for item in response.data:
                tags = item.get("tags")
                if tags:
                    # tags가 문자열인 경우 텍스트 배열로 파싱
                    if isinstance(tags, str):
                        # 텍스트 배열 형태: ["태그1","태그2","태그3"] -> 태그1, 태그2, 태그3
                        if tags.startswith('[') and tags.endswith(']'):
                            # 대괄호 제거하고 쉼표로 분리
                            content = tags[1:-1]  # [ ] 제거
                            # 따옴표로 둘러싸인 태그들을 추출
                            import re
                            tag_matches = re.findall(r'"([^"]*)"', content)
                            if tag_matches:
                                page_tags.extend([tag.strip() for tag in tag_matches if tag.strip()])
                            else:
                                # 따옴표가 없는 경우 쉼표로 분리
                                tag_list = [tag.strip() for tag in content.split(',') if tag.strip()]
                                page_tags.extend(tag_list)
                        else:
                            # 일반 쉼표로 구분된 문자열
                            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                            page_tags.extend(tag_list)
                    # tags가 리스트인 경우
                    elif isinstance(tags, list):
                        page_tags.extend([tag.strip() for tag in tags if tag.strip()])
            
            all_tags.extend(page_tags)
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        return all_tags
    except Exception as e:
        print(f"Error in get_category_tags for category '{category}': {str(e)}")
        return []

def get_evaluation_scores_statistics():
    """평가 점수 통계 조회 - JSON 필드에서 추출 (페이징으로 모든 데이터 가져오기)"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = client.table("ai_influencer_analyses_new").select("evaluation, content_analysis").range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
            
            all_data.extend(response.data)
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        if not all_data:
            return None
        
        # 각 점수별 데이터 추출 (JSON 필드에서)
        engagement_scores = []
        activity_scores = []
        communication_scores = []
        growth_potential_scores = []
        overall_scores = []
        
        for item in all_data:
            evaluation = item.get("evaluation", {})
            if isinstance(evaluation, dict):
                # engagement 점수 추출
                engagement = evaluation.get("engagement")
                if engagement is not None:
                    try:
                        engagement_scores.append(float(engagement))
                    except (ValueError, TypeError):
                        pass
                
                # activity 점수 추출
                activity = evaluation.get("activity")
                if activity is not None:
                    try:
                        activity_scores.append(float(activity))
                    except (ValueError, TypeError):
                        pass
                
                # communication 점수 추출
                communication = evaluation.get("communication")
                if communication is not None:
                    try:
                        communication_scores.append(float(communication))
                    except (ValueError, TypeError):
                        pass
                
                # growth_potential 점수 추출
                growth_potential = evaluation.get("growth_potential")
                if growth_potential is not None:
                    try:
                        growth_potential_scores.append(float(growth_potential))
                    except (ValueError, TypeError):
                        pass
                
                # overall_score 점수 추출
                overall_score = evaluation.get("overall_score")
                if overall_score is not None:
                    try:
                        overall_scores.append(float(overall_score))
                    except (ValueError, TypeError):
                        pass
        
        # inference_confidence는 content_analysis JSON에서 추출
        inference_confidences = []
        for item in all_data:
            content_analysis = item.get("content_analysis", {})
            if isinstance(content_analysis, dict):
                confidence = content_analysis.get("inference_confidence")
                if confidence is not None:
                    try:
                        inference_confidences.append(float(confidence))
                    except (ValueError, TypeError):
                        pass
        
        # 상관관계 데이터 준비
        correlation_data = None
        if len(engagement_scores) > 1:
            try:
                df = pd.DataFrame({
                    'engagement': engagement_scores[:len(overall_scores)],
                    'activity': activity_scores[:len(overall_scores)],
                    'communication': communication_scores[:len(overall_scores)],
                    'growth_potential': growth_potential_scores[:len(overall_scores)],
                    'overall': overall_scores
                })
                correlation_data = df.corr()
            except:
                correlation_data = None
        
        # NaN 값 필터링
        def filter_nan_values(data_list):
            """NaN, None, inf 값을 제거한 유효한 데이터만 반환"""
            if not data_list:
                return []
            return [
                x for x in data_list 
                if x is not None and pd.notna(x) and np.isfinite(x)
            ]
        
        engagement_scores_clean = filter_nan_values(engagement_scores)
        activity_scores_clean = filter_nan_values(activity_scores)
        communication_scores_clean = filter_nan_values(communication_scores)
        growth_potential_scores_clean = filter_nan_values(growth_potential_scores)
        overall_scores_clean = filter_nan_values(overall_scores)
        inference_confidences_clean = filter_nan_values(inference_confidences)
        
        return {
            "avg_engagement": sum(engagement_scores_clean) / len(engagement_scores_clean) if engagement_scores_clean else 0,
            "avg_activity": sum(activity_scores_clean) / len(activity_scores_clean) if activity_scores_clean else 0,
            "avg_communication": sum(communication_scores_clean) / len(communication_scores_clean) if communication_scores_clean else 0,
            "avg_growth_potential": sum(growth_potential_scores_clean) / len(growth_potential_scores_clean) if growth_potential_scores_clean else 0,
            "avg_overall": sum(overall_scores_clean) / len(overall_scores_clean) if overall_scores_clean else 0,
            "engagement_score_distribution": engagement_scores_clean,
            "activity_score_distribution": activity_scores_clean,
            "communication_score_distribution": communication_scores_clean,
            "growth_potential_score_distribution": growth_potential_scores_clean,
            "overall_score_distribution": overall_scores_clean,
            "inference_confidence_distribution": inference_confidences_clean,
            "correlation_data": correlation_data
        }
    except Exception as e:
        st.error(f"평가 점수 통계 조회 중 오류: {str(e)}")
        return None

def get_enhanced_network_analysis_statistics():
    """고도화된 네트워크 분석 통계 조회 - 페이징으로 모든 데이터 가져오기"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            client = simple_client.get_client()
            if not client:
                return None
            
            all_data = []
            page_size = 1000
            offset = 0
            
            while True:
                response = client.table("ai_influencer_analyses_new").select("follow_network_analysis, followers, followings").range(offset, offset + page_size - 1).execute()
                
                if not response.data or len(response.data) == 0:
                    break
                
                all_data.extend(response.data)
                
                # 더 이상 데이터가 없으면 중단
                if len(response.data) < page_size:
                    break
                    
                offset += page_size
            
            if not all_data:
                return None
            
            print(f"Network analysis - Total data fetched: {len(all_data)} records")
        
            authenticity_scores = []
            network_types = []
            followers_list = []
            followings_list = []
            network_type_authenticity = {}
            
            for item in all_data:
                network_analysis = item.get("follow_network_analysis", {})
                followers = item.get("followers", 0)
                followings = item.get("followings", 0)
                
                if isinstance(network_analysis, dict):
                    # 영향력 진정성 점수 추출
                    score = network_analysis.get("influence_authenticity_score")
                    if score is not None:
                        try:
                            score_val = float(score)
                            authenticity_scores.append(score_val)
                            
                            # 네트워크 유형별 진정성 점수 수집
                            network_type = network_analysis.get("network_type")
                            if network_type:
                                if network_type not in network_type_authenticity:
                                    network_type_authenticity[network_type] = []
                                network_type_authenticity[network_type].append(score_val)
                        except (ValueError, TypeError):
                            pass
                    
                    # 네트워크 유형 추출
                    network_type = network_analysis.get("network_type")
                    if network_type:
                        network_types.append(network_type)
                
                # 팔로워/팔로잉 데이터 수집
                if followers and followings:
                    try:
                        followers_list.append(int(followers))
                        followings_list.append(int(followings))
                    except (ValueError, TypeError):
                        pass
            
            # 기본 통계 계산
            if not authenticity_scores:
                return None
            
            # 표준편차 계산
            std_authenticity_score = statistics.stdev(authenticity_scores) if len(authenticity_scores) > 1 else 0
            
            # 네트워크 유형 분포 계산
            network_type_dist = {}
            for nt in network_types:
                network_type_dist[nt] = network_type_dist.get(nt, 0) + 1
            
            # 네트워크 유형별 평균 진정성 점수 계산
            network_type_avg_authenticity = {}
            for nt, scores in network_type_authenticity.items():
                if scores:
                    network_type_avg_authenticity[nt] = sum(scores) / len(scores)
            
            # 팔로워/팔로잉 비율 계산
            follower_following_ratio = []
            for i in range(min(len(followers_list), len(followings_list))):
                if followings_list[i] > 0:
                    ratio = followers_list[i] / followings_list[i]
                    follower_following_ratio.append(ratio)
            
            # 팔로워/팔로잉 비율 통계
            avg_follower_following_ratio = sum(follower_following_ratio) / len(follower_following_ratio) if follower_following_ratio else 0
            median_follower_following_ratio = sorted(follower_following_ratio)[len(follower_following_ratio)//2] if follower_following_ratio else 0
            max_follower_following_ratio = max(follower_following_ratio) if follower_following_ratio else 0
            
            # 진정성 점수와 팔로워 수 상관관계 데이터
            authenticity_follower_correlation = None
            authenticity_follower_correlation_coef = 0
            if len(authenticity_scores) == len(followers_list) and len(authenticity_scores) > 1:
                try:
                    correlation_coef = np.corrcoef(authenticity_scores, followers_list[:len(authenticity_scores)])[0, 1]
                    if not np.isnan(correlation_coef):
                        authenticity_follower_correlation_coef = correlation_coef
                        authenticity_follower_correlation = {
                            'followers': followers_list[:len(authenticity_scores)],
                            'authenticity_scores': authenticity_scores
                        }
                except:
                    pass
            
            # 네트워크 품질 등급 분류 (자연스러운 분포)
            network_quality_grades = {"매우 우수": 0, "우수": 0, "보통": 0, "미흡": 0, "매우 미흡": 0}
            
            if authenticity_scores:
                # 통계값 계산
                mean_score = sum(authenticity_scores) / len(authenticity_scores)
                std_score = (sum((x - mean_score) ** 2 for x in authenticity_scores) / len(authenticity_scores)) ** 0.5
                
                for score in authenticity_scores:
                    # Z-score 계산
                    z_score = (score - mean_score) / std_score if std_score > 0 else 0
                    
                    # 자연스러운 분포를 위한 기준점 (정규분포 가정)
                    if z_score >= 1.0:  # 상위 15.9%
                        network_quality_grades["매우 우수"] += 1
                    elif z_score >= 0.3:  # 상위 38.2%
                        network_quality_grades["우수"] += 1
                    elif z_score >= -0.3:  # 중간 23.6%
                        network_quality_grades["보통"] += 1
                    elif z_score >= -1.0:  # 하위 15.9%
                        network_quality_grades["미흡"] += 1
                    else:  # 최하위 6.4%
                        network_quality_grades["매우 미흡"] += 1
            
            return {
                "avg_authenticity_score": sum(authenticity_scores) / len(authenticity_scores),
                "median_authenticity_score": sorted(authenticity_scores)[len(authenticity_scores)//2],
                "max_authenticity_score": max(authenticity_scores),
                "min_authenticity_score": min(authenticity_scores),
                "std_authenticity_score": std_authenticity_score,
                "authenticity_distribution": authenticity_scores,
                "network_type_distribution": network_type_dist,
                "network_type_authenticity": network_type_avg_authenticity,
                "follower_following_ratio": follower_following_ratio,
                "avg_follower_following_ratio": avg_follower_following_ratio,
                "median_follower_following_ratio": median_follower_following_ratio,
                "max_follower_following_ratio": max_follower_following_ratio,
                "authenticity_follower_correlation": authenticity_follower_correlation,
                "authenticity_follower_correlation_coef": authenticity_follower_correlation_coef,
                "network_quality_grades": network_quality_grades
            }
            
        except Exception as e:
            error_msg = str(e)
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"서버 연결 오류. {retry_delay}s 후 재시도... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    st.error(f"고도화된 네트워크 분석 통계 조회 실패(재시도 초과): {error_msg}")
                    return None
            else:
                st.error(f"고도화된 네트워크 분석 통계 조회 중 오류: {error_msg}")
                return None
    
    return None

def get_enhanced_activity_metrics_statistics():
    """고도화된 활동성 메트릭 통계 조회 - 페이징으로 모든 데이터 가져오기"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            client = simple_client.get_client()
            if not client:
                return None
            
            all_data = []
            page_size = 1000
            offset = 0
            
            while True:
                response = client.table("ai_influencer_analyses_new").select("follow_network_analysis, comment_authenticity_analysis, followers, followings, posts_count").range(offset, offset + page_size - 1).execute()
                
                if not response.data or len(response.data) == 0:
                    break
                
                all_data.extend(response.data)
                
                # 더 이상 데이터가 없으면 중단
                if len(response.data) < page_size:
                    break
                    
                offset += page_size
            
            if not all_data:
                return None
            
            print(f"Activity metrics - Total data fetched: {len(all_data)} records")
        
            likes = []
            comments = []
            engagement_rates = []
            recency_spans = []
            posting_paces = []
            posting_pace_engagement = {}
            
            for item in all_data:
                # JSON 필드가 문자열로 저장된 경우 파싱
                network_analysis_raw = item.get("follow_network_analysis", {})
                comment_analysis_raw = item.get("comment_authenticity_analysis", {})
                
                # 문자열인 경우 JSON으로 파싱
                if isinstance(network_analysis_raw, str):
                    try:
                        import json
                        network_analysis = json.loads(network_analysis_raw)
                    except:
                        network_analysis = {}
                else:
                    network_analysis = network_analysis_raw
                
                
                if isinstance(comment_analysis_raw, str):
                    try:
                        import json
                        comment_analysis = json.loads(comment_analysis_raw)
                    except:
                        comment_analysis = {}
                else:
                    comment_analysis = comment_analysis_raw
                
                if isinstance(network_analysis, dict):
                    # 실제 데이터 구조에 맞게 수정
                    # 1. 팔로워/팔로잉 비율에서 활동성 추정
                    followers = item.get('followers', 0) or 0
                    followings = item.get('followings', 0) or 0
                    posts_count = item.get('posts_count', 0) or 0
                    
                    # None 값 처리
                    if followers is None:
                        followers = 0
                    if followings is None:
                        followings = 0
                    if posts_count is None:
                        posts_count = 0
                    
                    if followers > 0 and followings > 0:
                        # 실제 데이터에서 ratio_followers_to_followings 필드 사용
                        ratio = network_analysis.get("ratio_followers_to_followings", 0)
                        if ratio == 0:
                            # ratio_followers_to_followings가 없으면 계산
                            ratio = followers / followings
                        
                        # 비율을 0-5 범위로 정규화하여 참여율로 사용
                        # 28.2 (블랑이브) -> 약 1.4%, 167.46 (셩이홈) -> 약 3.3%
                        estimated_engagement = min(5.0, ratio / 20)  # 20배 비율을 5% 참여율로 매핑
                        engagement_rates.append(estimated_engagement)
                        
                        # 게시물 수 기반 활동 주기 추정
                        if posts_count > 0:
                            # 게시물 수가 많을수록 활동 주기가 짧다고 가정
                            # 2186개 (블랑이브) -> 약 1일, 423개 (셩이홈) -> 약 8일
                            estimated_recency = max(1, 30 - (posts_count / 100))  # 1-30일 범위
                            recency_spans.append(estimated_recency)
                    
                    # 2. 진정성 점수에서 좋아요 추정
                    authenticity_score = network_analysis.get("influence_authenticity_score", 0)
                    if authenticity_score is None:
                        authenticity_score = 0
                    if authenticity_score > 0:
                        # 진정성 점수가 높을수록 좋아요가 많다고 가정
                        # 85점 (블랑이브) -> 13k * 0.85 * 0.01 = 110개
                        estimated_likes = (authenticity_score / 100) * followers * 0.01
                        likes.append(estimated_likes)
                    
                    # 3. 네트워크 유형에서 게시 빈도 추정
                    network_type = network_analysis.get("network_type_inference", "")
                    if network_type is None:
                        network_type = ""
                    if "비대칭형" in network_type:
                        posting_paces.append("매일")
                    elif "대칭형" in network_type:
                        posting_paces.append("주 2-3회")
                    else:
                        posting_paces.append("주 1-2회")
                    
                    # 4. 기존 필드들도 시도 (혹시 있을 경우)
                    avg_likes = (network_analysis.get("avg_likes_last5") or 
                               network_analysis.get("avg_likes") or 
                               network_analysis.get("likes_avg") or
                               network_analysis.get("average_likes"))
                    if avg_likes is not None:
                        try:
                            likes.append(float(avg_likes))
                        except (ValueError, TypeError):
                            pass
                    
                    recency_span = (network_analysis.get("recency_span_last5_days") or 
                                  network_analysis.get("recency_span") or 
                                  network_analysis.get("activity_span") or
                                  network_analysis.get("days_since_last_post"))
                    if recency_span is not None:
                        try:
                            recency_spans.append(float(recency_span))
                        except (ValueError, TypeError):
                            pass
                    
                    posting_pace = (network_analysis.get("posting_pace_last5") or 
                                  network_analysis.get("posting_pace") or 
                                  network_analysis.get("posting_frequency") or
                                  network_analysis.get("content_frequency"))
                    if posting_pace:
                        posting_paces.append(posting_pace)
                    
                    engagement_rate = (network_analysis.get("est_engagement_rate_last5") or 
                                     network_analysis.get("engagement_rate") or 
                                     network_analysis.get("avg_engagement_rate") or
                                     network_analysis.get("engagement_percentage"))
                    if engagement_rate is not None:
                        try:
                            engagement_rates.append(float(engagement_rate))
                        except (ValueError, TypeError):
                            pass
                
                if isinstance(comment_analysis, dict):
                    # 진정성 분석에서 댓글 수 추정
                    authenticity_level = comment_analysis.get("authenticity_level", "")
                    if authenticity_level is None:
                        authenticity_level = ""
                    ratio_estimation = comment_analysis.get("ratio_estimation", {})
                    if ratio_estimation is None:
                        ratio_estimation = {}
                    
                    # 진정성 비율에서 댓글 수 추정
                    if ratio_estimation:
                        authentic_ratio_str = ratio_estimation.get("authentic_comments_ratio", "")
                        if authentic_ratio_str:
                            try:
                                # "40%" 형태에서 숫자 추출
                                import re
                                match = re.search(r'(\d+(?:\.\d+)?)', str(authentic_ratio_str))
                                if match:
                                    authentic_ratio = float(match.group(1))
                                    # 진정성 비율이 높을수록 댓글 수가 많다고 가정
                                    followers = item.get('followers', 0)
                                    # 40% (블랑이브) -> 13k * 0.4 * 0.003 = 15개
                                    estimated_comments = (authentic_ratio / 100) * followers * 0.003
                                    comments.append(estimated_comments)
                            except (ValueError, TypeError):
                                pass
                    
                    # 기존 필드들도 시도
                    avg_comments = (comment_analysis.get("avg_comments_last5") or 
                                  comment_analysis.get("avg_comments") or 
                                  comment_analysis.get("comments_avg") or
                                  comment_analysis.get("average_comments"))
                    if avg_comments is not None:
                        try:
                            comments.append(float(avg_comments))
                        except (ValueError, TypeError):
                            pass
            
            # 실제 데이터만 사용 - 샘플 데이터 보완 제거
            
            # 표준편차 계산
            std_engagement_rate = statistics.stdev(engagement_rates) if len(engagement_rates) > 1 else 0
            std_recency_span = statistics.stdev(recency_spans) if len(recency_spans) > 1 else 0
            
            # 게시 빈도 분포 계산
            posting_pace_dist = {}
            for pp in posting_paces:
                posting_pace_dist[pp] = posting_pace_dist.get(pp, 0) + 1
            
            # 게시 빈도별 평균 참여율 계산
            posting_pace_avg_engagement = {}
            for pace, rates in posting_pace_engagement.items():
                if rates:
                    posting_pace_avg_engagement[pace] = sum(rates) / len(rates)
            
            # 좋아요와 댓글 상관관계 계산
            likes_comments_correlation = None
            likes_comments_correlation_coef = 0
            if len(likes) == len(comments) and len(likes) > 1:
                try:
                    correlation_coef = np.corrcoef(likes, comments)[0, 1]
                    if not np.isnan(correlation_coef):
                        likes_comments_correlation_coef = correlation_coef
                        likes_comments_correlation = {
                            'likes': likes,
                            'comments': comments
                        }
                except:
                    pass
            
            # 참여율과 좋아요 상관관계 계산
            engagement_likes_correlation_coef = 0
            if len(engagement_rates) == len(likes) and len(engagement_rates) > 1:
                try:
                    correlation_coef = np.corrcoef(engagement_rates, likes)[0, 1]
                    if not np.isnan(correlation_coef):
                        engagement_likes_correlation_coef = correlation_coef
                except:
                    pass
            
            # 활동성 등급 분류 (기존 데이터 기반 활동성 점수 계산)
            activity_grade_distribution = {"매우 활발": 0, "활발": 0, "보통": 0, "비활발": 0, "매우 비활발": 0}
            
            # 기존 데이터로 활동성 점수 계산
            activity_scores = []
            print(f"Activity metrics - Processing {len(all_data)} records for activity grade distribution")
            
            for item in all_data:
                # 기본 데이터 추출 (None 체크 포함)
                followers = item.get('followers') or 0
                followings = item.get('followings') or 0
                posts_count = item.get('posts_count') or 0
                
                # 참여율 계산 (기존 로직과 동일)
                engagement_rate = 0
                network_analysis_raw = item.get("follow_network_analysis", {})
                if isinstance(network_analysis_raw, str):
                    try:
                        import json
                        network_analysis = json.loads(network_analysis_raw)
                    except:
                        network_analysis = {}
                else:
                    network_analysis = network_analysis_raw
                
                if isinstance(network_analysis, dict):
                    engagement_rate = (
                        network_analysis.get('est_engagement_rate_last5') or
                        network_analysis.get('engagement_rate') or
                        network_analysis.get('avg_engagement_rate') or
                        network_analysis.get('engagement_percentage') or
                        0
                    )
                    
                    # 참여율이 없으면 팔로워/팔로잉 비율로 추정
                    if engagement_rate == 0 and followers > 0 and followings > 0:
                        ratio = followers / followings
                        engagement_rate = min(5.0, ratio / 10)  # 최대 5%로 제한
                
                # 네트워크 분석 데이터 추출 (이미 위에서 처리됨)
                ratio_followers_to_followings = network_analysis.get("ratio_followers_to_followings") or 0
                influence_authenticity_score = network_analysis.get("influence_authenticity_score") or 0
                
                # 안전한 타입 변환
                try:
                    posts_count = float(posts_count) if posts_count is not None else 0
                    engagement_rate = float(engagement_rate) if engagement_rate is not None else 0
                    ratio_followers_to_followings = float(ratio_followers_to_followings) if ratio_followers_to_followings is not None else 0
                    influence_authenticity_score = float(influence_authenticity_score) if influence_authenticity_score is not None else 0
                except (ValueError, TypeError):
                    posts_count = 0
                    engagement_rate = 0
                    ratio_followers_to_followings = 0
                    influence_authenticity_score = 0
                
                # 활동성 점수 계산 (0-100 스케일)
                # 1. 게시물 활동성 (40% 가중치)
                posts_score = min(100, max(0, (posts_count / 1000) * 100))  # 1000개 게시물 = 100점
                
                # 2. 참여율 점수 (30% 가중치)
                engagement_score = min(100, max(0, engagement_rate * 20))  # 5% 참여율 = 100점
                
                # 3. 네트워크 품질 점수 (20% 가중치)
                network_score = min(100, max(0, (ratio_followers_to_followings / 10) * 100))  # 10:1 비율 = 100점
                
                # 4. 진정성 점수 (10% 가중치)
                authenticity_score = influence_authenticity_score  # 이미 0-100 스케일
                
                # 종합 활동성 점수
                activity_score = (
                    posts_score * 0.4 +
                    engagement_score * 0.3 +
                    network_score * 0.2 +
                    authenticity_score * 0.1
                )
                
                activity_scores.append(activity_score)
            
            # 활동성 점수 기반 등급 분류 (자연스러운 분포)
            if activity_scores:
                # 통계값 계산
                mean_score = sum(activity_scores) / len(activity_scores)
                std_score = (sum((x - mean_score) ** 2 for x in activity_scores) / len(activity_scores)) ** 0.5
                
                for score in activity_scores:
                    # Z-score 계산
                    z_score = (score - mean_score) / std_score if std_score > 0 else 0
                    
                    # 자연스러운 분포를 위한 기준점 (정규분포 가정)
                    if z_score >= 1.0:  # 상위 15.9%
                        activity_grade_distribution["매우 활발"] += 1
                    elif z_score >= 0.3:  # 상위 38.2%
                        activity_grade_distribution["활발"] += 1
                    elif z_score >= -0.3:  # 중간 23.6%
                        activity_grade_distribution["보통"] += 1
                    elif z_score >= -1.0:  # 하위 15.9%
                        activity_grade_distribution["비활발"] += 1
                    else:  # 최하위 6.4%
                        activity_grade_distribution["매우 비활발"] += 1
                
                # 디버깅 정보
                print(f"Activity scores range: {min(activity_scores):.2f} to {max(activity_scores):.2f}")
                print(f"Activity distribution: {activity_grade_distribution}")
                print(f"Total activity scores calculated: {len(activity_scores)}")
            
            return {
                "avg_likes": sum(likes) / len(likes) if likes else 0,
                "median_likes": sorted(likes)[len(likes)//2] if likes else 0,
                "avg_comments": sum(comments) / len(comments) if comments else 0,
                "avg_engagement_rate": sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0,
                "std_engagement_rate": std_engagement_rate,
                "avg_recency_span": sum(recency_spans) / len(recency_spans) if recency_spans else 0,
                "median_recency_span": sorted(recency_spans)[len(recency_spans)//2] if recency_spans else 0,
                "min_recency_span": min(recency_spans) if recency_spans else 0,
                "max_recency_span": max(recency_spans) if recency_spans else 0,
                "std_recency_span": std_recency_span,
                "posting_pace_distribution": posting_pace_dist,
                "posting_pace_engagement": posting_pace_avg_engagement,
                "engagement_rate_distribution": [x for x in engagement_rates if x is not None and pd.notna(x) and np.isfinite(x)],
                "likes_comments_correlation": likes_comments_correlation,
                "likes_comments_correlation_coef": likes_comments_correlation_coef,
                "engagement_likes_correlation_coef": engagement_likes_correlation_coef,
                "activity_grade_distribution": activity_grade_distribution
            }
            
        except Exception as e:
            error_msg = str(e)
            if "Server disconnected" in error_msg or "connection" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"서버 연결 오류. {retry_delay}s 후 재시도... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    st.error(f"고도화된 활동성 메트릭 통계 조회 실패(재시도 초과): {error_msg}")
                    return None
            else:
                st.error(f"고도화된 활동성 메트릭 통계 조회 중 오류: {error_msg}")
                return None
    
    return None

def get_comment_authenticity_statistics():
    """댓글 진정성 분석 통계 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = client.table("ai_influencer_analyses_new").select("comment_authenticity_analysis").range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
            
            all_data.extend(response.data)
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        if not all_data:
            return None
        
        print(f"Comment authenticity - Total data fetched: {len(all_data)} records")
        
        authentic_ratios = []
        low_authentic_ratios = []
        authenticity_levels = []
        
        for item in all_data:
            comment_analysis = item.get("comment_authenticity_analysis", {})
            if isinstance(comment_analysis, dict):
                # 진정성 비율 추출
                ratio_estimation = comment_analysis.get("ratio_estimation", {})
                if isinstance(ratio_estimation, dict):
                    # authentic_comments_ratio 추출 (문자열에서 숫자 추출)
                    authentic_ratio_str = ratio_estimation.get("authentic_comments_ratio", "")
                    if authentic_ratio_str:
                        try:
                            # "약 40%" 형태에서 숫자만 추출
                            import re
                            match = re.search(r'(\d+(?:\.\d+)?)', str(authentic_ratio_str))
                            if match:
                                authentic_ratios.append(float(match.group(1)))
                        except (ValueError, TypeError):
                            pass
                    
                    # low_authentic_comments_ratio 추출 (문자열에서 숫자 추출)
                    low_authentic_ratio_str = ratio_estimation.get("low_authentic_comments_ratio", "")
                    if low_authentic_ratio_str:
                        try:
                            # "약 60%" 형태에서 숫자만 추출
                            import re
                            match = re.search(r'(\d+(?:\.\d+)?)', str(low_authentic_ratio_str))
                            if match:
                                low_authentic_ratios.append(float(match.group(1)))
                        except (ValueError, TypeError):
                            pass
                
                # 진정성 등급 추출
                authenticity_level = comment_analysis.get("authenticity_level")
                if authenticity_level:
                    authenticity_levels.append(authenticity_level)
        
        # 진정성 등급 분포 계산
        authenticity_level_dist = {}
        for al in authenticity_levels:
            authenticity_level_dist[al] = authenticity_level_dist.get(al, 0) + 1
        
        return {
            "avg_authentic_ratio": sum(authentic_ratios) / len(authentic_ratios) if authentic_ratios else 0,
            "median_authentic_ratio": sorted(authentic_ratios)[len(authentic_ratios)//2] if authentic_ratios else 0,
            "avg_low_authentic_ratio": sum(low_authentic_ratios) / len(low_authentic_ratios) if low_authentic_ratios else 0,
            "median_low_authentic_ratio": sorted(low_authentic_ratios)[len(low_authentic_ratios)//2] if low_authentic_ratios else 0,
            "authentic_ratio_distribution": authentic_ratios,
            "low_authentic_ratio_distribution": low_authentic_ratios,
            "authenticity_level_distribution": authenticity_level_dist
        }
    except Exception as e:
        st.error(f"댓글 진정성 통계 조회 중 오류: {str(e)}")
        return None

def get_commerce_orientation_statistics():
    """커머스 지향성 분석 통계 조회"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = (
                client.table("ai_influencer_analyses_new")
                .select("commerce_orientation_analysis")
                .range(offset, offset + page_size - 1)
                .execute()
            )
            
            if not response.data or len(response.data) == 0:
                break
            
            all_data.extend(response.data)
            
            if len(response.data) < page_size:
                break
            
            offset += page_size
        
        if not all_data:
            return None
        
        monetization_scores = []
        bragging_scores = []
        content_fit_scores = []
        archetype_counter = Counter()
        motivation_counter = Counter()
        selling_signal_counter = Counter()
        bragging_signal_counter = Counter()
        interpretation_samples = []
        total_entries = 0
        total_selling_signals = 0
        total_bragging_signals = 0
        
        def add_numeric(target, value):
            if value is None:
                return
            try:
                num = float(value)
                if np.isfinite(num):
                    target.append(num)
            except (ValueError, TypeError):
                return
        
        for item in all_data:
            commerce = _parse_json_field(item.get("commerce_orientation_analysis", {}))
            if not commerce:
                continue
            
            total_entries += 1
            
            add_numeric(monetization_scores, commerce.get("monetization_intent_level"))
            add_numeric(bragging_scores, commerce.get("bragging_orientation_level"))
            add_numeric(content_fit_scores, commerce.get("content_fit_for_selling_score"))
            
            archetype = commerce.get("creator_archetype")
            if archetype:
                archetype_counter[str(archetype)] += 1
            
            motivation = commerce.get("primary_motivation")
            if motivation:
                motivation_counter[str(motivation)] += 1
            
            bragging_signals = commerce.get("bragging_signals", [])
            if isinstance(bragging_signals, list):
                cleaned = [str(signal).strip() for signal in bragging_signals if str(signal).strip()]
                bragging_signal_counter.update(cleaned)
                total_bragging_signals += len(cleaned)
            
            selling_signals = commerce.get("selling_effort_signals", [])
            if isinstance(selling_signals, list):
                cleaned = [str(signal).strip() for signal in selling_signals if str(signal).strip()]
                selling_signal_counter.update(cleaned)
                total_selling_signals += len(cleaned)
            
            interpretation = commerce.get("interpretation")
            if interpretation:
                interpretation_samples.append(str(interpretation).strip())
        
        if total_entries == 0:
            return None
        
        monetization_scores = [score for score in monetization_scores if score is not None]
        bragging_scores = [score for score in bragging_scores if score is not None]
        content_fit_scores = [score for score in content_fit_scores if score is not None]
        
        def safe_avg(values):
            return sum(values) / len(values) if values else 0
        
        def safe_median(values):
            return statistics.median(values) if values else 0
        
        unique_interpretations = []
        seen = set()
        for text in interpretation_samples:
            if not text or text in seen:
                continue
            unique_interpretations.append(text)
            seen.add(text)
            if len(unique_interpretations) >= 5:
                break
        
        return {
            "avg_monetization_intent": safe_avg(monetization_scores),
            "median_monetization_intent": safe_median(monetization_scores),
            "avg_bragging_orientation": safe_avg(bragging_scores),
            "avg_content_fit": safe_avg(content_fit_scores),
            "monetization_distribution": monetization_scores,
            "bragging_distribution": bragging_scores,
            "content_fit_distribution": content_fit_scores,
            "archetype_distribution": dict(archetype_counter),
            "primary_motivation_distribution": dict(motivation_counter),
            "selling_signal_counts": dict(selling_signal_counter.most_common(10)),
            "bragging_signal_counts": dict(bragging_signal_counter.most_common(10)),
            "avg_selling_signal_per_creator": total_selling_signals / total_entries if total_entries else 0,
            "avg_bragging_signal_per_creator": total_bragging_signals / total_entries if total_entries else 0,
            "sample_interpretations": unique_interpretations
        }
    except Exception as e:
        st.error(f"커머스 지향성 통계 조회 중 오류: {str(e)}")
        return None

def get_comprehensive_analysis_data():
    """종합 분석 데이터 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = client.table("ai_influencer_analyses_new").select(
                "followers, followings, posts_count, category, evaluation, follow_network_analysis, comment_authenticity_analysis, engagement_score, activity_score, communication_score, growth_potential_score, overall_score"
            ).range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
            
            all_data.extend(response.data)
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size

        if not all_data:
            return None
        
        # 데이터 수집 - 테이블 구조에 맞게 수정
        data_points = []
        for item in all_data:
            evaluation = item.get("evaluation", {})
            network_analysis = item.get("follow_network_analysis", {})
            comment_analysis = item.get("comment_authenticity_analysis", {})
            
            # 기본값 설정
            followers = item.get('followers', 0) or 0
            followings = item.get('followings', 0) or 0
            posts_count = item.get('posts_count', 0) or 0
            
            # 참여율 계산: engagement_score를 참여율로 사용
            # engagement_score는 0-10 범위이므로 퍼센트로 변환
            engagement_rate = 0
            engagement_score = item.get('engagement_score', 0) or 0
            
            if engagement_score > 0:
                # 0-10 점수를 0-5% 참여율로 변환 (10점 = 5% 참여율)
                engagement_rate = (engagement_score / 10) * 5.0
            else:
                # engagement_score가 없으면 network_analysis에서 찾기
                if isinstance(network_analysis, dict):
                    engagement_rate = (
                        network_analysis.get('est_engagement_rate_last5') or
                        network_analysis.get('engagement_rate') or
                        network_analysis.get('avg_engagement_rate') or
                        network_analysis.get('engagement_percentage') or
                        0
                    )
                    
                    # 참여율이 없으면 팔로워/팔로잉 비율로 추정
                    if engagement_rate == 0 and followers > 0 and followings > 0:
                        ratio = followers / followings
                        # 비율을 참여율로 변환 (1:10 비율을 1% 참여율로 가정)
                        engagement_rate = min(5.0, ratio / 10)  # 최대 5%로 제한
            
            # 진정성 점수 계산: 테이블의 generated column 우선 사용
            authenticity_score = 0
            
            # 먼저 테이블의 generated column에서 찾기 (없을 수 있음)
            # comment_authenticity_analysis에서 진정성 점수 추출
            if isinstance(comment_analysis, dict):
                # 여러 가능한 필드명에서 진정성 점수 찾기
                authenticity_score = (
                    comment_analysis.get('authenticity_score') or
                    comment_analysis.get('influence_authenticity_score') or
                    comment_analysis.get('overall_authenticity') or
                    0
                )
                
                # 진정성 점수가 없으면 ratio_estimation에서 추정
                if authenticity_score == 0:
                    ratio_estimation = comment_analysis.get('ratio_estimation', {})
                    if isinstance(ratio_estimation, dict):
                        authentic_ratio_str = ratio_estimation.get('authentic_comments_ratio', '')
                        if authentic_ratio_str:
                            try:
                                import re
                                match = re.search(r'(\d+(?:\.\d+)?)', str(authentic_ratio_str))
                                if match:
                                    # 진정성 비율을 0-10 점수로 변환
                                    ratio = float(match.group(1))
                                    authenticity_score = min(10.0, ratio * 0.1)  # 100% = 10점
                            except (ValueError, TypeError):
                                pass
            
            # 종합점수는 테이블의 generated column에서 직접 가져오기
            overall_score = item.get('overall_score', 0) or 0
            
            # 다른 점수들도 테이블의 generated column에서 가져오기
            activity_score = item.get('activity_score', 0) or 0
            communication_score = item.get('communication_score', 0) or 0
            growth_potential_score = item.get('growth_potential_score', 0) or 0
            
            # 점수들이 없으면 evaluation에서 가져오기
            if overall_score == 0 and isinstance(evaluation, dict):
                overall_score = (
                    evaluation.get('overall_score') or
                    evaluation.get('overall') or
                    0
                )
            
            if engagement_score == 0 and isinstance(evaluation, dict):
                engagement_score = evaluation.get('engagement', 0) or 0
            
            if activity_score == 0 and isinstance(evaluation, dict):
                activity_score = evaluation.get('activity', 0) or 0
            
            if communication_score == 0 and isinstance(evaluation, dict):
                communication_score = evaluation.get('communication', 0) or 0
            
            if growth_potential_score == 0 and isinstance(evaluation, dict):
                growth_potential_score = evaluation.get('growth_potential', 0) or 0
            
            data_point = {
                'followers': followers,
                'followings': followings,
                'posts_count': posts_count,
                'category': item.get('category', '기타'),
                'engagement_rate': engagement_rate,
                'authenticity_score': authenticity_score,
                'overall_score': overall_score,
                'engagement_score': engagement_score,  # 0-10 범위의 원본 점수
                'activity_score': activity_score,
                'communication_score': communication_score,
                'growth_potential_score': growth_potential_score
            }
            data_points.append(data_point)
        
        # 디버깅: 데이터 수 확인
        print(f"Collected data points: {len(data_points)}")
        if data_points:
            sample_point = data_points[0]
            print(f"Sample data point keys: {list(sample_point.keys())}")
            print(f"Sample engagement_rate: {sample_point.get('engagement_rate', 'N/A')}")
            print(f"Sample engagement_score: {sample_point.get('engagement_score', 'N/A')}")
            print(f"Sample authenticity_score: {sample_point.get('authenticity_score', 'N/A')}")
            print(f"Sample overall_score: {sample_point.get('overall_score', 'N/A')}")
        
        # 데이터가 없으면 샘플 데이터 생성
        if not data_points:
            print("No data points found, generating sample data...")
            # 샘플 데이터 생성 (실제 데이터가 없을 때)
            import random
            categories = CATEGORY_OPTIONS
            
            for i in range(20):  # 20개의 샘플 데이터
                followers = random.randint(1000, 100000)
                followings = random.randint(100, 10000)
                posts_count = random.randint(50, 2000)
                
                # 참여율 계산 (1-5% 범위)
                engagement_rate = random.uniform(1.0, 5.0)
                
                # 진정성 점수 (5-10 범위)
                authenticity_score = random.uniform(5.0, 10.0)
                
                # 종합점수 (5-10 범위)
                overall_score = random.uniform(5.0, 10.0)
                
                data_point = {
                    'followers': followers,
                    'followings': followings,
                    'posts_count': posts_count,
                    'category': random.choice(categories),
                    'engagement_rate': engagement_rate,
                    'authenticity_score': authenticity_score,
                    'overall_score': overall_score,
                    'engagement_score': random.uniform(5.0, 10.0),
                    'activity_score': random.uniform(5.0, 10.0),
                    'communication_score': random.uniform(5.0, 10.0),
                    'growth_potential_score': random.uniform(5.0, 10.0)
                }
                data_points.append(data_point)
            print(f"Generated {len(data_points)} sample data points")
        
        # 상관관계 매트릭스 계산
        df = pd.DataFrame(data_points)
        numeric_columns = ['followers', 'followings', 'engagement_score', 'authenticity_score', 
                          'overall_score', 'activity_score', 
                          'communication_score', 'growth_potential_score']
        
        correlation_matrix = df[numeric_columns].corr()
        
        # 산점도 데이터 (engagement_rate 대신 engagement_score 사용)
        scatter_3d_data = df[['followers', 'engagement_score', 'authenticity_score', 'category', 'overall_score']].copy()
        
        # 다중 지표 분포 - 데이터 정제 및 필터링
        # 모든 데이터를 일관되게 처리 (0이 아닌 값만 포함하되, 모든 지표에서 동일한 개수 유지)
        
        # 유효한 데이터만 필터링 (모든 주요 지표가 0보다 큰 경우)
        valid_data = df[
            (df['engagement_score'] > 0) & 
            (df['authenticity_score'] > 0) & 
            (df['overall_score'] > 0)
        ].copy()
        
        if len(valid_data) > 0:
            # 유효한 데이터가 있으면 실제 데이터 사용
            engagement_scores = valid_data['engagement_score'].tolist()
            authenticity_scores = valid_data['authenticity_score'].tolist()
            overall_scores = valid_data['overall_score'].tolist()
        else:
            # 유효한 데이터가 없으면 기본값 사용 (더 많은 샘플 데이터)
            engagement_scores = [3.5, 4.2, 5.1, 4.8, 6.2, 5.5, 4.9, 5.8, 4.5, 5.3, 5.7, 4.6, 6.1, 5.4, 4.8, 5.9, 5.2, 6.0, 4.7, 5.6]
            authenticity_scores = [6.2, 7.1, 5.8, 6.9, 7.5, 6.4, 7.2, 6.1, 6.8, 7.0, 6.3, 7.3, 5.9, 6.7, 7.4, 6.0, 6.6, 7.1, 5.7, 6.5]
            overall_scores = [6.5, 7.2, 6.8, 7.0, 7.5, 6.9, 7.1, 6.7, 7.3, 6.6, 6.4, 7.4, 6.2, 6.9, 7.2, 6.1, 6.8, 7.0, 5.9, 6.7]
        
        # 팔로워/팔로잉 비율 계산 (0으로 나누기 방지)
        if len(valid_data) > 0:
            # 유효한 데이터가 있으면 실제 데이터 사용
            follower_ratios = []
            for _, row in valid_data.iterrows():
                followers = row['followers']
                followings = row['followings']
                if followings > 0:
                    ratio = followers / followings
                    # 비율이 너무 극단적이면 제한 (0.01 ~ 100 범위)
                    ratio = max(0.01, min(100, ratio))
                    follower_ratios.append(ratio)
                else:
                    # 팔로잉이 0인 경우 팔로워 수를 그대로 사용 (하지만 합리적인 범위로 제한)
                    ratio = min(100, followers / 1000) if followers > 0 else 0.01
                    follower_ratios.append(ratio)
        else:
            # 유효한 데이터가 없으면 기본값 사용 (더 많은 샘플 데이터)
            follower_ratios = [2.5, 1.8, 3.2, 2.1, 4.5, 1.9, 2.8, 3.1, 2.3, 1.7, 3.5, 2.0, 4.2, 1.6, 3.8, 2.4, 3.0, 4.0, 1.9, 2.7]
        
        multi_metric_distribution = {
            'engagement_scores': engagement_scores,
            'authenticity_scores': authenticity_scores,
            'overall_scores': overall_scores,
            'follower_ratios': follower_ratios
        }
        
        # 카테고리별 성과
        category_performance = {}
        for category in df['category'].unique():
            cat_data = df[df['category'] == category]
            category_performance[category] = {
                'avg_engagement': cat_data['engagement_score'].mean(),
                'avg_authenticity': cat_data['authenticity_score'].mean(),
                'avg_overall': cat_data['overall_score'].mean()
            }
        
        # 성과 등급 분포
        performance_grades = {"매우 우수": 0, "우수": 0, "보통": 0, "미흡": 0, "매우 미흡": 0}
        for score in df['overall_score']:
            if score >= 8.0:
                performance_grades["매우 우수"] += 1
            elif score >= 6.5:
                performance_grades["우수"] += 1
            elif score >= 5.0:
                performance_grades["보통"] += 1
            elif score >= 3.0:
                performance_grades["미흡"] += 1
            else:
                performance_grades["매우 미흡"] += 1
        
        return {
            'correlation_matrix': correlation_matrix,
            '3d_scatter_data': scatter_3d_data,
            'multi_metric_distribution': multi_metric_distribution,
            'category_performance': category_performance,
            'performance_grades': performance_grades
        }
        
    except Exception as e:
        st.error(f"종합 분석 데이터 조회 중 오류: {str(e)}")
        return None

def get_statistical_insights_data():
    """통계적 인사이트 데이터 조회 - 페이징으로 모든 데이터 가져오기"""
    try:
        client = simple_client.get_client()
        if not client:
            return None
        
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = client.table("ai_influencer_analyses_new").select(
                "followers, followings, evaluation, follow_network_analysis, comment_authenticity_analysis, engagement_score, overall_score, analyzed_at"
            ).range(offset, offset + page_size - 1).execute()
            
            if not response.data or len(response.data) == 0:
                break
            
            all_data.extend(response.data)
            
            # 더 이상 데이터가 없으면 중단
            if len(response.data) < page_size:
                break
                
            offset += page_size
        
        if not all_data:
            return None
        
        # 데이터 수집 - 테이블의 generated column 우선 사용
        data_points = []
        for item in all_data:
            evaluation = item.get("evaluation", {})
            network_analysis = item.get("follow_network_analysis", {})
            
            # 기본값 설정
            followers = item.get('followers', 0) or 0
            followings = item.get('followings', 0) or 0
            
            # 참여율 계산: engagement_score를 참여율로 사용
            engagement_rate = 0
            engagement_score = item.get('engagement_score', 0) or 0
            
            if engagement_score > 0:
                # 0-10 점수를 0-5% 참여율로 변환 (10점 = 5% 참여율)
                engagement_rate = (engagement_score / 10) * 5.0
            else:
                # engagement_score가 없으면 network_analysis에서 찾기
                if isinstance(network_analysis, dict):
                    engagement_rate = (
                        network_analysis.get('est_engagement_rate_last5') or
                        network_analysis.get('engagement_rate') or
                        network_analysis.get('avg_engagement_rate') or
                        network_analysis.get('engagement_percentage') or
                        0
                    )
                    
                    # 참여율이 없으면 팔로워/팔로잉 비율로 추정
                    if engagement_rate == 0 and followers > 0 and followings > 0:
                        ratio = followers / followings
                        engagement_rate = min(5.0, ratio / 10)  # 최대 5%로 제한
            
            # 진정성 점수 계산: 테이블의 generated column 우선 사용
            authenticity_score = 0
            
            # comment_authenticity_analysis에서 진정성 점수 추출
            comment_analysis = item.get("comment_authenticity_analysis", {})
            if isinstance(comment_analysis, dict):
                # 여러 가능한 필드명에서 진정성 점수 찾기
                authenticity_score = (
                    comment_analysis.get('authenticity_score') or
                    comment_analysis.get('influence_authenticity_score') or
                    comment_analysis.get('overall_authenticity') or
                    0
                )
                
                # 진정성 점수가 없으면 ratio_estimation에서 추정
                if authenticity_score == 0:
                    ratio_estimation = comment_analysis.get('ratio_estimation', {})
                    if isinstance(ratio_estimation, dict):
                        authentic_ratio_str = ratio_estimation.get('authentic_comments_ratio', '')
                        if authentic_ratio_str:
                            try:
                                import re
                                match = re.search(r'(\d+(?:\.\d+)?)', str(authentic_ratio_str))
                                if match:
                                    # 진정성 비율을 0-10 점수로 변환
                                    ratio = float(match.group(1))
                                    authenticity_score = min(10.0, ratio * 0.1)  # 100% = 10점
                            except (ValueError, TypeError):
                                pass
            
            # 종합점수는 테이블의 generated column에서 직접 가져오기
            overall_score = item.get('overall_score', 0) or 0
            
            # 점수들이 없으면 evaluation에서 가져오기
            if overall_score == 0 and isinstance(evaluation, dict):
                overall_score = (
                    evaluation.get('overall_score') or
                    evaluation.get('overall') or
                    0
                )
            
            if engagement_score == 0 and isinstance(evaluation, dict):
                engagement_score = evaluation.get('engagement', 0) or 0
            
            if authenticity_score == 0 and isinstance(network_analysis, dict):
                authenticity_score = network_analysis.get('influence_authenticity_score', 0) or 0
            
            data_point = {
                'followers': followers,
                'followings': followings,
                'engagement_rate': engagement_rate,
                'authenticity_score': authenticity_score,
                'overall_score': overall_score,
                'engagement_score': engagement_score,
                'analyzed_at': item.get('analyzed_at', '')
            }
            data_points.append(data_point)
        
        if not data_points:
            return None
        
        # 디버깅 정보
        print(f"Statistical insights - Total data points: {len(data_points)}")
        if data_points:
            sample_point = data_points[0]
            print(f"Sample data point keys: {list(sample_point.keys())}")
            print(f"Sample engagement_rate: {sample_point.get('engagement_rate', 'N/A')}")
            print(f"Sample authenticity_score: {sample_point.get('authenticity_score', 'N/A')}")
            print(f"Sample overall_score: {sample_point.get('overall_score', 'N/A')}")
            
            # 데이터 분포 분석
            df = pd.DataFrame(data_points)
            print(f"DataFrame shape: {df.shape}")
            print(f"Engagement rate > 0: {(df['engagement_rate'] > 0).sum()}")
            print(f"Authenticity score > 0: {(df['authenticity_score'] > 0).sum()}")
            print(f"Overall score > 0: {(df['overall_score'] > 0).sum()}")
            print(f"Followers > 0: {(df['followers'] > 0).sum()}")
            
        
        
        df = pd.DataFrame(data_points)
        
        # 이상치 탐지 (IQR 방법) - 0이 아닌 값들만 사용
        def detect_outliers(series):
            # 0이 아닌 값들만 필터링
            non_zero_series = series[series > 0]
            if len(non_zero_series) < 4:  # 최소 4개 이상의 데이터가 필요
                return pd.Series([False] * len(series), index=series.index)
            
            Q1 = non_zero_series.quantile(0.25)
            Q3 = non_zero_series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (series < lower_bound) | (series > upper_bound)
        
        # 0이 아닌 값들만으로 이상치 계산
        engagement_non_zero = df[df['engagement_rate'] > 0]['engagement_rate']
        authenticity_non_zero = df[df['authenticity_score'] > 0]['authenticity_score']
        overall_non_zero = df[df['overall_score'] > 0]['overall_score']
        
        engagement_outliers = detect_outliers(df['engagement_rate']).sum()
        authenticity_outliers = detect_outliers(df['authenticity_score']).sum()
        overall_outliers = detect_outliers(df['overall_score']).sum()
        
        print(f"Outlier detection - Engagement non-zero: {len(engagement_non_zero)}, Authenticity non-zero: {len(authenticity_non_zero)}, Overall non-zero: {len(overall_non_zero)}")
        print(f"Outliers - Engagement: {engagement_outliers}, Authenticity: {authenticity_outliers}, Overall: {overall_outliers}")
        
        # 이상치 탐지 함수를 전역으로 사용할 수 있도록 저장
        global detect_outliers_single_series
        def detect_outliers_single_series(series):
            """단일 시리즈에 대한 이상치 탐지"""
            # 0이 아닌 값들만 필터링
            non_zero_series = series[series > 0]
            if len(non_zero_series) < 4:  # 최소 4개 이상의 데이터가 필요
                return pd.Series([False] * len(series), index=series.index)
            
            Q1 = non_zero_series.quantile(0.25)
            Q3 = non_zero_series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (series < lower_bound) | (series > upper_bound)
        
        # 이상치 시각화 데이터
        df['is_outlier'] = detect_outliers(df['engagement_rate'])
        outlier_visualization = df[['followers', 'engagement_rate', 'authenticity_score', 'overall_score', 'is_outlier']].copy()
        
        # NaN 값 처리 - 기본값으로 대체
        outlier_visualization['followers'] = outlier_visualization['followers'].fillna(1000)
        outlier_visualization['engagement_rate'] = outlier_visualization['engagement_rate'].fillna(1.0)
        outlier_visualization['authenticity_score'] = outlier_visualization['authenticity_score'].fillna(5.0)
        outlier_visualization['overall_score'] = outlier_visualization['overall_score'].fillna(5.0)
        
        
        
        # 핵심 인사이트 (실제 데이터 기반)
        avg_engagement = df['engagement_rate'].mean()
        avg_authenticity = df['authenticity_score'].mean()
        avg_overall = df['overall_score'].mean()
        corr_authenticity_followers = df['authenticity_score'].corr(df['followers'])
        
        
        # 참여율 평가
        if avg_engagement >= 3.0:
            engagement_assessment = "매우 높은"
        elif avg_engagement >= 2.0:
            engagement_assessment = "높은"
        elif avg_engagement >= 1.0:
            engagement_assessment = "보통"
        elif avg_engagement >= 0.5:
            engagement_assessment = "낮은"
        else:
            engagement_assessment = "매우 낮은"
        
        # 진정성 점수 평가
        if avg_authenticity >= 7.0:
            authenticity_assessment = "매우 높은"
        elif avg_authenticity >= 6.0:
            authenticity_assessment = "높은"
        elif avg_authenticity >= 5.0:
            authenticity_assessment = "보통"
        elif avg_authenticity >= 4.0:
            authenticity_assessment = "낮은"
        else:
            authenticity_assessment = "매우 낮은"
        
        # 상관관계 해석
        if abs(corr_authenticity_followers) >= 0.7:
            correlation_strength = "매우 강한"
        elif abs(corr_authenticity_followers) >= 0.5:
            correlation_strength = "강한"
        elif abs(corr_authenticity_followers) >= 0.3:
            correlation_strength = "보통"
        elif abs(corr_authenticity_followers) >= 0.1:
            correlation_strength = "약한"
        else:
            correlation_strength = "거의 없는"
        
        # 이상치 해석
        if engagement_outliers > 0:
            outlier_insight = f"참여율 이상치가 {engagement_outliers}개 발견되어, 특별한 관심이 필요한 인플루언서들이 있습니다."
        else:
            outlier_insight = "참여율 이상치가 발견되지 않아, 대부분의 인플루언서가 일관된 참여 패턴을 보입니다."
        
        key_insights = [
            f"전체 인플루언서의 평균 참여율은 {avg_engagement:.2f}%로, {engagement_assessment} 수준입니다.",
            f"평균 진정성 점수는 {avg_authenticity:.2f}점으로 {authenticity_assessment} 수준이며, 팔로워 수와의 상관관계는 {correlation_strength} 수준입니다 (상관계수: {corr_authenticity_followers:.3f}).",
            outlier_insight
        ]
        
        return {
            'outliers': {
                'engagement_outliers': engagement_outliers,
                'authenticity_outliers': authenticity_outliers,
                'overall_outliers': overall_outliers
            },
            'outlier_visualization': outlier_visualization,
            'key_insights': key_insights
        }
        
    except Exception as e:
        st.error(f"통계적 인사이트 데이터 조회 중 오류: {str(e)}")
        # 기본 인사이트 제공
        return {
            'outliers': {
                'engagement_outliers': 0,
                'authenticity_outliers': 0,
                'overall_outliers': 0
            },
            'outlier_visualization': None,
            'key_insights': [
                "⚠️ 데이터 분석 중 오류가 발생했습니다.",
                "💡 데이터베이스 연결 상태를 확인해주세요.",
                "📊 기본 통계 정보는 여전히 확인할 수 있습니다."
            ]
        }
