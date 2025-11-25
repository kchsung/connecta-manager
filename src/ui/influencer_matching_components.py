"""
인플루언서 매칭 관련 컴포넌트들
"""
import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, List, Optional
from ..db.database import db_manager
from ..utils.gemini_client import analyze_campaign_with_gemini, generate_proposal_with_gemini, generate_proposal_with_openai
from ..supabase.simple_client import simple_client


def render_influencer_matching():
    """인플루언서 매칭 메인 컴포넌트"""
    st.subheader("🎯 인플루언서 매칭")
    st.markdown("캠페인에 적합한 인플루언서를 자동으로 매칭하고 제안서를 생성합니다.")
    
    # 탭으로 분리
    tab_names = ["🤖 인공지능 캠페인 분석", "🎯 캠페인별 인플루언서 매칭"]
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        render_campaign_analysis_tab()
    
    with tabs[1]:
        render_influencer_matching_tab()


def render_campaign_selection():
    """캠페인 선택 탭"""
    st.markdown("### 📋 캠페인 선택")
    st.markdown("매칭할 캠페인을 선택하고 필요한 인플루언서 수를 입력하세요.")
    
    # 캠페인 목록 조회
    try:
        campaigns = db_manager.get_campaigns()
        
        if not campaigns:
            st.warning("등록된 캠페인이 없습니다. 먼저 캠페인을 등록해주세요.")
            return
        
        # 캠페인 선택
        campaign_options = {
            f"{camp['campaign_name']} (ID: {camp['id']})": camp 
            for camp in campaigns
        }
        
        selected_campaign_label = st.selectbox(
            "캠페인 선택",
            options=list(campaign_options.keys()),
            key="matching_campaign_select",
            help="매칭할 캠페인을 선택하세요"
        )
        
        if selected_campaign_label:
            selected_campaign = campaign_options[selected_campaign_label]
            
            # 선택된 캠페인 정보 표시
            st.markdown("---")
            st.markdown("#### 📝 선택된 캠페인 정보")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**캠페인명:** {selected_campaign.get('campaign_name', 'N/A')}")
                st.markdown(f"**타입:** {selected_campaign.get('campaign_type', 'N/A')}")
                st.markdown(f"**상태:** {selected_campaign.get('status', 'N/A')}")
            
            with col2:
                st.markdown(f"**시작일:** {selected_campaign.get('start_date', 'N/A')}")
                st.markdown(f"**종료일:** {selected_campaign.get('end_date', 'N/A')}")
            
            if selected_campaign.get('campaign_description'):
                st.markdown("**설명:**")
                st.text_area(
                    "설명",
                    value=selected_campaign.get('campaign_description', ''),
                    disabled=True,
                    key="selected_campaign_description",
                    label_visibility="collapsed"
                )
            
            if selected_campaign.get('campaign_instructions'):
                st.markdown("**지시사항:**")
                st.text_area(
                    "지시사항",
                    value=selected_campaign.get('campaign_instructions', ''),
                    disabled=True,
                    key="selected_campaign_instructions",
                    label_visibility="collapsed"
                )
            
            # 총 필요 인플루언서 수 입력
            st.markdown("---")
            st.markdown("#### 👥 필요 인플루언서 수")
            required_influencers = st.number_input(
                "총 필요 인플루언서 수",
                min_value=1,
                value=st.session_state.get("matching_required_influencers", 10),
                step=1,
                key="matching_required_influencers_input",
                help="이 캠페인에 필요한 총 인플루언서 수를 입력하세요"
            )
            
            # 세션 상태에 저장
            st.session_state.selected_campaign = selected_campaign
            st.session_state.matching_required_influencers = required_influencers
            
            st.success(f"✅ 캠페인이 선택되었습니다. 필요 인플루언서 수: {required_influencers}명")
    
    except Exception as e:
        st.error(f"캠페인 목록 조회 중 오류: {e}")
        import traceback
        st.code(traceback.format_exc())


def render_campaign_analysis_tab():
    """인공지능 캠페인 분석 탭"""
    st.markdown("### 🤖 인공지능 캠페인 분석")
    
    # 캠페인 목록 조회
    try:
        campaigns = db_manager.get_campaigns()
        
        if not campaigns:
            st.warning("등록된 캠페인이 없습니다. 먼저 캠페인을 등록해주세요.")
            return
        
        # 캠페인 선택
        campaign_options = {
            f"{camp['campaign_name']} (ID: {camp['id']})": camp 
            for camp in campaigns
        }
        
        # 이전에 선택된 캠페인 ID 확인
        previous_campaign_id = None
        if 'selected_campaign' in st.session_state:
            previous_campaign_id = st.session_state.selected_campaign.get('id')
        
        # 기본값 설정
        default_index = 0
        if previous_campaign_id:
            for idx, (label, camp) in enumerate(campaign_options.items()):
                if camp.get('id') == previous_campaign_id:
                    default_index = idx
                    break
        
        selected_campaign_label = st.selectbox(
            "캠페인 선택",
            options=list(campaign_options.keys()),
            index=default_index,
            key="analysis_campaign_select",
            help="분석할 캠페인을 선택하세요"
        )
        
        if not selected_campaign_label:
            return
        
        selected_campaign = campaign_options[selected_campaign_label]
        current_campaign_id = selected_campaign.get('id')
        
        # 캠페인이 변경되었는지 확인
        if previous_campaign_id != current_campaign_id:
            # 캠페인 변경 시 기존 분석 결과 초기화
            if 'campaign_analysis_result' in st.session_state:
                del st.session_state.campaign_analysis_result
            if 'campaign_analysis_campaign_id' in st.session_state:
                del st.session_state.campaign_analysis_campaign_id
            st.info("🔄 캠페인이 변경되어 기존 분석 결과가 초기화되었습니다.")
        
        # 세션 상태에 저장
        st.session_state.selected_campaign = selected_campaign
        
        # 좌우 분할 레이아웃
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            # 선택된 캠페인 정보 표시
            st.markdown("#### 📝 선택된 캠페인 정보")
            
            st.markdown(f"**캠페인명:** {selected_campaign.get('campaign_name', 'N/A')}")
            st.markdown(f"**타입:** {selected_campaign.get('campaign_type', 'N/A')}")
            st.markdown(f"**상태:** {selected_campaign.get('status', 'N/A')}")
            st.markdown(f"**시작일:** {selected_campaign.get('start_date', 'N/A')}")
            st.markdown(f"**종료일:** {selected_campaign.get('end_date', 'N/A')}")
            
            if selected_campaign.get('campaign_description'):
                st.markdown("**설명:**")
                st.text_area(
                    "설명",
                    value=selected_campaign.get('campaign_description', ''),
                    disabled=True,
                    key="analysis_campaign_description",
                    label_visibility="collapsed",
                    height=150
                )
            
            if selected_campaign.get('campaign_instructions'):
                st.markdown("**지시사항:**")
                st.text_area(
                    "지시사항",
                    value=selected_campaign.get('campaign_instructions', ''),
                    disabled=True,
                    key="analysis_campaign_instructions",
                    label_visibility="collapsed",
                    height=150
                )
        
        with col_right:
            # 캠페인 내용 분석
            st.markdown("#### 🔍 캠페인 내용 분석")
            
            # 기존 분석 결과 확인
            campaign_id = selected_campaign.get('id')
            
            # 세션 상태의 분석 결과가 현재 선택된 캠페인과 일치하는지 확인
            analysis_campaign_id = st.session_state.get('campaign_analysis_campaign_id')
            if analysis_campaign_id != campaign_id:
                # 분석 결과가 다른 캠페인 것이거나 없으면 초기화
                if 'campaign_analysis_result' in st.session_state:
                    del st.session_state.campaign_analysis_result
                if 'campaign_analysis_campaign_id' in st.session_state:
                    del st.session_state.campaign_analysis_campaign_id
            
            # 분석 결과가 세션에 없으면 DB에서 조회
            if 'campaign_analysis_result' not in st.session_state and campaign_id:
                existing_analysis = get_campaign_analysis_from_db(campaign_id)
                if existing_analysis and existing_analysis.get('analysis_result'):
                    st.session_state.campaign_analysis_result = existing_analysis.get('analysis_result')
                    st.session_state.campaign_analysis_campaign_id = campaign_id
                    st.info("💾 저장된 분석 결과를 불러왔습니다.")
            
            # 분석 결과가 있으면 표시
            if 'campaign_analysis_result' in st.session_state and st.session_state.get('campaign_analysis_campaign_id') == campaign_id:
                display_campaign_analysis_result()
                
                # 다시 분석 버튼
                if st.button("🔄 다시 분석", type="secondary", key="reanalyze_campaign", use_container_width=True):
                    # 세션 상태 초기화
                    if 'campaign_analysis_result' in st.session_state:
                        del st.session_state.campaign_analysis_result
                    if 'campaign_analysis_campaign_id' in st.session_state:
                        del st.session_state.campaign_analysis_campaign_id
                    # 강제로 다시 분석
                    analyze_campaign(selected_campaign, force_reanalyze=True)
                    st.rerun()
            else:
                # 분석 결과가 없으면 분석 시작 버튼 표시
                if st.button("🔍 캠페인 분석 시작", type="primary", key="start_campaign_analysis", use_container_width=True):
                    analyze_campaign(selected_campaign)
    
    except Exception as e:
        st.error(f"캠페인 목록 조회 중 오류: {e}")
        import traceback
        st.code(traceback.format_exc())


