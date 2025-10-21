"""
인플루언서 상세 정보 관련 컴포넌트들
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..db.database import db_manager
from .common_functions import safe_int_conversion

def render_influencer_detail_form(influencer):
    """인플루언서 상세 정보 폼 (기존 함수 - 호환성 유지)"""
    st.markdown(f"**{influencer.get('influencer_name') or influencer['sns_id']}**")
    
    # 프로필 이미지 제거됨 - 깔끔한 레이아웃
    
    # 기본 정보 표시 (간소화)
    col1, col2 = st.columns(2)
    with col1:
        # 플랫폼 아이콘화
        platform_icons = {
            "instagram": "📸 Instagram",
            "youtube": "📺 YouTube", 
            "tiktok": "🎵 TikTok",
            "twitter": "🐦 Twitter"
        }
        platform_display = platform_icons.get(influencer['platform'], f"🌐 {influencer['platform']}")
        st.metric("플랫폼", platform_display)
    with col2:
        st.metric("SNS ID", influencer['sns_id'])
    
    # 필수 정보 표시
    st.markdown("### 📋 필수 정보")
    
    # SNS URL (필수) - 링크로 표시
    sns_url = influencer.get('sns_url', 'N/A')
    if sns_url and sns_url != 'N/A':
        st.markdown(f"**🔗 SNS URL:** [{sns_url}]({sns_url})")
    else:
        st.markdown(f"**🔗 SNS URL:** {sns_url}")
    
    # Owner Comment (필수) - 안전한 텍스트 표시
    owner_comment = influencer.get('owner_comment', 'N/A')
    st.markdown("**💬 Owner Comment:**")
    try:
        # 특수 문자를 안전하게 처리
        safe_owner_comment = str(owner_comment) if owner_comment else 'N/A'
        st.text_area("", value=safe_owner_comment, height=80, disabled=True, key=f"owner_comment_{influencer['id']}")
    except Exception as e:
        st.text_area("", value="[텍스트 표시 오류]", height=80, disabled=True, key=f"owner_comment_{influencer['id']}")
        st.caption(f"텍스트 표시 오류: {str(e)}")
    
    
    # 추가 정보 섹션
    st.markdown("### 📞 연락처 정보")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Phone Number
        phone_number = influencer.get('phone_number')
        if phone_number:
            st.markdown(f"**📱 Phone Number:** {phone_number}")
        else:
            st.markdown("**📱 Phone Number:** 정보 없음")
        
        # Email
        email = influencer.get('email')
        if email:
            st.markdown(f"**📧 Email:** {email}")
        else:
            st.markdown("**📧 Email:** 정보 없음")
    
    with col4:
        # Kakao Channel ID
        kakao_channel_id = influencer.get('kakao_channel_id')
        if kakao_channel_id:
            st.markdown(f"**💬 Kakao Channel ID:** {kakao_channel_id}")
        else:
            st.markdown("**💬 Kakao Channel ID:** 정보 없음")
        
        # Contact Method
        contact_method = influencer.get('contact_method', 'dm')
        contact_method_etc = influencer.get('contact_method_etc', '')
        contact_method_display = {
            "dm": "💬 DM",
            "email": "📧 이메일",
            "kakao": "💛 카카오톡",
            "phone": "📞 전화",
            "form": "📝 폼",
            "other": "🔧 기타"
        }.get(contact_method, f"🔧 {contact_method}")
        
        if contact_method == 'other' and contact_method_etc:
            st.markdown(f"**📱 연락 방식:** {contact_method_display} ({contact_method_etc})")
        else:
            st.markdown(f"**📱 연락 방식:** {contact_method_display}")
    
    # 배송 정보
    st.markdown("### 📦 배송 정보")
    shipping_address = influencer.get('shipping_address')
    if shipping_address:
        st.markdown(f"**📦 Shipping Address:**")
        st.text_area("", value=shipping_address, height=60, disabled=True, key=f"shipping_address_display_{influencer['id']}")
    else:
        st.markdown("**📦 Shipping Address:** 정보 없음")
    
    # 태그 정보
    tags = influencer.get('tags')
    if tags:
        st.markdown("### 🏷️ Tags")
        st.markdown(f"**{tags}**")
    else:
        st.markdown("### 🏷️ Tags")
        st.markdown("**정보 없음**")
    
    
    # 관심 제품 정보
    interested_products = influencer.get('interested_products')
    if interested_products:
        st.markdown("### 🛍️ Interested Products")
        st.text_area("", value=interested_products, height=80, disabled=True, key=f"interested_products_display_{influencer['id']}")
    
    # 선호 홍보/세일즈 방식
    preferred_mode = influencer.get('preferred_mode')
    if preferred_mode:
        preferred_mode_display = {
            "seeding": "🌱 시딩",
            "promotion": "📢 홍보",
            "sales": "💰 세일즈"
        }.get(preferred_mode, f"🔧 {preferred_mode}")
        st.markdown(f"**🎯 선호 홍보/세일즈 방식:** {preferred_mode_display}")
    
    # 등록일 정보
    if influencer.get('created_at'):
        st.caption(f"등록일: {influencer['created_at'][:10]}")
    
    # 수정 폼
    with st.expander("✏️ 정보 수정", expanded=True):
        with st.form(f"edit_influencer_form_{influencer['id']}"):
            st.markdown("**수정 가능 정보:**")
            
            # 세션 상태에 초기값 설정 (폼이 처음 렌더링될 때만)
            form_key = f"edit_influencer_form_{influencer['id']}"
            if f"{form_key}_initialized" not in st.session_state:
                st.session_state[f"edit_owner_comment_{influencer['id']}"] = influencer.get('owner_comment') or ''
                # 컨텐츠 카테고리 초기값 설정 (매칭되는 것이 있으면 해당 값, 없으면 "기타")
                current_category = influencer.get('content_category', '')
                category_options = ["일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"]
                if current_category in category_options:
                    default_category = current_category
                else:
                    default_category = "기타"
                st.session_state[f"edit_content_category_{influencer['id']}"] = default_category
                st.session_state[f"edit_tags_{influencer['id']}"] = influencer.get('tags') or ''
                st.session_state[f"edit_contact_method_{influencer['id']}"] = influencer.get('contact_method') or 'dm'
                st.session_state[f"edit_preferred_mode_{influencer['id']}"] = influencer.get('preferred_mode') or 'seeding'
                st.session_state[f"edit_price_krw_{influencer['id']}"] = float(influencer.get('price_krw') or 0)
                st.session_state[f"edit_manager_rating_{influencer['id']}"] = str(influencer.get('manager_rating') or '3')
                st.session_state[f"edit_content_rating_{influencer['id']}"] = str(influencer.get('content_rating') or '3')
                st.session_state[f"edit_interested_products_{influencer['id']}"] = influencer.get('interested_products') or ''
                st.session_state[f"edit_shipping_address_{influencer['id']}"] = influencer.get('shipping_address') or ''
                st.session_state[f"edit_phone_number_{influencer['id']}"] = influencer.get('phone_number') or ''
                st.session_state[f"edit_email_{influencer['id']}"] = influencer.get('email') or ''
                st.session_state[f"edit_kakao_channel_id_{influencer['id']}"] = influencer.get('kakao_channel_id') or ''
                st.session_state[f"edit_followers_count_{influencer['id']}"] = influencer.get('followers_count') or 0
                st.session_state[f"edit_influencer_name_{influencer['id']}"] = influencer.get('influencer_name') or ''
                st.session_state[f"{form_key}_initialized"] = True
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Owner Comment
                new_owner_comment = st.text_area(
                    "💬 Owner Comment", 
                    key=f"edit_owner_comment_{influencer['id']}",
                    help="인플루언서에 대한 담당자 코멘트"
                )
                
                # Content Category
                category_options = ["일반", "뷰티", "패션", "푸드", "여행", "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"]
                
                # 현재 DB 값 확인
                current_category = influencer.get('content_category', '')
                
                # 매칭되는 카테고리가 있으면 해당 카테고리, 없으면 "기타"로 설정
                if current_category in category_options:
                    default_category = current_category
                else:
                    default_category = "기타"
                
                new_content_category = st.selectbox(
                    "📂 Content Category",
                    category_options,
                    key=f"edit_content_category_{influencer['id']}"
                )
                
                # Tags
                tags_input = st.text_input(
                    "🏷️ Tags", 
                    key=f"edit_tags_{influencer['id']}",
                    help="태그를 쉼표로 구분하여 입력하세요"
                )
                
                # Contact Method (enum: dm, email, kakao, phone, form, other)
                contact_method_options = ["dm", "email", "kakao", "phone", "form", "other"]
                new_contact_method = st.selectbox(
                    "📱 연락 방식",
                    contact_method_options,
                    key=f"edit_contact_method_{influencer['id']}",
                    format_func=lambda x: {
                        "dm": "💬 DM",
                        "email": "📧 이메일",
                        "kakao": "💛 카카오톡",
                        "phone": "📞 전화",
                        "form": "📝 폼",
                        "other": "🔧 기타"
                    }[x]
                )
            
            with col2:
                # 연락방법 추가정보 필드 (언제나 표시)
                contacts_method_etc = st.text_input(
                    "📝 연락방법 추가정보",
                    value=influencer.get('contacts_method_etc', ''),
                    key=f"edit_contacts_method_etc_{influencer['id']}",
                    help="연락방법에 대한 추가 상세 정보를 입력해주세요"
                )
                
                # Preferred Mode (enum: seeding, promotion, sales)
                preferred_mode_options = ["seeding", "promotion", "sales"]
                new_preferred_mode = st.selectbox(
                    "🎯 선호 홍보/세일즈 방식",
                    preferred_mode_options,
                    key=f"edit_preferred_mode_{influencer['id']}",
                    format_func=lambda x: {
                        "seeding": "🌱 시딩",
                        "promotion": "📢 홍보",
                        "sales": "💰 세일즈"
                    }[x]
                )
                
                # Price KRW
                new_price_krw = st.number_input(
                    "💰 Price (KRW)", 
                    min_value=0, 
                    value=safe_int_conversion(influencer.get('price_krw', 0)),
                    step=1,
                    format="%d",
                    key=f"edit_price_krw_{influencer['id']}",
                    help="인플루언서 협찬 비용"
                )
                
                # Manager Rating
                rating_options = ["1", "2", "3", "4", "5"]
                new_manager_rating = st.selectbox(
                    "⭐ Manager Rating",
                    rating_options,
                    key=f"edit_manager_rating_{influencer['id']}",
                    help="담당자 평가 (1-5점)"
                )
                
                # Interested Products
                new_interested_products = st.text_area(
                    "🛍️ Interested Products", 
                    key=f"edit_interested_products_{influencer['id']}",
                    help="관심 있는 제품 카테고리",
                    height=80
                )
                
                # Shipping Address
                new_shipping_address = st.text_area(
                    "📦 Shipping Address", 
                    key=f"edit_shipping_address_{influencer['id']}",
                    help="배송 주소",
                    height=80
                )
                
                # Content Rating
                content_rating_options = ["1", "2", "3", "4", "5"]
                new_content_rating = st.selectbox(
                    "⭐ Content Rating",
                    content_rating_options,
                    key=f"edit_content_rating_{influencer['id']}",
                    help="콘텐츠 품질 평가 (1-5점)"
                )
            
            # 추가 연락처 정보 (새로운 행)
            st.markdown("**📞 연락처 정보**")
            col3, col4 = st.columns(2)
            
            with col3:
                # Phone Number
                new_phone_number = st.text_input(
                    "📱 Phone Number", 
                    key=f"edit_phone_number_{influencer['id']}",
                    help="인플루언서 전화번호",
                    placeholder="010-1234-5678"
                )
                
                # Email
                new_email = st.text_input(
                    "📧 Email", 
                    key=f"edit_email_{influencer['id']}",
                    help="인플루언서 이메일 주소",
                    placeholder="influencer@example.com"
                )
            
            with col4:
                # Kakao Channel ID
                new_kakao_channel_id = st.text_input(
                    "💬 Kakao Channel ID", 
                    key=f"edit_kakao_channel_id_{influencer['id']}",
                    help="카카오 채널 ID",
                    placeholder="@channel_id"
                )
            
            # 기본 정보 (새로운 행)
            st.markdown("**👤 기본 정보**")
            col5, col6 = st.columns(2)
            
            with col5:
                # 팔로워수
                new_followers_count = st.number_input(
                    "👥 팔로워수", 
                    min_value=0,
                    value=safe_int_conversion(influencer.get('followers_count', 0)),
                    step=1,
                    key=f"edit_followers_count_{influencer['id']}",
                    help="인플루언서 팔로워 수"
                )
            
            with col6:
                # 이름
                new_influencer_name = st.text_input(
                    "👤 이름", 
                    key=f"edit_influencer_name_{influencer['id']}",
                    help="인플루언서 이름",
                    placeholder="인플루언서 이름"
                )
            
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 수정하기", type="primary"):
                    # 폼 제출 시점에서 세션 상태에서 실제 값 가져오기
                    actual_tags_input = st.session_state.get(f"edit_tags_{influencer['id']}", "")
                    
                    # 실제 세션 상태 값으로 태그 처리
                    if actual_tags_input and actual_tags_input.strip():
                        # 문자열 그대로 저장
                        actual_tags = actual_tags_input.strip()
                    else:
                        actual_tags = ""
                    
                    # 수정 데이터 준비
                    update_data = {
                        "owner_comment": new_owner_comment,
                        "content_category": new_content_category,
                        "tags": actual_tags,
                        "contact_method": new_contact_method,
                        "contacts_method_etc": contacts_method_etc,
                        "preferred_mode": new_preferred_mode,
                        "price_krw": float(new_price_krw) if new_price_krw and new_price_krw > 0 else None,
                        "manager_rating": int(new_manager_rating) if new_manager_rating and new_manager_rating.isdigit() else None,
                        "content_rating": int(new_content_rating) if new_content_rating and new_content_rating.isdigit() else None,
                        "interested_products": new_interested_products,
                        "shipping_address": new_shipping_address,
                        "phone_number": new_phone_number,
                        "email": new_email,
                        "kakao_channel_id": new_kakao_channel_id,
                        "followers_count": int(new_followers_count) if new_followers_count and new_followers_count > 0 else None,
                        "influencer_name": new_influencer_name
                    }
                    
                    # 데이터베이스 업데이트
                    result = db_manager.update_influencer(influencer['id'], update_data)
                    
                    if result["success"]:
                        st.success("인플루언서 정보가 수정되었습니다!")
                        # 캐시 초기화
                        for key in list(st.session_state.keys()):
                            if key.startswith("filtered_influencers_"):
                                del st.session_state[key]
                        # 폼 초기화 플래그 제거 (다음에 다시 로드되도록)
                        if f"{form_key}_initialized" in st.session_state:
                            del st.session_state[f"{form_key}_initialized"]
                        # 선택된 인플루언서 정보도 업데이트 (DB에서 최신 정보 가져오기)
                        if 'selected_influencer' in st.session_state:
                            # DB에서 최신 정보 가져오기
                            updated_influencer = db_manager.get_influencer_info(
                                st.session_state.selected_influencer['platform'], 
                                st.session_state.selected_influencer['sns_id']
                            )
                            if updated_influencer["success"] and updated_influencer["exists"]:
                                st.session_state.selected_influencer = updated_influencer["data"]
                            else:
                                # 폴백: 기존 정보에 업데이트 데이터 병합
                                st.session_state.selected_influencer.update(update_data)
                        st.session_state.detail_update_completed = True  # 상세 업데이트 완료 플래그
                        # 리렌더링 없이 상태 기반 UI 업데이트
                    else:
                        st.error(f"수정 실패: {result['message']}")
            with col2:
                if st.form_submit_button("❌ 취소"):
                    st.session_state.detail_edit_cancelled = True  # 상세 편집 취소 플래그
                    # 리렌더링 없이 상태 기반 UI 업데이트
    
    # 선택 해제 버튼
    if st.button("🔄 선택 해제", key=f"clear_selection_{influencer['id']}"):
        # 선택된 인플루언서 제거
        if 'selected_influencer' in st.session_state:
            del st.session_state.selected_influencer
        
        # 폼 초기화 플래그 제거 (다음에 다시 로드되도록)
        form_key = f"edit_influencer_form_{influencer['id']}"
        if f"{form_key}_initialized" in st.session_state:
            del st.session_state[f"{form_key}_initialized"]
        
        # 모든 편집 관련 세션 상태 정리
        for key in list(st.session_state.keys()):
            if key.startswith(f"edit_") and key.endswith(f"_{influencer['id']}"):
                del st.session_state[key]
        
        st.session_state.selection_cleared = True  # 선택 해제 완료 플래그
        # 리렌더링 없이 상태 기반 UI 업데이트


