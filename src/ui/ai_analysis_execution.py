"""
AI 분석 실행 관련 컴포넌트
"""
import streamlit as st
import time
from ..supabase.simple_client import simple_client
from .ai_analysis_common import (
    get_completed_crawling_data, 
    get_completed_crawling_data_count,
    is_recently_analyzed_by_id,
    save_ai_analysis_result,
    perform_ai_analysis,
    transform_to_db_format
)

def render_ai_analysis_execution():
    """AI 분석 실행 탭"""
    st.subheader("🚀 인공지능 분석 실행")
    st.markdown("크롤링이 완료된 인플루언서 데이터를 AI로 분석합니다.")
    
    # OpenAI API 키 확인
    import os
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        try:
            openai_api_key = st.secrets["OPENAI_API_KEY"]
        except (KeyError, AttributeError):
            openai_api_key = None
    
    if not openai_api_key or openai_api_key == "your-openai-api-key-here":
        st.error("API 키가 설정되지 않았습니다.")
        return
        
    # 분석 상태 초기화
    if "ai_analysis_running" not in st.session_state:
        st.session_state.ai_analysis_running = False
    if "ai_analysis_stop_requested" not in st.session_state:
        st.session_state.ai_analysis_stop_requested = False
    
    # 분석 중지 버튼 (분석 중일 때만 표시)
    if st.session_state.ai_analysis_running:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("⏹️ 분석 중지", type="secondary", help="현재 진행 중인 AI 분석을 중지합니다"):
                st.session_state.ai_analysis_stop_requested = True
                st.warning("🛑 분석 중지 요청됨. 현재 처리 중인 항목 완료 후 중지됩니다.")
                st.rerun()
    
    # 분석 실행 버튼 (분석 중이 아닐 때만 표시)
    if not st.session_state.ai_analysis_running:
        if st.button("🚀 AI 분석 시작", type="primary"):
            st.session_state.ai_analysis_running = True
            st.session_state.ai_analysis_stop_requested = False
            st.rerun()
    
    # 분석 실행 중일 때
    if st.session_state.ai_analysis_running:
        with st.spinner("AI 분석을 시작합니다..."):
            result = execute_ai_analysis()
            
            # 분석 완료 후 상태 초기화
            st.session_state.ai_analysis_running = False
            st.session_state.ai_analysis_stop_requested = False
            
            if result["success"]:
                if result.get("stopped", False):
                    st.warning("🛑 AI 분석이 중지되었습니다.")
                else:
                    st.success("🎉 AI 분석이 완료되었습니다!")
                
                # 결과 요약 표시
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("✅ 성공", result["analyzed_count"])
                with col2:
                    st.metric("⏭️ 건너뜀", result["skipped_count"])
                with col3:
                    st.metric("❌ 실패", result["failed_count"])
                with col4:
                    st.metric("📊 총 처리", result["total_count"])
                
                # 건너뛴 이유 상세 정보 표시
                if result.get("skipped_count", 0) > 0:
                    st.markdown("#### 📋 건너뛴 이유 상세")
                    skip_col1, skip_col2 = st.columns(2)
                    with skip_col1:
                        st.info(f"🕐 최근 30일 이내 분석됨: **{result.get('skipped_recent_analysis', 0)}개**")
                    with skip_col2:
                        st.info(f"📝 posts 데이터 없음: **{result.get('skipped_no_posts', 0)}개**")
                
                
                # 실패한 항목들 표시
                if result.get("failed_items"):
                    st.markdown("### ❌ 실패한 항목들")
                    with st.expander(f"실패한 {len(result['failed_items'])}개 항목 상세보기"):
                        for item in result["failed_items"]:
                            st.error(f"**ID: {item['id']}** - {item['error']}")
            else:
                st.error(f"❌ AI 분석 실패: {result['error']}")