def render_influencer_matching_tab():
    """캠페인별 인플루언서 매칭 탭"""
    st.markdown("### 🎯 캠페인별 인플루언서 매칭")
    
    # 캠페인 목록 조회
    try:
        campaigns = db_manager.get_campaigns()
        
        if not campaigns:
            st.warning("등록된 캠페인이 없습니다. 먼저 캠페인을 등록해주세요.")
            return
        
        # 분석된 캠페인 ID 목록 조회
        analyzed_campaign_ids = get_analyzed_campaign_ids()
        
        # ID를 문자열로 변환하여 비교 (UUID 형식 일치 보장)
        analyzed_campaign_ids_str = [str(cid) for cid in analyzed_campaign_ids]
        
        # 분석된 캠페인만 필터링
        analyzed_campaigns = [
            camp for camp in campaigns 
            if str(camp.get('id')) in analyzed_campaign_ids_str
        ]
        
        if not analyzed_campaigns:
            st.warning("⚠️ 분석된 캠페인이 없습니다. 먼저 '인공지능 캠페인 분석' 탭에서 캠페인을 분석해주세요.")
            return
        
        # 캠페인 선택
        campaign_options = {
            f"{camp['campaign_name']} (ID: {camp['id']})": camp 
            for camp in analyzed_campaigns
        }
        
        # 이전에 선택된 캠페인 ID 확인
        previous_campaign_id = None
        if 'matching_selected_campaign' in st.session_state:
            previous_campaign_id = st.session_state.matching_selected_campaign.get('id')
        
        # 기본값 설정 (이전 선택 캠페인이 필터링된 목록에 있는지 확인)
        default_index = 0
        if previous_campaign_id:
            for idx, (label, camp) in enumerate(campaign_options.items()):
                if camp.get('id') == previous_campaign_id:
                    default_index = idx
                    break
            else:
                # 이전 선택 캠페인이 필터링된 목록에 없으면 기본값 0 사용
                default_index = 0
        
        selected_campaign_label = st.selectbox(
            "캠페인 선택",
            options=list(campaign_options.keys()),
            index=default_index,
            key="matching_campaign_select",
            help="매칭할 캠페인을 선택하세요"
        )
        
        if not selected_campaign_label:
            return
        
        selected_campaign = campaign_options[selected_campaign_label]
        current_campaign_id = selected_campaign.get('id')
        
        # 캠페인이 변경되었는지 확인
        if previous_campaign_id != current_campaign_id:
            # 캠페인 변경 시 기존 매칭 결과 및 분석 결과 초기화
            if 'matched_influencers' in st.session_state:
                del st.session_state.matched_influencers
            if 'matching_analysis_result' in st.session_state:
                del st.session_state.matching_analysis_result
            if 'selected_influencer_for_proposal' in st.session_state:
                del st.session_state.selected_influencer_for_proposal
            if 'generated_proposal' in st.session_state:
                del st.session_state.generated_proposal
            # 분석 결과도 초기화 (다른 캠페인 분석 결과가 남아있을 수 있음)
            if 'campaign_analysis_result' in st.session_state:
                del st.session_state.campaign_analysis_result
            if 'campaign_analysis_campaign_id' in st.session_state:
                del st.session_state.campaign_analysis_campaign_id
        
        # 세션 상태에 저장
        st.session_state.matching_selected_campaign = selected_campaign
        
        # 필요 인플루언서 수 입력
        required_influencers = st.number_input(
            "필요 인플루언서 수",
            min_value=1,
            value=st.session_state.get("matching_required_influencers", 10),
            step=1,
            key="matching_required_influencers_input",
            help="이 캠페인에 필요한 총 인플루언서 수를 입력하세요"
        )
        st.session_state.matching_required_influencers = required_influencers
        
        # 캠페인 분석 결과 확인 (매칭에 필요)
        campaign_id = selected_campaign.get('id')
        
        # 세션 상태의 분석 결과가 현재 선택된 캠페인과 일치하는지 확인
        analysis_campaign_id = st.session_state.get('campaign_analysis_campaign_id')
        if analysis_campaign_id != campaign_id:
            # 분석 결과가 다른 캠페인 것이거나 없으면 초기화
            if 'campaign_analysis_result' in st.session_state:
                del st.session_state.campaign_analysis_result
            if 'campaign_analysis_campaign_id' in st.session_state:
                del st.session_state.campaign_analysis_campaign_id
        
        if campaign_id:
            # 세션 상태에 분석 결과가 없으면 DB에서 조회
            if 'campaign_analysis_result' not in st.session_state:
                existing_analysis = get_campaign_analysis_from_db(campaign_id)
                if existing_analysis and existing_analysis.get('analysis_result'):
                    # 분석 결과가 있으면 매칭 가능
                    st.session_state.campaign_analysis_result = existing_analysis.get('analysis_result')
                    st.session_state.campaign_analysis_campaign_id = campaign_id
                else:
                    st.warning("⚠️ 먼저 '인공지능 캠페인 분석' 탭에서 캠페인을 분석해주세요.")
                    return
            # 세션 상태에 분석 결과가 있지만 다른 캠페인 것이면 경고
            elif st.session_state.get('campaign_analysis_campaign_id') != campaign_id:
                st.warning("⚠️ 먼저 '인공지능 캠페인 분석' 탭에서 캠페인을 분석해주세요.")
                return
        
        # 좌우 분할 레이아웃
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            # 인플루언서 매칭
            st.markdown("#### 👥 인플루언서 매칭")
            
            # 매칭 결과 확인
            matched_influencers = st.session_state.get('matched_influencers', [])
            
            # 매칭 결과가 없거나 비어있으면 매칭 시작 버튼
            if not matched_influencers:
                if st.button("🎯 인플루언서 매칭 시작", type="primary", key="start_influencer_matching", use_container_width=True):
                    match_influencers(required_influencers)
            else:
                # 매칭 결과가 있으면 드롭다운으로 표시
                display_matched_influencers_list_for_matching()
        
        with col_right:
            # 제안서 작성 영역
            st.markdown("#### 📝 제안서 작성")
            display_proposal_area_for_matching(selected_campaign)
    
    except Exception as e:
        st.error(f"캠페인 목록 조회 중 오류: {e}")
        import traceback
        st.code(traceback.format_exc())


