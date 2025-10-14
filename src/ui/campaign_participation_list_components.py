"""
캠페인 참여 인플루언서 목록 및 편집 관련 UI 컴포넌트
"""
import streamlit as st
import pandas as pd
from src.db.database import db_manager
from .common_functions import format_campaign_type, format_sample_status

def render_participation_list():
    """참여 인플루언서 목록 및 편집 메인 컴포넌트"""
    st.markdown("### 📋 참여 인플루언서 목록 / 편집")
    st.markdown("캠페인에 참여하는 인플루언서 목록을 조회하고 편집합니다.")
    
    # 캠페인 선택
    campaigns = db_manager.get_campaigns()
    if not campaigns:
        st.info("먼저 캠페인을 생성해주세요.")
        return
    
    campaign_options = {f"{c['campaign_name']} ({format_campaign_type(c['campaign_type'])})": c for c in campaigns}
    selected_campaign_name = st.selectbox(
        "관리할 캠페인을 선택하세요",
        list(campaign_options.keys()),
        key="list_participation_campaign_select"
    )
    
    if selected_campaign_name:
        selected_campaign = campaign_options[selected_campaign_name]
        st.markdown(f"**선택된 캠페인:** {selected_campaign.get('campaign_name', 'N/A')} ({format_campaign_type(selected_campaign.get('campaign_type', ''))})")
        
        # 참여 인플루언서 목록
        participations = db_manager.get_all_campaign_participations(selected_campaign.get('id', ''))
        
        if not participations:
            st.info("이 캠페인에 참여한 인플루언서가 없습니다.")
        else:
            # 단일 레이아웃으로 변경
            st.markdown("#### 📋 참여 인플루언서 목록 (편집 가능)")
            render_participation_list_table(participations)

