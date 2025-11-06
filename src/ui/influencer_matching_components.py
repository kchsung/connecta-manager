"""
인플루언서 매칭 관련 컴포넌트들
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from ..db.database import db_manager
from ..utils.gemini_client import analyze_campaign_with_gemini, generate_proposal_with_gemini
from ..supabase.simple_client import simple_client


def render_influencer_matching():
    """인플루언서 매칭 메인 컴포넌트"""
    st.subheader("🎯 인플루언서 매칭")
    st.markdown("캠페인에 적합한 인플루언서를 자동으로 매칭하고 제안서를 생성합니다.")
    
    # 탭으로 분리
    tab_names = ["📋 캠페인 선택", "🤖 인플루언서 매칭"]
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        render_campaign_selection()
    
    with tabs[1]:
        render_influencer_matching_process()


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


def render_influencer_matching_process():
    """인플루언서 매칭 프로세스 탭"""
    st.markdown("### 🤖 인플루언서 매칭")
    
    # 선택된 캠페인 확인
    if 'selected_campaign' not in st.session_state:
        st.warning("⚠️ 먼저 '캠페인 선택' 탭에서 캠페인을 선택하고 필요한 인플루언서 수를 입력해주세요.")
        return
    
    selected_campaign = st.session_state.selected_campaign
    required_influencers = st.session_state.get("matching_required_influencers", 10)
    
    st.info(f"**선택된 캠페인:** {selected_campaign.get('campaign_name')} | **필요 인플루언서 수:** {required_influencers}명")
    
    # 매칭 프로세스 단계별 진행
    st.markdown("---")
    st.markdown("#### 1️⃣ 캠페인 내용 분석")
    
    if st.button("🔍 캠페인 분석 시작", type="primary", key="start_campaign_analysis"):
        analyze_campaign(selected_campaign)
    
    # 분석 결과가 있으면 표시
    if 'campaign_analysis_result' in st.session_state:
        display_campaign_analysis_result()
        
        # 인플루언서 매칭 진행
        st.markdown("---")
        st.markdown("#### 2️⃣ 인플루언서 매칭")
        
        if st.button("🎯 인플루언서 매칭 시작", type="primary", key="start_influencer_matching"):
            match_influencers(required_influencers)
    
    # 매칭 결과가 있으면 표시
    if 'matched_influencers' in st.session_state:
        # 좌우 분할 레이아웃
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            display_matched_influencers_list()
        
        with col_right:
            display_proposal_area(selected_campaign)


def analyze_campaign(campaign: Dict[str, Any]):
    """캠페인 내용 분석"""
    # Gemini API 키 확인
    import os
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        try:
            gemini_key = st.secrets.get("GEMINI_API_KEY")
        except (KeyError, AttributeError, TypeError):
            gemini_key = None
    
    if not gemini_key:
        st.error("❌ Gemini API 키를 찾을 수 없습니다.")
        st.info("💡 `.streamlit/secrets.toml` 파일에 `GEMINI_API_KEY = \"your-api-key\"` 형식으로 추가하고 앱을 재시작해주세요.")
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
        
        # Gemini API로 분석
        analysis_result = analyze_campaign_with_gemini(campaign_content)
        
        if analysis_result:
            st.session_state.campaign_analysis_result = analysis_result
            st.success("✅ 캠페인 분석이 완료되었습니다!")
        else:
            st.error("❌ 캠페인 분석에 실패했습니다.")


def display_campaign_analysis_result():
    """캠페인 분석 결과 표시"""
    result = st.session_state.campaign_analysis_result
    
    st.markdown("##### 📊 분석 결과")
    
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
    """인플루언서 매칭"""
    with st.spinner("인플루언서를 매칭 중입니다..."):
        analysis_result = st.session_state.campaign_analysis_result
        
        # 1. 분석 결과 추출
        category = analysis_result.get('category', '').strip()
        recommended_tags = analysis_result.get('recommended_tags', [])
        
        # AI 분석 데이터 조회
        try:
            client = simple_client.get_client()
            if not client:
                st.error("데이터베이스 연결 실패")
                return
            
            # 전체 인플루언서 조회 (점수 순)
            query = client.table("ai_influencer_analyses").select("*")
            response = query.order("overall_score", desc=True).limit(10000).execute()
            all_candidates = response.data if response.data else []
            
            # 2. 필터링 단계별 적용
            filtered_candidates = all_candidates.copy()
            
            # 2-1. 카테고리 필터링 (표준 카테고리 기준)
            # 표준 카테고리 목록
            standard_categories = [
                "일반", "뷰티", "패션", "푸드", "여행", 
                "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"
            ]
            
            if category:
                # "/"로 구분된 카테고리를 OR 조건으로 처리
                category_keywords = [kw.strip() for kw in category.split('/') if kw.strip()]
                category_keywords_lower = [kw.lower() for kw in category_keywords]
                
                # 정확히 일치하는 경우 먼저 확인
                exact_match = [c for c in filtered_candidates if c.get('category', '').strip() == category]
                
                if exact_match:
                    filtered_candidates = exact_match
                else:
                    # OR 조건으로 필터링: 키워드 중 하나라도 일치하면 선택
                    category_matched = []
                    
                    for candidate in filtered_candidates:
                        candidate_category = candidate.get('category', '').strip()
                        candidate_category_lower = candidate_category.lower()
                        
                        # 키워드 중 하나라도 일치하는지 확인 (OR 조건)
                        matched = False
                        
                        # 1. 정확 일치 확인 (표준 카테고리와 비교)
                        if candidate_category in category_keywords:
                            matched = True
                        
                        # 2. 표준 카테고리와 매칭 확인
                        if not matched:
                            for keyword in category_keywords_lower:
                                # 표준 카테고리 목록에서 매칭 확인
                                for std_cat in standard_categories:
                                    std_cat_lower = std_cat.lower()
                                    # 키워드가 표준 카테고리와 일치하고, 후보 카테고리도 같은 표준 카테고리인 경우
                                    if (keyword == std_cat_lower and candidate_category_lower == std_cat_lower):
                                        matched = True
                                        break
                                    # 부분 일치 (키워드가 표준 카테고리에 포함되고, 후보도 같은 카테고리)
                                    elif (keyword in std_cat_lower and candidate_category_lower == std_cat_lower):
                                        matched = True
                                        break
                                
                                if matched:
                                    break
                        
                        # 3. 부분 일치 확인 (키워드가 카테고리에 포함되거나, 카테고리가 키워드에 포함)
                        if not matched:
                            for keyword in category_keywords_lower:
                                if (keyword in candidate_category_lower or 
                                    candidate_category_lower in keyword):
                                    matched = True
                                    break
                        
                        if matched:
                            category_matched.append(candidate)
                    
                    if category_matched:
                        filtered_candidates = category_matched
                    else:
                        # 카테고리 매칭 실패 시 전체에서 태그로만 필터링
                        pass
            
            # 2-2. 태그 필터링 (Python에서 처리 - 여러 태그 중 하나라도 포함되면 매칭)
            if recommended_tags:
                tag_filtered = []
                for candidate in filtered_candidates:
                    candidate_tags = candidate.get('tags', [])
                    if not candidate_tags:
                        continue
                    
                    # 추천 태그 중 하나라도 후보의 태그에 포함되면 선택
                    # 대소문자 무시, 부분 일치도 허용
                    candidate_tags_lower = [str(tag).lower() for tag in candidate_tags]
                    recommended_tags_lower = [str(tag).lower() for tag in recommended_tags]
                    
                    if any(rec_tag in cand_tag or cand_tag in rec_tag 
                           for rec_tag in recommended_tags_lower 
                           for cand_tag in candidate_tags_lower):
                        tag_filtered.append(candidate)
                
                if tag_filtered:
                    filtered_candidates = tag_filtered
                else:
                    # 태그 매칭 실패 시 필터링 없이 점수 순으로 추출
                    pass
            
            # 3. 총 필요 인플루언서 * 2 배수 추출
            target_count = required_count * 2
            matched = filtered_candidates[:target_count] if len(filtered_candidates) >= target_count else filtered_candidates
            
            # 4. 세션 상태에 저장
            st.session_state.matched_influencers = matched
            st.session_state.matching_analysis_result = {
                "category": category,
                "recommended_tags": recommended_tags,
                "total_candidates": len(all_candidates),
                "filtered_candidates": len(filtered_candidates),
                "matched_count": len(matched)
            }
            
            if len(matched) > 0:
                st.success(f"✅ {len(matched)}명의 인플루언서를 매칭했습니다!")
            else:
                st.warning(f"⚠️ 매칭된 인플루언서가 없습니다. 필터 조건을 완화하거나 데이터를 확인해주세요.")
        
        except Exception as e:
            st.error(f"인플루언서 매칭 중 오류: {e}")


def display_matched_influencers_list():
    """매칭된 인플루언서 목록을 좌측에 드롭다운으로 표시"""
    matched = st.session_state.matched_influencers
    analysis_info = st.session_state.get('matching_analysis_result', {})
    
    st.markdown("##### 👥 매칭된 인플루언서")
    
    # 분석 정보 요약
    if analysis_info:
        st.info(f"**필터:** {analysis_info.get('category', 'N/A')} | **후보:** {analysis_info.get('filtered_candidates', 0)}명 | **매칭:** {analysis_info.get('matched_count', 0)}명")
    
    if not matched:
        st.warning("매칭된 인플루언서가 없습니다.")
        return
    
    # 인플루언서 선택 드롭다운
    influencer_options = {}
    for idx, inf in enumerate(matched):
        name = inf.get('alias') or inf.get('name', 'N/A')
        platform = inf.get('platform', 'N/A')
        category = inf.get('category', 'N/A')
        score = f"{inf.get('overall_score', 0):.2f}" if inf.get('overall_score') else 'N/A'
        followers = f"{inf.get('followers', 0):,}" if inf.get('followers') else 'N/A'
        
        display_name = f"{name} ({platform}) - {category} [점수: {score}] [팔로워: {followers}]"
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
        
        # 선택된 인플루언서 정보 표시
        st.markdown("---")
        st.markdown("#### 📋 선택된 인플루언서 정보")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**이름:** {selected_influencer.get('alias') or selected_influencer.get('name', 'N/A')}")
            st.write(f"**플랫폼:** {selected_influencer.get('platform', 'N/A')}")
            st.write(f"**카테고리:** {selected_influencer.get('category', 'N/A')}")
            st.write(f"**팔로워:** {selected_influencer.get('followers', 0):,}" if selected_influencer.get('followers') else "**팔로워:** N/A")
        
        with col2:
            st.write(f"**종합점수:** {selected_influencer.get('overall_score', 0):.2f}" if selected_influencer.get('overall_score') else "**종합점수:** N/A")
            st.write(f"**참여도:** {selected_influencer.get('engagement_score', 0):.2f}" if selected_influencer.get('engagement_score') else "**참여도:** N/A")
            st.write(f"**활동도:** {selected_influencer.get('activity_score', 0):.2f}" if selected_influencer.get('activity_score') else "**활동도:** N/A")
            if selected_influencer.get('tags'):
                st.write(f"**태그:** {', '.join(selected_influencer.get('tags', []))}")
        
        # 세션 상태에 선택된 인플루언서 저장
        st.session_state.selected_influencer_for_proposal = selected_influencer
        st.session_state.selected_influencer_idx = selected_idx


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


def generate_single_proposal(campaign: Dict[str, Any], influencer: Dict[str, Any]):
    """단일 인플루언서에 대한 제안서 생성"""
    with st.spinner("제안서를 작성 중입니다..."):
        # Gemini API로 제안서 생성
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