def get_analyzed_campaign_ids() -> list:
    """분석된 캠페인 ID 목록 조회 (Edge Function 사용)"""
    try:
        import requests
        import os
        
        supabase_url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_anon_key:
            return []
        
        # Edge Function 호출
        function_url = f"{supabase_url}/functions/v1/ai-influencer-analysis"
        headers = {
            "Authorization": f"Bearer {supabase_anon_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "action": "get_analyzed_campaign_ids"
        }
        
        try:
            response = requests.post(function_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("data"):
                    return result["data"]
        except:
            # 조회 실패는 치명적이지 않으므로 조용히 실패
            pass
        
        return []
    except Exception as e:
        # 조회 실패는 치명적이지 않으므로 조용히 실패
        return []


def get_campaign_analysis_from_db(campaign_id: str) -> Optional[Dict[str, Any]]:
    """Supabase에서 캠페인 분석 결과 조회 (Edge Function 사용)"""
    try:
        import requests
        import os
        
        supabase_url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_anon_key:
            return None
        
        # Edge Function 호출
        function_url = f"{supabase_url}/functions/v1/ai-influencer-analysis"
        headers = {
            "Authorization": f"Bearer {supabase_anon_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "action": "get_campaign_analysis",
            "data": {"campaign_id": campaign_id}
        }
        
        try:
            response = requests.post(function_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("data"):
                    return result["data"]
        except:
            # 조회 실패는 치명적이지 않으므로 조용히 실패
            pass
        
        return None
    except Exception as e:
        # 조회 실패는 치명적이지 않으므로 조용히 실패
        return None


def save_campaign_analysis_to_db(campaign_id: str, analysis_result: Dict[str, Any]) -> bool:
    """캠페인 분석 결과를 Supabase에 저장 (Edge Function 사용)"""
    try:
        import requests
        import os
        
        supabase_url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_anon_key:
            st.error("❌ Supabase URL 또는 API 키가 설정되지 않았습니다.")
            st.info("💡 `.streamlit/secrets.toml` 파일에 `SUPABASE_URL`과 `SUPABASE_ANON_KEY`를 추가해주세요.")
            return False
        
        # Edge Function 호출
        function_url = f"{supabase_url}/functions/v1/ai-influencer-analysis"
        headers = {
            "Authorization": f"Bearer {supabase_anon_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "action": "save_campaign_analysis",
            "data": {
                "campaign_id": campaign_id,
                "analysis_result": analysis_result
            }
        }
        
        try:
            response = requests.post(function_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success", False):
                    return True
                else:
                    error_msg = result.get("error", "알 수 없는 오류")
                    error_details = result.get("details", "")
                    st.error(f"❌ Edge Function 저장 실패: {error_msg}")
                    if error_details:
                        st.error(f"❌ 상세 오류: {error_details}")
                    return False
            else:
                error_text = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get("error", error_text)
                    error_details = error_json.get("details", "")
                except:
                    error_msg = error_text
                    error_details = ""
                st.error(f"❌ Edge Function 호출 실패 (상태 코드: {response.status_code}): {error_msg}")
                if error_details:
                    st.error(f"❌ 상세 오류: {error_details}")
                return False
                
        except requests.exceptions.Timeout:
            st.error("❌ Edge Function 요청 시간 초과 (10초)")
            return False
        except requests.exceptions.ConnectionError as conn_error:
            st.error(f"❌ Edge Function 연결 실패: {str(conn_error)}")
            st.info("💡 네트워크 연결을 확인해주세요.")
            return False
        except requests.exceptions.RequestException as req_error:
            st.error(f"❌ Edge Function 요청 실패: {str(req_error)}")
            import traceback
            st.code(traceback.format_exc())
            return False
        
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ 분석 결과 저장 중 오류: {error_msg}")
        import traceback
        st.code(traceback.format_exc())
        return False


def analyze_campaign(campaign: Dict[str, Any], force_reanalyze: bool = False):
    """캠페인 내용 분석"""
    # OpenAI API 키 확인
    import os
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        try:
            openai_key = st.secrets.get("OPENAI_API_KEY")
        except (KeyError, AttributeError, TypeError):
            openai_key = None
    
    if not openai_key:
        st.error("❌ OpenAI API 키를 찾을 수 없습니다.")
        st.info("💡 `.streamlit/secrets.toml` 파일에 `OPENAI_API_KEY = \"your-api-key\"` 형식으로 추가하고 앱을 재시작해주세요.")
        return
    
    # 강제 재분석이 아니면 기존 분석 결과 확인
    campaign_id = campaign.get('id')
    if not force_reanalyze and campaign_id:
        existing_analysis = get_campaign_analysis_from_db(campaign_id)
        if existing_analysis and existing_analysis.get('analysis_result'):
            st.session_state.campaign_analysis_result = existing_analysis['analysis_result']
            st.session_state.campaign_analysis_campaign_id = campaign_id
            st.info("💾 저장된 분석 결과를 불러왔습니다.")
            return
    
    with st.spinner("캠페인 내용을 분석 중입니다..."):
        # 캠페인 내용 구성
        campaign_content = f"""
캠페인명: {campaign.get('campaign_name', '')}
설명: {campaign.get('campaign_description', '')}
타입: {campaign.get('campaign_type', '')}
지시사항: {campaign.get('campaign_instructions', '')}
태그: {campaign.get('tags', '')}
"""
        
        # OpenAI 프롬프트 ID로 분석
        analysis_result = analyze_campaign_with_gemini(campaign_content)
        
        if analysis_result:
            st.session_state.campaign_analysis_result = analysis_result
            st.session_state.campaign_analysis_campaign_id = campaign_id
            
            # Supabase에 저장
            if campaign_id:
                if save_campaign_analysis_to_db(campaign_id, analysis_result):
                    st.success("✅ 캠페인 분석이 완료되었고 저장되었습니다!")
                else:
                    st.success("✅ 캠페인 분석이 완료되었습니다! (저장 실패)")
            else:
                st.success("✅ 캠페인 분석이 완료되었습니다!")
        else:
            st.error("❌ 캠페인 분석에 실패했습니다.")


def display_campaign_analysis_result():
    """캠페인 분석 결과 표시 (새로운 JSON 형식 지원)"""
    result = st.session_state.campaign_analysis_result
    
    st.markdown("##### 📊 분석 결과")
    
    # 새로운 형식인지 확인 (campaign_summary가 있으면 새로운 형식)
    if 'campaign_summary' in result:
        display_new_format_result(result)
    else:
        # 기존 형식 (하위 호환성)
        display_old_format_result(result)


def display_new_format_result(result: Dict[str, Any]):
    """새로운 JSON 형식 결과 표시"""
    # 1. 캠페인 요약
    if 'campaign_summary' in result:
        summary = result['campaign_summary']
        st.markdown("### 📋 캠페인 요약")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**캠페인명:** {summary.get('campaign_name', 'N/A')}")
            st.markdown(f"**캠페인 타입:** {summary.get('campaign_type', 'N/A')}")
        
        with col2:
            st.markdown(f"**핵심 목표:** {summary.get('core_goal', 'N/A')}")
        
        target_keywords = summary.get('target_keywords', [])
        if target_keywords:
            st.markdown(f"**핵심 키워드:** {', '.join(target_keywords)}")
        else:
            st.markdown("**핵심 키워드:** 없음")
        
        st.markdown("---")
    
    # 2. 이상적인 인플루언서 프로필
    if 'ideal_influencer_profile' in result:
        profile = result['ideal_influencer_profile']
        st.markdown("### 🎯 이상적인 인플루언서 프로필")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**추천 카테고리:** {profile.get('recommended_category', 'N/A')}")
            min_followers = profile.get('min_followers')
            if min_followers:
                st.markdown(f"**최소 팔로워:** {min_followers:,}명")
            else:
                st.markdown("**최소 팔로워:** 제한 없음")
        
        with col2:
            st.markdown(f"**선호 네트워크 타입:** {profile.get('preferred_network_type', 'N/A')}")
            min_trust_score = profile.get('min_trust_score')
            if min_trust_score is not None:
                st.markdown(f"**최소 신뢰 점수:** {min_trust_score}/100")
            else:
                st.markdown("**최소 신뢰 점수:** 제한 없음")
        
        description = profile.get('description', '')
        if description:
            st.markdown("**설명:**")
            st.info(description)
        
        st.markdown("---")
    
    # 3. 캠페인 타입별 가중치
    if 'weights_by_campaign_type' in result:
        weights = result['weights_by_campaign_type']
        st.markdown("### ⚖️ 캠페인 타입별 가중치")
        
        tabs = st.tabs(list(weights.keys()))
        for idx, (campaign_type, weight_data) in enumerate(weights.items()):
            with tabs[idx]:
                st.markdown(f"**{campaign_type.upper()} 캠페인 가중치**")
                
                # 가중치를 시각화
                weight_items = []
                for key, value in weight_data.items():
                    if isinstance(value, (int, float)):
                        weight_items.append({
                            '항목': key.replace('_', ' ').title(),
                            '가중치': f"{value:.2f}",
                            '비율': value
                        })
                
                if weight_items:
                    df = pd.DataFrame(weight_items)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # 가중치 합계 확인
                    total = sum(item['비율'] for item in weight_items)
                    if abs(total - 1.0) > 0.01:
                        st.warning(f"⚠️ 가중치 합계가 1.0이 아닙니다: {total:.2f}")
        
        st.markdown("---")
    
    # 4. 인플루언서 평가 (있는 경우)
    if 'influencer_evaluations' in result and result['influencer_evaluations']:
        evaluations = result['influencer_evaluations']
        st.markdown(f"### 👥 인플루언서 평가 ({len(evaluations)}명)")
        
        # 간단한 요약 테이블
        eval_summary = []
        for eval_item in evaluations[:10]:  # 최대 10개만 표시
            eval_summary.append({
                '이름': eval_item.get('alias', 'N/A'),
                '플랫폼': eval_item.get('platform', 'N/A'),
                '카테고리': eval_item.get('mapped_category', 'N/A'),
                '팔로워': f"{eval_item.get('followers', 0):,}" if eval_item.get('followers') else 'N/A',
                '최종 점수': f"{eval_item.get('final_scores', {}).get('final_score', 0):.1f}" if eval_item.get('final_scores', {}).get('final_score') else 'N/A',
                '추천': eval_item.get('final_scores', {}).get('recommendation_label', 'N/A')
            })
        
        if eval_summary:
            df = pd.DataFrame(eval_summary)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if len(evaluations) > 10:
                st.info(f"💡 총 {len(evaluations)}명 중 상위 10명만 표시됩니다.")


def display_old_format_result(result: Dict[str, Any]):
    """기존 형식 결과 표시 (하위 호환성)"""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**카테고리:** {result.get('category', 'N/A')}")
    
    with col2:
        tags = result.get('recommended_tags', [])
        if tags:
            st.markdown(f"**추천 태그:** {', '.join(tags)}")
        else:
            st.markdown("**추천 태그:** 없음")
    
    if result.get('details'):
        st.markdown("**상세 분석:**")
        st.text_area(
            "상세 분석",
            value=result.get('details', ''),
            disabled=True,
            key="campaign_analysis_details",
            label_visibility="collapsed",
            height=150
        )


def match_influencers(required_count: int):
    """인플루언서 매칭 (정량 기반)"""
    with st.spinner("인플루언서를 매칭 중입니다..."):
        analysis_result = st.session_state.campaign_analysis_result
        
        # 1. 캠페인 파라미터 추출
        if 'ideal_influencer_profile' in analysis_result:
            # 새로운 형식
            profile = analysis_result['ideal_influencer_profile']
            recommended_category = profile.get('recommended_category', '').strip()
            min_followers = profile.get('min_followers', 0) or 0
            min_trust_score_100 = profile.get('min_trust_score')  # 0~100 스케일
            min_trust_score_10 = (min_trust_score_100 / 10.0) if min_trust_score_100 is not None else 0.0
        else:
            # 기존 형식 (기본값 사용)
            recommended_category = analysis_result.get('category', '').strip()
            min_followers = 0
            min_trust_score_10 = 0.0
        
        # 캠페인 타입 및 가중치 추출
        campaign_type = analysis_result.get('campaign_summary', {}).get('campaign_type', 'sales')
        if not campaign_type:
            # 매칭 탭 또는 분석 탭에서 선택된 캠페인 확인
            selected_campaign = st.session_state.get('matching_selected_campaign') or st.session_state.get('selected_campaign')
            if selected_campaign:
                campaign_type = selected_campaign.get('campaign_type', 'sales')
            else:
                campaign_type = 'sales'
        
        # 가중치 추출
        weights_by_type = analysis_result.get('weights_by_campaign_type', {})
        campaign_weights = weights_by_type.get(campaign_type, {})
        
        # 기본 가중치 (sales 캠페인 기준)
        w_conv = campaign_weights.get('conversion_fit_weight', 0.5)
        w_branding = campaign_weights.get('branding_fit_weight', 0.2)
        w_trust = campaign_weights.get('trust_weight', 0.2)
        w_growth = campaign_weights.get('growth_potential_weight', 0.1)
        
        # AI 분석 데이터 조회
        try:
            client = simple_client.get_client()
            if not client:
                st.error("데이터베이스 연결 실패")
                return
            
            # 전체 인플루언서 조회 (새 테이블 사용)
            query = client.table("ai_influencer_analyses_new").select("*")
            response = query.limit(10000).execute()
            all_candidates = response.data if response.data else []
            
            if not all_candidates:
                st.warning("⚠️ 분석된 인플루언서 데이터가 없습니다.")
                return
            
            # 2. 각 인플루언서에 대해 점수 계산
            scored_candidates = []
            
            for candidate in all_candidates:
                # JSON 필드 파싱
                follow_network = candidate.get('follow_network_analysis', {}) or {}
                comment_auth = candidate.get('comment_authenticity_analysis', {}) or {}
                
                # 2-1. 네트워크 신뢰도 점수 계산 (0~10)
                influence_auth_raw = follow_network.get('influence_authenticity_score')
                if influence_auth_raw is None:
                    influence_auth_raw = 0
                else:
                    try:
                        influence_auth_raw = float(influence_auth_raw)
                    except (ValueError, TypeError):
                        influence_auth_raw = 0
                
                ratio_f_f = follow_network.get('ratio_followers_to_followings')
                if ratio_f_f is None:
                    ratio_f_f = 1.0
                else:
                    try:
                        ratio_f_f = float(ratio_f_f)
                    except (ValueError, TypeError):
                        ratio_f_f = 1.0
                
                # influence_auth_raw (0~100) → 0~10으로 스케일
                network_base_score = (influence_auth_raw / 10.0) if influence_auth_raw > 0 else 0
                
                # 팔로워/팔로잉 비율 보정
                ratio_bonus = 0
                if 0.5 <= ratio_f_f <= 3.0:
                    ratio_bonus = 1
                elif 0.3 <= ratio_f_f <= 5.0:
                    ratio_bonus = 0
                else:
                    ratio_bonus = -1
                
                network_trust_score_10 = max(0, min(10, network_base_score + ratio_bonus))
                
                # 2-2. 댓글 진정성 점수 계산 (0~10)
                ratio_estimation = comment_auth.get('ratio_estimation', {}) or {}
                authentic_ratio = ratio_estimation.get('authentic_comments_ratio')
                if authentic_ratio is None:
                    authentic_ratio = 0.0
                else:
                    try:
                        authentic_ratio = float(authentic_ratio)
                    except (ValueError, TypeError):
                        authentic_ratio = 0.0
                
                authenticity_level = comment_auth.get('authenticity_level', '')
                
                # authentic_ratio (0~1) → 0~10으로 스케일
                comment_base_score = authentic_ratio * 10.0
                
                # authenticity_level 보정
                level_bonus = 0
                if authenticity_level == '높음':
                    level_bonus = 2
                elif authenticity_level == '중간':
                    level_bonus = 0
                elif authenticity_level == '낮음':
                    level_bonus = -2
                
                comment_trust_score_10 = max(0, min(10, comment_base_score + level_bonus))
                
                # 2-3. 통합 trust_score (0~10)
                trust_score_10 = round(0.6 * network_trust_score_10 + 0.4 * comment_trust_score_10, 2)
                
                # 2-4. 브랜드/카테고리 적합도 점수 (0~10)
                candidate_category = candidate.get('category', '').strip()
                if candidate_category == recommended_category:
                    brand_fit_score_10 = 10.0
                elif candidate_category in ['웰빙', '푸드', '스포츠']:
                    brand_fit_score_10 = 7.0
                else:
                    brand_fit_score_10 = 4.0
                
                # 2-5. 기존 점수들 가져오기
                engagement_score = candidate.get('engagement_score') or 0.0
                activity_score = candidate.get('activity_score') or 0.0
                overall_score = candidate.get('overall_score') or 0.0
                growth_potential_score = candidate.get('growth_potential_score') or 0.0
                
                try:
                    engagement_score = float(engagement_score)
                    activity_score = float(activity_score)
                    overall_score = float(overall_score)
                    growth_potential_score = float(growth_potential_score)
                except (ValueError, TypeError):
                    engagement_score = 0.0
                    activity_score = 0.0
                    overall_score = 0.0
                    growth_potential_score = 0.0
                
                # 2-6. conversion_fit_score 계산 (0~10)
                conversion_fit_score_10 = round(
                    0.4 * engagement_score +
                    0.3 * overall_score +
                    0.3 * trust_score_10,
                    2
                )
                
                # 2-7. branding_fit_score 계산 (0~10)
                branding_fit_score_10 = round(
                    0.4 * brand_fit_score_10 +
                    0.3 * activity_score +
                    0.2 * engagement_score +
                    0.1 * trust_score_10,
                    2
                )
                
                # 2-8. seeding_fit_score 계산 (0~10)
                seeding_fit_score_10 = round(
                    0.35 * trust_score_10 +
                    0.25 * brand_fit_score_10 +
                    0.2 * activity_score +
                    0.2 * growth_potential_score,
                    2
                )
                
                # 2-9. 캠페인 타입별 최종 점수 계산
                if campaign_type == 'sales':
                    final_score_10 = round(
                        w_conv * conversion_fit_score_10 +
                        w_branding * branding_fit_score_10 +
                        w_trust * trust_score_10 +
                        w_growth * growth_potential_score,
                        2
                    )
                elif campaign_type == 'branding':
                    final_score_10 = round(
                        w_branding * branding_fit_score_10 +
                        w_conv * conversion_fit_score_10 +
                        w_trust * trust_score_10 +
                        w_growth * growth_potential_score,
                        2
                    )
                elif campaign_type == 'seeding':
                    final_score_10 = round(
                        w_trust * trust_score_10 +
                        w_branding * branding_fit_score_10 +
                        w_conv * conversion_fit_score_10 +
                        w_growth * growth_potential_score,
                        2
                    )
                else:
                    # 기본값 (sales와 동일)
                    final_score_10 = round(
                        w_conv * conversion_fit_score_10 +
                        w_branding * branding_fit_score_10 +
                        w_trust * trust_score_10 +
                        w_growth * growth_potential_score,
                        2
                    )
                
                # 점수 정보를 candidate에 추가
                candidate_with_scores = candidate.copy()
                candidate_with_scores.update({
                    'network_trust_score_10': network_trust_score_10,
                    'comment_trust_score_10': comment_trust_score_10,
                    'trust_score_10': trust_score_10,
                    'brand_fit_score_10': brand_fit_score_10,
                    'conversion_fit_score_10': conversion_fit_score_10,
                    'branding_fit_score_10': branding_fit_score_10,
                    'seeding_fit_score_10': seeding_fit_score_10,
                    'final_score_10': final_score_10
                })
                
                scored_candidates.append(candidate_with_scores)
            
            # 3. 필터링 (최소 조건)
            filtered_candidates = []
            for c in scored_candidates:
                # 팔로워 수 확인
                followers = c.get('followers') or 0
                try:
                    followers = int(followers)
                except (ValueError, TypeError):
                    followers = 0
                
                # 신뢰 점수 확인
                trust_score = c.get('trust_score_10', 0)
                
                # 카테고리 필수 매칭 확인
                candidate_category = c.get('category', '').strip()
                category_match = True
                if recommended_category:
                    # recommended_category가 있으면 정확히 일치해야 함
                    category_match = (candidate_category == recommended_category)
                
                # 모든 조건을 만족하는 경우만 포함
                if (followers >= min_followers 
                    and trust_score >= min_trust_score_10 
                    and category_match):
                    filtered_candidates.append(c)
            
            # 4. 최종 점수로 정렬
            filtered_candidates.sort(
                key=lambda x: (x.get('final_score_10', 0), x.get('followers', 0)),
                reverse=True
            )
            
            # 5. 상위 N명 추출 (필요 인플루언서 수의 3배수)
            target_count = required_count * 3
            matched = filtered_candidates[:target_count] if len(filtered_candidates) >= target_count else filtered_candidates
            
            # 6. 세션 상태에 저장
            st.session_state.matched_influencers = matched
            st.session_state.matching_analysis_result = {
                "campaign_type": campaign_type,
                "recommended_category": recommended_category,
                "min_followers": min_followers,
                "min_trust_score_10": min_trust_score_10,
                "total_candidates": len(all_candidates),
                "filtered_candidates": len(filtered_candidates),
                "matched_count": len(matched),
                "weights": {
                    "conversion": w_conv,
                    "branding": w_branding,
                    "trust": w_trust,
                    "growth": w_growth
                }
            }
            
            if len(matched) > 0:
                st.success(f"✅ {len(matched)}명의 인플루언서를 매칭했습니다!")
                # UI 업데이트를 위해 페이지 다시 렌더링
                st.rerun()
            else:
                st.warning(f"⚠️ 매칭된 인플루언서가 없습니다. 필터 조건을 완화하거나 데이터를 확인해주세요.")
        
        except Exception as e:
            st.error(f"인플루언서 매칭 중 오류: {e}")
            import traceback
            st.code(traceback.format_exc())


def display_matched_influencers_list():
    """매칭된 인플루언서 목록을 좌측에 드롭다운으로 표시"""
    matched = st.session_state.matched_influencers
    analysis_info = st.session_state.get('matching_analysis_result', {})
    
    st.markdown("##### 👥 매칭된 인플루언서")
    
    # 분석 정보 요약
    if analysis_info:
        campaign_type = analysis_info.get('campaign_type', 'N/A')
        category = analysis_info.get('recommended_category', 'N/A')
        min_followers = analysis_info.get('min_followers', 0)
        min_trust = analysis_info.get('min_trust_score_10', 0)
        st.info(
            f"**캠페인 타입:** {campaign_type} | **카테고리:** {category} | "
            f"**최소 팔로워:** {min_followers:,} | **최소 신뢰점수:** {min_trust:.1f}/10 | "
            f"**후보:** {analysis_info.get('filtered_candidates', 0)}명 | **매칭:** {analysis_info.get('matched_count', 0)}명"
        )
    
    if not matched:
        st.warning("매칭된 인플루언서가 없습니다.")
        return
    
    # 인플루언서 선택 드롭다운
    influencer_options = {}
    for idx, inf in enumerate(matched):
        name = inf.get('alias') or inf.get('name', 'N/A')
        platform = inf.get('platform', 'N/A')
        category = inf.get('category', 'N/A')
        # 최종 점수 우선 표시, 없으면 overall_score
        final_score = inf.get('final_score_10')
        if final_score is not None:
            score = f"{final_score:.2f}"
        else:
            score = f"{inf.get('overall_score', 0):.2f}" if inf.get('overall_score') else 'N/A'
        followers = f"{inf.get('followers', 0):,}" if inf.get('followers') else 'N/A'
        
        display_name = f"{name} ({platform}) - {category} [최종점수: {score}] [팔로워: {followers}]"
        influencer_options[display_name] = idx
    
    selected_display = st.selectbox(
        "인플루언서 선택",
        options=list(influencer_options.keys()),
        key="selected_influencer_dropdown",
        help="제안서를 작성할 인플루언서를 선택하세요"
    )
    
    if selected_display:
        selected_idx = influencer_options[selected_display]
        selected_influencer = matched[selected_idx]
        
        # SNS URL 조회
        sns_url = None
        platform = selected_influencer.get('platform')
        sns_id = selected_influencer.get('sns_id') or selected_influencer.get('alias')
        
        if platform and sns_id:
            try:
                simple_client_instance = db_manager.get_client()
                client = simple_client_instance.get_client()
                if client:
                    # platform과 sns_id로 connecta_influencers 테이블에서 조회
                    response = client.table("connecta_influencers")\
                        .select("sns_url")\
                        .eq("platform", platform)\
                        .eq("sns_id", sns_id)\
                        .single()\
                        .execute()
                    if response.data:
                        sns_url = response.data.get('sns_url')
            except Exception as e:
                # SNS URL 조회 실패는 치명적이지 않으므로 조용히 실패
                pass
        
        # 선택된 인플루언서 정보 표시
        st.markdown("---")
        st.markdown("#### 📋 선택된 인플루언서 정보")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**이름:** {selected_influencer.get('alias') or selected_influencer.get('name', 'N/A')}")
            st.write(f"**플랫폼:** {selected_influencer.get('platform', 'N/A')}")
            st.write(f"**카테고리:** {selected_influencer.get('category', 'N/A')}")
            if sns_url:
                st.markdown(f"**SNS URL:** [🔗 프로필 보기]({sns_url})")
            st.write(f"**팔로워:** {selected_influencer.get('followers', 0):,}" if selected_influencer.get('followers') else "**팔로워:** N/A")
        
        with col2:
            final_score = selected_influencer.get('final_score_10')
            if final_score is not None:
                st.write(f"**최종 매칭 점수:** {final_score:.2f}/10")
            st.write(f"**종합점수:** {selected_influencer.get('overall_score', 0):.2f}" if selected_influencer.get('overall_score') else "**종합점수:** N/A")
            st.write(f"**참여도:** {selected_influencer.get('engagement_score', 0):.2f}" if selected_influencer.get('engagement_score') else "**참여도:** N/A")
            st.write(f"**활동도:** {selected_influencer.get('activity_score', 0):.2f}" if selected_influencer.get('activity_score') else "**활동도:** N/A")
            if selected_influencer.get('tags'):
                st.write(f"**태그:** {', '.join(selected_influencer.get('tags', []))}")
        
        # 상세 점수 정보 표시
        if selected_influencer.get('final_score_10') is not None:
            st.markdown("---")
            st.markdown("#### 📊 상세 매칭 점수")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("신뢰도 점수", f"{selected_influencer.get('trust_score_10', 0):.2f}/10")
                st.metric("네트워크 신뢰도", f"{selected_influencer.get('network_trust_score_10', 0):.2f}/10")
                st.metric("댓글 진정성", f"{selected_influencer.get('comment_trust_score_10', 0):.2f}/10")
            
            with col2:
                st.metric("브랜드 적합도", f"{selected_influencer.get('brand_fit_score_10', 0):.2f}/10")
                st.metric("전환 적합도", f"{selected_influencer.get('conversion_fit_score_10', 0):.2f}/10")
                st.metric("브랜딩 적합도", f"{selected_influencer.get('branding_fit_score_10', 0):.2f}/10")
            
            with col3:
                st.metric("시딩 적합도", f"{selected_influencer.get('seeding_fit_score_10', 0):.2f}/10")
                st.metric("성장 잠재력", f"{selected_influencer.get('growth_potential_score', 0):.2f}/10" if selected_influencer.get('growth_potential_score') else "N/A")
        
        # 세션 상태에 선택된 인플루언서 저장
        st.session_state.selected_influencer_for_proposal = selected_influencer
        st.session_state.selected_influencer_idx = selected_idx


def display_matched_influencers_list_for_matching():
    """매칭된 인플루언서 목록을 드롭다운으로 표시하고 선택 시 상세 내용 하단에 표시"""
    matched = st.session_state.get('matched_influencers', [])
    analysis_info = st.session_state.get('matching_analysis_result', {})
    
    if not matched or len(matched) == 0:
        st.warning("매칭된 인플루언서가 없습니다.")
        # 매칭 다시 시작 버튼
        if st.button("🔄 다시 매칭하기", type="secondary", key="rematch_influencers", use_container_width=True):
            if 'matched_influencers' in st.session_state:
                del st.session_state.matched_influencers
            if 'matching_analysis_result' in st.session_state:
                del st.session_state.matching_analysis_result
            st.rerun()
        return
    
    # 분석 정보 요약
    if analysis_info:
        campaign_type = analysis_info.get('campaign_type', 'N/A')
        category = analysis_info.get('recommended_category', 'N/A')
        min_followers = analysis_info.get('min_followers', 0)
        min_trust = analysis_info.get('min_trust_score_10', 0)
        st.info(
            f"**캠페인 타입:** {campaign_type} | **카테고리:** {category} | "
            f"**최소 팔로워:** {min_followers:,} | **최소 신뢰점수:** {min_trust:.1f}/10 | "
            f"**후보:** {analysis_info.get('filtered_candidates', 0)}명 | **매칭:** {analysis_info.get('matched_count', 0)}명"
        )
    
    # 다시 매칭하기 버튼
    if st.button("🔄 다시 매칭하기", type="secondary", key="rematch_influencers_top", use_container_width=True):
        if 'matched_influencers' in st.session_state:
            del st.session_state.matched_influencers
        if 'matching_analysis_result' in st.session_state:
            del st.session_state.matching_analysis_result
        if 'selected_influencer_for_proposal' in st.session_state:
            del st.session_state.selected_influencer_for_proposal
        if 'generated_proposal' in st.session_state:
            del st.session_state.generated_proposal
        st.rerun()
    
    st.markdown("---")
    
    # 인플루언서 선택 드롭다운
    influencer_options = {}
    for idx, inf in enumerate(matched):
        name = inf.get('alias') or inf.get('name', 'N/A')
        platform = inf.get('platform', 'N/A')
        category = inf.get('category', 'N/A')
        # 최종 점수 우선 표시, 없으면 overall_score
        final_score = inf.get('final_score_10')
        if final_score is not None:
            score = f"{final_score:.2f}"
        else:
            score = f"{inf.get('overall_score', 0):.2f}" if inf.get('overall_score') else 'N/A'
        followers = f"{inf.get('followers', 0):,}" if inf.get('followers') else 'N/A'
        
        display_name = f"{name} ({platform}) - {category} [최종점수: {score}] [팔로워: {followers}]"
        influencer_options[display_name] = idx
    
    selected_display = st.selectbox(
        "인플루언서 선택",
        options=list(influencer_options.keys()),
        key="matching_selected_influencer_dropdown",
        help="상세 정보를 확인할 인플루언서를 선택하세요"
    )
    
    if selected_display:
        selected_idx = influencer_options[selected_display]
        selected_influencer = matched[selected_idx]
        
        # 세션 상태에 선택된 인플루언서 저장
        st.session_state.selected_influencer_for_proposal = selected_influencer
        st.session_state.selected_influencer_idx = selected_idx
        
        # 선택된 인플루언서 상세 정보 표시 (하단)
        st.markdown("---")
        st.markdown("#### 📋 선택된 인플루언서 상세 정보")
        
        # SNS URL 조회
        sns_url = None
        platform = selected_influencer.get('platform')
        sns_id = selected_influencer.get('sns_id') or selected_influencer.get('alias')
        
        if platform and sns_id:
            try:
                simple_client_instance = db_manager.get_client()
                client = simple_client_instance.get_client()
                if client:
                    # platform과 sns_id로 connecta_influencers 테이블에서 조회
                    response = client.table("connecta_influencers")\
                        .select("sns_url")\
                        .eq("platform", platform)\
                        .eq("sns_id", sns_id)\
                        .single()\
                        .execute()
                    if response.data:
                        sns_url = response.data.get('sns_url')
            except Exception as e:
                # SNS URL 조회 실패는 치명적이지 않으므로 조용히 실패
                pass
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**이름:** {selected_influencer.get('alias') or selected_influencer.get('name', 'N/A')}")
            st.write(f"**플랫폼:** {selected_influencer.get('platform', 'N/A')}")
            st.write(f"**카테고리:** {selected_influencer.get('category', 'N/A')}")
            if sns_url:
                st.markdown(f"**SNS URL:** [🔗 프로필 보기]({sns_url})")
            st.write(f"**팔로워:** {selected_influencer.get('followers', 0):,}" if selected_influencer.get('followers') else "**팔로워:** N/A")
            st.write(f"**팔로잉:** {selected_influencer.get('followings', 0):,}" if selected_influencer.get('followings') else "**팔로잉:** N/A")
            st.write(f"**게시물 수:** {selected_influencer.get('posts_count', 0):,}" if selected_influencer.get('posts_count') else "**게시물 수:** N/A")
        
        with col2:
            final_score = selected_influencer.get('final_score_10')
            if final_score is not None:
                st.write(f"**최종 매칭 점수:** {final_score:.2f}/10")
            st.write(f"**종합점수:** {selected_influencer.get('overall_score', 0):.2f}" if selected_influencer.get('overall_score') else "**종합점수:** N/A")
            st.write(f"**참여도:** {selected_influencer.get('engagement_score', 0):.2f}" if selected_influencer.get('engagement_score') else "**참여도:** N/A")
            st.write(f"**활동도:** {selected_influencer.get('activity_score', 0):.2f}" if selected_influencer.get('activity_score') else "**활동도:** N/A")
            st.write(f"**성장 잠재력:** {selected_influencer.get('growth_potential_score', 0):.2f}" if selected_influencer.get('growth_potential_score') else "**성장 잠재력:** N/A")
            if selected_influencer.get('tags'):
                st.write(f"**태그:** {', '.join(selected_influencer.get('tags', []))}")
        
        # 상세 점수 정보 표시
        if selected_influencer.get('final_score_10') is not None:
            st.markdown("---")
            st.markdown("#### 📊 상세 매칭 점수")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("신뢰도 점수", f"{selected_influencer.get('trust_score_10', 0):.2f}/10")
                st.metric("네트워크 신뢰도", f"{selected_influencer.get('network_trust_score_10', 0):.2f}/10")
                st.metric("댓글 진정성", f"{selected_influencer.get('comment_trust_score_10', 0):.2f}/10")
            
            with col2:
                st.metric("브랜드 적합도", f"{selected_influencer.get('brand_fit_score_10', 0):.2f}/10")
                st.metric("전환 적합도", f"{selected_influencer.get('conversion_fit_score_10', 0):.2f}/10")
                st.metric("브랜딩 적합도", f"{selected_influencer.get('branding_fit_score_10', 0):.2f}/10")
            
            with col3:
                st.metric("시딩 적합도", f"{selected_influencer.get('seeding_fit_score_10', 0):.2f}/10")
                st.metric("성장 잠재력", f"{selected_influencer.get('growth_potential_score', 0):.2f}/10" if selected_influencer.get('growth_potential_score') else "N/A")


def display_proposal_area(campaign: Dict[str, Any]):
    """제안서 작성 영역 (우측)"""
    st.markdown("##### 📝 캠페인 제안서 작성")
    
    # 선택된 인플루언서 확인
    if 'selected_influencer_for_proposal' not in st.session_state:
        st.info("👈 좌측에서 인플루언서를 선택해주세요.")
        return
    
    selected_influencer = st.session_state.selected_influencer_for_proposal
    
    # 선택된 인플루언서 요약 정보
    st.markdown(f"**선택된 인플루언서:** {selected_influencer.get('alias') or selected_influencer.get('name', 'N/A')} ({selected_influencer.get('platform', 'N/A')})")
    
    st.markdown("---")
    
    # 제안서 작성 버튼
    if st.button("📝 제안서 작성", type="primary", key="generate_single_proposal", use_container_width=True):
        generate_single_proposal(campaign, selected_influencer)
    
    # 작성된 제안서 표시
    if 'generated_proposal' in st.session_state:
        proposal_data = st.session_state.generated_proposal
        
        # 선택된 인플루언서와 제안서의 인플루언서가 일치하는지 확인
        proposal_influencer_id = proposal_data.get('influencer_id')
        current_influencer_id = selected_influencer.get('influencer_id')
        
        # influencer_id가 없으면 alias나 name으로 비교
        if not proposal_influencer_id or not current_influencer_id:
            proposal_influencer = proposal_data.get('influencer', {})
            proposal_name = proposal_influencer.get('alias') or proposal_influencer.get('name', '')
            current_name = selected_influencer.get('alias') or selected_influencer.get('name', '')
            is_match = proposal_name == current_name
        else:
            is_match = proposal_influencer_id == current_influencer_id
        
        if is_match:
            st.markdown("---")
            st.markdown("#### 📄 작성된 제안서")
            
            # 제안서 내용 표시 (스크롤 가능한 영역)
            st.markdown(proposal_data.get('proposal', ''))
            
            # 다운로드 버튼
            st.download_button(
                label="📥 제안서 다운로드",
                data=proposal_data.get('proposal', ''),
                file_name=f"proposal_{selected_influencer.get('alias', 'influencer')}_{campaign.get('campaign_name', 'campaign')}.md",
                mime="text/markdown",
                key="download_single_proposal",
                use_container_width=True
            )


def display_proposal_area_for_matching(campaign: Dict[str, Any]):
    """제안서 작성 영역 (매칭 탭용, 우측)"""
    # 선택된 인플루언서 확인
    if 'selected_influencer_for_proposal' not in st.session_state:
        st.info("👈 좌측에서 인플루언서를 선택해주세요.")
        return
    
    selected_influencer = st.session_state.selected_influencer_for_proposal
    
    # 선택된 인플루언서 요약 정보
    st.markdown(f"**선택된 인플루언서:** {selected_influencer.get('alias') or selected_influencer.get('name', 'N/A')} ({selected_influencer.get('platform', 'N/A')})")
    
    st.markdown("---")
    
    # 인공지능으로 제안서 작성 버튼
    if st.button("🤖 인공지능으로 제안서 작성", type="primary", key="generate_proposal_ai", use_container_width=True):
        generate_single_proposal(campaign, selected_influencer, use_openai=True)
    
    # 작성된 제안서 표시
    if 'generated_proposal' in st.session_state:
        proposal_data = st.session_state.generated_proposal
        
        # 선택된 인플루언서와 제안서의 인플루언서가 일치하는지 확인
        proposal_influencer_id = proposal_data.get('influencer_id')
        current_influencer_id = selected_influencer.get('influencer_id')
        
        # influencer_id가 없으면 alias나 name으로 비교
        if not proposal_influencer_id or not current_influencer_id:
            proposal_influencer = proposal_data.get('influencer', {})
            proposal_name = proposal_influencer.get('alias') or proposal_influencer.get('name', '')
            current_name = selected_influencer.get('alias') or selected_influencer.get('name', '')
            is_match = proposal_name == current_name
        else:
            is_match = proposal_influencer_id == current_influencer_id
        
        if is_match:
            st.markdown("---")
            st.markdown("#### 📄 작성된 제안서")
            
            # 제안서 내용 표시 (스크롤 가능한 영역)
            st.markdown(proposal_data.get('proposal', ''))
            
            # 다운로드 버튼
            st.download_button(
                label="📥 제안서 다운로드",
                data=proposal_data.get('proposal', ''),
                file_name=f"proposal_{selected_influencer.get('alias', 'influencer')}_{campaign.get('campaign_name', 'campaign')}.md",
                mime="text/markdown",
                key="download_proposal_matching",
                use_container_width=True
            )


def generate_single_proposal(campaign: Dict[str, Any], influencer: Dict[str, Any], use_openai: bool = False):
    """단일 인플루언서에 대한 제안서 생성"""
    with st.spinner("제안서를 작성 중입니다..."):
        proposal = None
        
        if use_openai:
            # OpenAI를 사용하여 제안서 생성 (매칭 탭용)
            # 캠페인 분석 결과 가져오기
            campaign_analysis_result = st.session_state.get('campaign_analysis_result')
            if not campaign_analysis_result:
                # DB에서 가져오기 시도
                campaign_id = campaign.get('id')
                if campaign_id:
                    existing_analysis = get_campaign_analysis_from_db(campaign_id)
                    if existing_analysis and existing_analysis.get('analysis_result'):
                        campaign_analysis_result = existing_analysis.get('analysis_result')
            
            if not campaign_analysis_result:
                st.error("❌ 캠페인 분석 결과가 없습니다. 먼저 '인공지능 캠페인 분석' 탭에서 캠페인을 분석해주세요.")
                return
            
            # OpenAI로 제안서 생성
            proposal = generate_proposal_with_openai(campaign_analysis_result, influencer)
        else:
            # Gemini API로 제안서 생성 (기존 방식)
            proposal = generate_proposal_with_gemini(campaign, influencer)
        
        if proposal:
            # 세션 상태에 저장
            st.session_state.generated_proposal = {
                "influencer_id": influencer.get('influencer_id'),
                "influencer": influencer,
                "proposal": proposal
            }
            st.success("✅ 제안서가 작성되었습니다!")
        else:
            st.error("❌ 제안서 작성에 실패했습니다.")


def generate_proposals(campaign: Dict[str, Any]):
    """제안서 생성"""
    if 'matched_influencers' not in st.session_state:
        st.error("매칭된 인플루언서가 없습니다.")
        return
    
    matched = st.session_state.matched_influencers
    
    if not matched:
        st.warning("매칭된 인플루언서가 없습니다.")
        return
    
    # 제안서 생성 진행 상태
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    proposals = []
    
    for idx, influencer in enumerate(matched):
        status_text.text(f"제안서 생성 중... ({idx + 1}/{len(matched)})")
        progress_bar.progress((idx + 1) / len(matched))
        
        # Gemini API로 제안서 생성
        proposal = generate_proposal_with_gemini(campaign, influencer)
        
        if proposal:
            proposals.append({
                "influencer": influencer,
                "proposal": proposal
            })
    
    progress_bar.empty()
    status_text.empty()
    
    # 제안서 저장 및 표시
    st.session_state.generated_proposals = proposals
    
    st.success(f"✅ {len(proposals)}개의 제안서가 생성되었습니다!")
    
    # 제안서 목록 표시
    display_proposals(proposals)


def display_proposals(proposals: List[Dict[str, Any]]):
    """제안서 목록 표시"""
    st.markdown("---")
    st.markdown("##### 📝 생성된 제안서")
    
    for idx, item in enumerate(proposals):
        influencer = item['influencer']
        proposal = item['proposal']
        
        with st.expander(
            f"📄 {idx + 1}. {influencer.get('alias') or influencer.get('name', 'N/A')} ({influencer.get('platform', 'N/A')})",
            expanded=(idx == 0)
        ):
            st.markdown(proposal)
            
            # 다운로드 버튼
            st.download_button(
                label="📥 제안서 다운로드",
                data=proposal,
                file_name=f"proposal_{influencer.get('alias', 'influencer')}_{idx + 1}.md",
                mime="text/markdown",
                key=f"download_proposal_{idx}"
            )