def execute_ai_analysis():
    """AI 분석 실행 함수 (배치 처리) - 안정화 버전"""
    try:
        # Supabase 클라이언트 1회 생성/재사용
        client = simple_client.get_client()
        if not client:
            return {"success": False, "error": "Supabase 클라이언트 생성 실패"}

        # 1. 전체 데이터 개수 (COMPLETE 상태만)
        total_count = get_completed_crawling_data_count(client)
        if total_count == 0:
            return {"success": False, "error": "분석할 크롤링 데이터가 없습니다."}

        # 디버깅: 전체 데이터 개수도 확인
        try:
            total_all_count = client.table("tb_instagram_crawling").select("id", count="exact").execute()
            st.info(f"📊 데이터 현황: 전체 {total_all_count.count:,}개 중 완료된 크롤링 데이터 {total_count:,}개 (status='COMPLETE')")
        except:
            st.info(f"총 {total_count:,}개의 완료된 크롤링 데이터(status='COMPLETE')가 있습니다.")
        
        st.info("배치 단위로 AI 분석을 시작합니다.")

        batch_size = 50
        total_batches = (total_count + batch_size - 1) // batch_size

        analyzed_count = 0
        skipped_count = 0
        skipped_recent_analysis = 0  # 최근 분석으로 건너뛴 개수
        skipped_no_posts = 0  # posts가 없어서 건너뛴 개수
        failed_count = 0
        processed_count = 0
        failed_items = []

        overall_progress_bar = st.progress(0)
        overall_status_text = st.empty()
        result_container = st.empty()

        UI_UPDATE_EVERY = 50  # 갱신 주기

        for batch_num in range(total_batches):
            # 중지 요청 확인
            if st.session_state.get("ai_analysis_stop_requested", False):
                st.warning("🛑 사용자에 의해 분석이 중지되었습니다.")
                return {
                    "success": True,
                    "stopped": True,
                    "analyzed_count": analyzed_count,
                    "skipped_count": skipped_count,
                    "skipped_recent_analysis": skipped_recent_analysis,
                    "skipped_no_posts": skipped_no_posts,
                    "failed_count": failed_count,
                    "total_count": total_count,
                    "failed_items": failed_items
                }
            
            offset = batch_num * batch_size
            batch_data = get_completed_crawling_data(client, limit=batch_size, offset=offset)
            
            if not batch_data:
                break

            # 배치 진행 UI (간소화)
            batch_progress_bar = st.progress(0)
            batch_status_text = st.empty()

            for index, data in enumerate(batch_data):
                # 각 항목 처리 전에도 중지 요청 확인
                if st.session_state.get("ai_analysis_stop_requested", False):
                    st.warning("🛑 사용자에 의해 분석이 중지되었습니다.")
                    return {
                        "success": True,
                        "stopped": True,
                        "analyzed_count": analyzed_count,
                        "skipped_count": skipped_count,
                        "failed_count": failed_count,
                        "total_count": total_count,
                        "failed_items": failed_items
                    }
                
                current_id = data.get('id', 'unknown')
                
                try:
                    # 전체/배치 진행률
                    overall_progress = (processed_count + index + 1) / total_count
                    overall_progress_bar.progress(overall_progress)
                    overall_status_text.text(
                        f"전체 진행: {processed_count + index + 1:,}/{total_count:,} (배치 {batch_num + 1}/{total_batches})"
                    )

                    batch_progress = (index + 1) / len(batch_data)
                    batch_progress_bar.progress(batch_progress)
                    batch_status_text.text(f"배치 {batch_num + 1} 진행: {index + 1}/{len(batch_data)} - {current_id}")

                    # 1) 최근 분석 여부 체크 (30일 이내 분석된 것은 건너뛰기)
                    # 새로운 조건에서는 ai_analysis_status.is_analyzed = FALSE인 것만 조회하므로
                    # 30일 체크는 선택적으로 적용 (강제 재분석 방지용)
                    if is_recently_analyzed_by_id(client, data["id"]):
                        skipped_count += 1
                        skipped_recent_analysis += 1
                        continue

                    # 2) 입력 구성 (posts는 자르지 않음)
                    posts_content = data.get("posts", "") or ""
                    if not posts_content:
                        skipped_count += 1
                        skipped_no_posts += 1
                        continue

                    ai_input_data = {
                        "id": data.get("id", ""),
                        "description": data.get("description", "") or "",
                        "posts": posts_content
                    }

                    # 3) AI 분석
                    analysis_result = perform_ai_analysis(ai_input_data)
                    if not analysis_result:
                        failed_items.append({"id": current_id, "error": "AI 분석 실패"})
                        failed_count += 1
                        continue

                    # 4) 변환
                    transformed_result = transform_to_db_format(ai_input_data, analysis_result, data["id"])
                    if not transformed_result:
                        failed_items.append({"id": current_id, "error": "데이터 변환 실패"})
                        failed_count += 1
                        continue

                    # 5) 저장
                    try:
                        save_ai_analysis_result(client, data, transformed_result, data["id"])
                        analyzed_count += 1
                    except Exception as se:
                        failed_items.append({"id": current_id, "error": f"저장 실패: {str(se)}"})
                        failed_count += 1
                        continue

                    # UI 업데이트(희소)
                    if ((index + 1) % UI_UPDATE_EVERY == 0) or (index == len(batch_data) - 1):
                        try:
                            with result_container.container():
                                st.markdown("### 📊 실시간 처리 결과")
                                c1, c2, c3, c4 = st.columns(4)
                                c1.metric("✅ 성공", analyzed_count)
                                c2.metric("⏭️ 건너뜀", skipped_count)
                                c3.metric("❌ 실패", failed_count)
                                c4.metric("📊 총 처리", processed_count + index + 1)
                                
                                # 건너뛴 이유 상세 정보
                                if skipped_count > 0:
                                    st.caption(f"건너뛴 이유: 최근 분석 {skipped_recent_analysis}개, posts 없음 {skipped_no_posts}개")
                                
                                # 중지 요청 상태 표시
                                if st.session_state.get("ai_analysis_stop_requested", False):
                                    st.warning("🛑 분석 중지 요청됨 - 현재 항목 완료 후 중지됩니다.")
                        except Exception as ui_error:
                            # UI 업데이트 실패해도 분석은 계속 진행
                            pass

                except Exception as e:
                    failed_items.append({"id": current_id, "error": f"예상치 못한 오류: {str(e)}"})
                    failed_count += 1
                    continue

            processed_count += len(batch_data)
            batch_progress_bar.empty()
            batch_status_text.empty()

            # 배치 간 휴식 최소화(또는 제거)
            if batch_num < total_batches - 1:
                time.sleep(0.1)

        overall_progress_bar.progress(1.0)
        overall_status_text.text("분석 완료!")

        with result_container.container():
            st.markdown("### 🎉 AI 분석 최종 결과")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("✅ 성공", analyzed_count, delta=f"{(analyzed_count/total_count*100):.1f}%")
            c2.metric("⏭️ 건너뜀", skipped_count, delta=f"{(skipped_count/total_count*100):.1f}%")
            c3.metric("❌ 실패", failed_count, delta=f"{(failed_count/total_count*100):.1f}%")
            c4.metric("📊 총 처리", total_count, delta="100%")
            
            # 건너뛴 이유 상세 정보 표시
            if skipped_count > 0:
                st.markdown("#### 📋 건너뛴 이유 상세")
                skip_col1, skip_col2 = st.columns(2)
                with skip_col1:
                    st.info(f"🕐 최근 30일 이내 분석됨: **{skipped_recent_analysis}개**")
                with skip_col2:
                    st.info(f"📝 posts 데이터 없음: **{skipped_no_posts}개**")

            if failed_items:
                st.markdown("### ❌ 실패한 항목들")
                with st.expander(f"실패한 {len(failed_items)}개 항목 상세보기"):
                    for item in failed_items:
                        st.error(f"**ID: {item['id']}** - {item['error']}")

        return {
            "success": True,
            "analyzed_count": analyzed_count,
            "skipped_count": skipped_count,
            "skipped_recent_analysis": skipped_recent_analysis,
            "skipped_no_posts": skipped_no_posts,
            "failed_count": failed_count,
            "total_count": total_count,
            "failed_items": failed_items
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