def render_participation_list_table(participations):
    """참여 인플루언서 목록 테이블 (편집 가능)"""
    # 참여 인플루언서 목록을 편집 가능한 테이블로 표시
    participation_data = []
    for participation in participations:
        participation_data.append({
            "ID": participation.get('id'),  # 숨겨진 ID 필드
            "인플루언서": participation.get('influencer_name', participation.get('sns_id', '')),
            "플랫폼": participation.get('platform', 'instagram'),
            "SNS ID": participation.get('sns_id', ''),
            "샘플 상태": participation.get('sample_status', '요청'),
            "업로드 완료": participation.get('content_uploaded', False),
            "비용": participation.get('cost_krw', 0) or 0,
            "매니저코멘트": participation.get('manager_comment', ''),
            "인플루언서요청사항": participation.get('influencer_requests', ''),
            "인플루언서피드백": participation.get('influencer_feedback', ''),
            "메모": participation.get('memo', ''),
            "참여일": participation.get('created_at', '')[:10] if participation.get('created_at') else "N/A"
        })
    
    if participation_data:
        df = pd.DataFrame(participation_data)
        
        # 컬럼 설정
        column_config = {
            "ID": st.column_config.NumberColumn("ID", disabled=True, help="참여 인플루언서 고유 ID"),
            "인플루언서": st.column_config.TextColumn(
                "인플루언서",
                help="인플루언서 이름 (읽기 전용)",
                disabled=True,
            ),
            "플랫폼": st.column_config.TextColumn(
                "플랫폼",
                help="SNS 플랫폼 (읽기 전용)",
                disabled=True,
            ),
            "SNS ID": st.column_config.TextColumn(
                "SNS ID", 
                help="SNS 계정 ID (읽기 전용)",
                disabled=True,
            ),
            "샘플 상태": st.column_config.SelectboxColumn(
                "샘플 상태",
                help="샘플 발송 상태",
                options=["요청", "발송준비", "발송완료", "수령"],
            ),
            "업로드 완료": st.column_config.CheckboxColumn(
                "업로드 완료",
                help="콘텐츠 업로드 완료 여부",
            ),
            "비용": st.column_config.NumberColumn(
                "비용 (원)",
                help="협찬 비용",
                min_value=0,
                format="%d원",
            ),
            "매니저코멘트": st.column_config.TextColumn(
                "매니저코멘트",
                help="매니저 코멘트",
                max_chars=500,
            ),
            "인플루언서요청사항": st.column_config.TextColumn(
                "인플루언서요청사항",
                help="인플루언서 요청사항",
                max_chars=500,
            ),
            "인플루언서피드백": st.column_config.TextColumn(
                "인플루언서피드백",
                help="인플루언서 피드백",
                max_chars=500,
            ),
            "메모": st.column_config.TextColumn(
                "메모",
                help="기타 메모",
                max_chars=500,
            ),
            "참여일": st.column_config.TextColumn(
                "참여일",
                disabled=True,
                help="참여 등록일 (읽기 전용)",
            ),
        }
        
        # 편집 가능한 테이블 표시
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            height=600,
            column_config=column_config,
            disabled=["ID", "인플루언서", "플랫폼", "SNS ID", "참여일"],  # 수정 불가능한 컬럼
            hide_index=True,
            key="participation_editor"
        )
        
        # 편집된 데이터가 있는지 확인하고 저장
        if not edited_df.equals(df):
            st.markdown("---")
            st.markdown("### 💾 변경사항 저장")
            st.info("📝 테이블에서 변경사항이 감지되었습니다. 저장 버튼을 클릭하여 데이터베이스를 업데이트하세요.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("💾 변경사항 저장", type="primary", key="save_participation_changes"):
                    save_edited_participations(df, edited_df)
            
            with col2:
                if st.button("🔄 변경사항 취소", key="cancel_participation_changes"):
                    st.rerun()
        else:
            # 항상 저장 버튼을 표시 (편의를 위해)
            st.markdown("---")
            st.markdown("### 💾 데이터 관리")
            st.info("💡 테이블에서 정보를 편집한 후 저장 버튼을 클릭하세요.")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("💾 현재 데이터 저장", type="primary", key="save_current_participation_data"):
                    save_edited_participations(df, edited_df)
            
            with col2:
                if st.button("🔄 새로고침", key="refresh_participation_data"):
                    st.rerun()
        
        # 총 개수 표시 및 편집 안내
        st.caption(f"총 {len(participations)}명의 참여 인플루언서가 표시됩니다.")
        st.info("💡 **편집 가능한 필드**: 샘플 상태, 업로드 완료, 비용, 매니저코멘트, 인플루언서요청사항, 인플루언서피드백, 메모  \n📖 **읽기 전용 필드**: 인플루언서, 플랫폼, SNS ID, 참여일")
    else:
        st.info("표시할 참여 인플루언서가 없습니다.")

def save_edited_participations(original_df, edited_df):
    """편집된 참여 인플루언서 데이터를 저장"""
    try:
        # 변경된 행들을 찾아서 업데이트
        updated_count = 0
        error_count = 0
        total_changes = 0
        
        # DataFrame을 인덱스 기반으로 비교
        for idx in range(len(original_df)):
            original_row = original_df.iloc[idx]
            edited_row = edited_df.iloc[idx]
            
            # 변경사항이 있는지 확인 (읽기 전용 컬럼 제외)
            readonly_columns = ["ID", "인플루언서", "플랫폼", "SNS ID", "참여일"]
            comparison_columns = [col for col in original_df.columns if col not in readonly_columns]
            has_changes = False
            
            for col in comparison_columns:
                if str(original_row[col]) != str(edited_row[col]):
                    has_changes = True
                    total_changes += 1
                    break
            
            if has_changes:
                participation_id = edited_row["ID"]
                
                # 업데이트할 데이터 준비 (NumPy 타입을 Python 기본 타입으로 변환)
                # 참고: influencer_name, platform, sns_id는 connecta_influencers 테이블에 있으므로 업데이트 불가
                update_data = {
                    'sample_status': str(edited_row["샘플 상태"]),
                    'content_uploaded': bool(edited_row["업로드 완료"]),
                    'cost_krw': int(edited_row["비용"]) if edited_row["비용"] is not None else 0,
                    'manager_comment': str(edited_row["매니저코멘트"]) if edited_row["매니저코멘트"] else None,
                    'influencer_requests': str(edited_row["인플루언서요청사항"]) if edited_row["인플루언서요청사항"] else None,
                    'influencer_feedback': str(edited_row["인플루언서피드백"]) if edited_row["인플루언서피드백"] else None,
                    'memo': str(edited_row["메모"]) if edited_row["메모"] else None
                }
                
                # 데이터베이스 업데이트
                result = db_manager.update_campaign_participation(participation_id, update_data)
                if result["success"]:
                    updated_count += 1
                else:
                    error_count += 1
                    st.error(f"❌ ID {participation_id} 업데이트 실패: {result['message']}")
        
        # 결과 표시
        if total_changes == 0:
            st.info("💡 변경된 내용이 없습니다. 테이블에서 정보를 편집한 후 다시 저장해주세요.")
        elif updated_count > 0:
            st.success(f"✅ {updated_count}명의 참여 인플루언서 정보가 업데이트되었습니다!")
        
        if error_count > 0:
            st.error(f"❌ {error_count}명의 참여 인플루언서 업데이트에 실패했습니다.")
        
        if updated_count > 0:
            # 캐시 초기화
            if "participations_cache" in st.session_state:
                del st.session_state["participations_cache"]
            
            # 페이지 새로고침
            st.rerun()
            
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")
        import traceback
        st.code(traceback.format_exc())
