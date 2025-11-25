"""
커머스 지향성 통계 컴포넌트
"""
import streamlit as st
import plotly.express as px
import numpy as np
from .common_functions import get_commerce_orientation_statistics


def _filter_numeric(values):
    """히스토그램용 숫자 데이터 정제"""
    if not values:
        return []
    filtered = []
    for value in values:
        try:
            num = float(value)
            if np.isfinite(num):
                filtered.append(num)
        except (ValueError, TypeError):
            continue
    return filtered


def render_commerce_orientation_statistics():
    """커머스 지향성 통계"""
    st.markdown("### 🛒 커머스 지향성 통계")
    
    stats = get_commerce_orientation_statistics()
    if not stats:
        st.warning("커머스 지향성 통계 데이터를 찾을 수 없습니다.")
        return
    
    st.markdown("#### 📌 핵심 지표")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("평균 수익화 성향", f"{stats.get('avg_monetization_intent', 0):.1f}/10")
    col2.metric("중앙값 수익화 성향", f"{stats.get('median_monetization_intent', 0):.1f}/10")
    col3.metric("평균 커머스 적합도", f"{stats.get('avg_content_fit', 0):.1f}/10")
    col4.metric("평균 판매 신호 수", f"{stats.get('avg_selling_signal_per_creator', 0):.1f}개")
    
    st.markdown("#### 📊 점수 분포")
    monetization_data = _filter_numeric(stats.get("monetization_distribution"))
    content_fit_data = _filter_numeric(stats.get("content_fit_distribution"))
    
    col_left, col_right = st.columns(2)
    with col_left:
        if monetization_data:
            fig = px.histogram(
                x=monetization_data,
                nbins=15,
                title="수익화 성향 점수 분포",
                labels={'x': '수익화 성향 점수', 'y': '빈도'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("수익화 성향 점수 데이터가 없습니다.")
    
    with col_right:
        if content_fit_data:
            fig = px.histogram(
                x=content_fit_data,
                nbins=15,
                title="커머스 적합도 점수 분포",
                labels={'x': '커머스 적합도 점수', 'y': '빈도'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("커머스 적합도 점수 데이터가 없습니다.")
    
    st.markdown("#### 🧬 유형 분포")
    archetype_dist = stats.get("archetype_distribution", {})
    motivation_dist = stats.get("primary_motivation_distribution", {})
    
    col_left, col_right = st.columns(2)
    with col_left:
        if archetype_dist:
            fig = px.pie(
                values=list(archetype_dist.values()),
                names=list(archetype_dist.keys()),
                title="크리에이터 유형 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("크리에이터 유형 데이터가 없습니다.")
    
    with col_right:
        if motivation_dist:
            fig = px.bar(
                x=list(motivation_dist.keys()),
                y=list(motivation_dist.values()),
                title="주요 동기 분포",
                labels={'x': '주요 동기', 'y': '인원 수'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("주요 동기 데이터가 없습니다.")
    
    st.markdown("#### 🛍️ 판매/과시 신호 상위 항목")
    selling_signals = stats.get("selling_signal_counts", {})
    bragging_signals = stats.get("bragging_signal_counts", {})
    
    col_left, col_right = st.columns(2)
    with col_left:
        if selling_signals:
            fig = px.bar(
                x=list(selling_signals.keys()),
                y=list(selling_signals.values()),
                title="판매 노력 신호 TOP 항목",
                labels={'x': '신호', 'y': '빈도'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("판매 노력 신호 데이터가 없습니다.")
    
    with col_right:
        if bragging_signals:
            fig = px.bar(
                x=list(bragging_signals.keys()),
                y=list(bragging_signals.values()),
                title="과시 신호 TOP 항목",
                labels={'x': '신호', 'y': '빈도'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("과시 신호 데이터가 없습니다.")
    
    st.markdown("#### 💡 주요 해석")
    interpretations = stats.get("sample_interpretations", [])
    if interpretations:
        for idx, text in enumerate(interpretations, start=1):
            st.markdown(f"**{idx}.** {text}")
    else:
        st.info("추가 해석 데이터가 없습니다.")

