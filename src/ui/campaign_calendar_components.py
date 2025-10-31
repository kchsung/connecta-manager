"""
캠페인 일정 캘린더(타임라인) 컴포넌트
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
try:
    # 선택적: 풀캘린더 컴포넌트 (월별 달력)
    from streamlit_calendar import calendar as fullcalendar
except Exception:  # 의존성 미설치 시 타임라인만 제공
    fullcalendar = None

from ..db.database import db_manager
from .common_functions import (
    format_campaign_type,
    format_campaign_status,
)
import hashlib


def _get_campaign_color(campaign_name: str) -> tuple:
    """
    캠페인 이름을 기반으로 일관된 색상을 반환
    RGB 튜플을 반환하며, 각 캠페인마다 고유한 색상이 할당됨
    """
    # 시각적으로 구별이 잘 되는 색상 팔레트
    color_palette = [
        "#4285F4",  # 파란색
        "#EA4335",  # 빨간색
        "#FBBC04",  # 노란색
        "#34A853",  # 초록색
        "#FF6D01",  # 주황색
        "#9C27B0",  # 보라색
        "#00BCD4",  # 청록색
        "#E91E63",  # 분홍색
        "#795548",  # 갈색
        "#607D8B",  # 청회색
        "#FF9800",  # 주황색2
        "#4CAF50",  # 초록색2
        "#2196F3",  # 파란색2
        "#F44336",  # 빨간색2
        "#9E9E9E",  # 회색
        "#3F51B5",  # 남색
        "#00ACC1",  # 청록색2
        "#8BC34A",  # 연두색
        "#FF5722",  # 진한 주황색
        "#673AB7",  # 보라색2
    ]
    
    # 캠페인 이름을 해시하여 색상 선택
    hash_obj = hashlib.md5(campaign_name.encode('utf-8'))
    hash_int = int(hash_obj.hexdigest(), 16)
    color_index = hash_int % len(color_palette)
    return color_palette[color_index]


def _prepare_campaign_timeline_df(campaigns):
    rows = []
    for c in campaigns:
        name = c.get("campaign_name", "N/A")
        ctype = c.get("campaign_type", "")
        status = c.get("status", "planned")
        start = c.get("start_date")
        end = c.get("end_date")

        # 날짜 파싱 (YYYY-MM-DD 형식 가정, 실패 시 None)
        def parse_date(v):
            if not v:
                return None
            try:
                if isinstance(v, str):
                    return datetime.strptime(v, "%Y-%m-%d").date()
                return v
            except Exception:
                return None

        start_dt = parse_date(start)
        end_dt = parse_date(end)

        # 종료일이 없고 시작일만 있으면 시작일로 1일 바 표시
        if start_dt and not end_dt:
            end_dt = start_dt

        # 시작일이 없으면 스킵 (타임라인 표시 불가)
        if not start_dt:
            continue

        rows.append({
            "캠페인": name,
            "시작": start_dt,
            "종료": end_dt,
            "유형": format_campaign_type(ctype),
            "상태": format_campaign_status(status),
            "라벨": f"{name} | {format_campaign_type(ctype)} | {format_campaign_status(status)}",
        })

    if not rows:
        return pd.DataFrame(columns=["캠페인", "시작", "종료", "유형", "상태", "라벨"])
    return pd.DataFrame(rows)


def render_campaign_calendar():
    """
    캠페인 일정을 캘린더(타임라인) 형태로 표시
    - 막대: 시작일~종료일
    - 텍스트: 캠페인명 | 유형 | 상태
    """
    st.markdown("### 📅 캠페인 캘린더")
    view_mode = st.segmented_control(
        "보기 방식",
        options=["달력", "타임라인"],
        selection_mode="single",
        default="달력",
        key="campaign_calendar_view_mode",
    )

    try:
        campaigns = db_manager.get_campaigns()
    except Exception as e:
        st.error(f"❌ 캠페인 데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return

    if not campaigns:
        st.info("표시할 캠페인이 없습니다. 먼저 캠페인을 생성해주세요.")
        return

    df = _prepare_campaign_timeline_df(campaigns)
    if df.empty:
        st.info("시작일이 등록된 캠페인이 없습니다. 캠페인 편집에서 날짜를 추가해주세요.")
        return

    # 공통 필터
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        types = ["전체"] + sorted([t for t in df["유형"].dropna().unique().tolist()])
        selected_type = st.selectbox("유형", types, key="calendar_filter_type")
    with col2:
        statuses = ["전체"] + sorted([s for s in df["상태"].dropna().unique().tolist()])
        selected_status = st.selectbox("상태", statuses, key="calendar_filter_status")
    with col3:
        search = st.text_input("검색 (캠페인명)", placeholder="캠페인 이름 검색", key="calendar_search")

    filtered = df.copy()
    if selected_type != "전체":
        filtered = filtered[filtered["유형"] == selected_type]
    if selected_status != "전체":
        filtered = filtered[filtered["상태"] == selected_status]
    if search:
        s = search.strip().lower()
        filtered = filtered[filtered["캠페인"].str.lower().str.contains(s)]

    if filtered.empty:
        st.warning("필터 결과가 없습니다. 필터를 변경해보세요.")
        return

    if view_mode == "달력":
        if fullcalendar is None:
            st.warning("월별 달력 보기를 위해 'streamlit-calendar' 패키지가 필요합니다. requirements.txt에 추가되었습니다. 배포 후 자동 활성화됩니다.")
        else:
            # FullCalendar 이벤트 변환 (끝 날짜는 다음날 00:00로 설정해 inclusive 처리)
            events = []
            for _, r in filtered.iterrows():
                end_date = r["종료"] or r["시작"]
                end_inclusive = end_date + timedelta(days=1)
                campaign_name = r['캠페인']
                color = _get_campaign_color(campaign_name)
                events.append({
                    "title": f"{campaign_name} | {r['유형']} | {r['상태']}",
                    "start": datetime.combine(r["시작"], datetime.min.time()).isoformat(),
                    "end": datetime.combine(end_inclusive, datetime.min.time()).isoformat(),
                    "allDay": True,
                    "backgroundColor": color,
                    "borderColor": color,
                    "textColor": "#ffffff",
                })

            calendar_options = {
                "initialView": "dayGridMonth",
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,dayGridWeek,dayGridDay",
                },
                "locale": "ko",
                "height": "auto",
                "weekNumbers": False,
                "displayEventEnd": True,
            }

            fullcalendar(events=events, options=calendar_options, key="campaign_fullcalendar")
    else:
        # 타임라인 차트 (캠페인별 색상 적용)
        # 각 캠페인에 고유 색상 맵 생성
        color_map = {}
        for campaign in filtered['캠페인'].unique():
            color_map[campaign] = _get_campaign_color(campaign)
        
        fig = px.timeline(
            filtered,
            x_start="시작",
            x_end="종료",
            y="캠페인",
            color="캠페인",
            hover_data={"유형": True, "상태": True, "시작": True, "종료": True},
            text="라벨",
            color_discrete_map=color_map,
            category_orders={"캠페인": filtered.sort_values(["시작", "종료"])['캠페인'].tolist()},
        )

        fig.update_traces(textposition="inside", cliponaxis=False)
        
        # 오늘 날짜 표시선 추가 (레이아웃 업데이트 전에)
        today = datetime.now().date()
        today_dt = datetime.combine(today, datetime.min.time())
        
        # 오늘 날짜는 항상 표시 (범위가 확장되어도 표시되도록)
        try:
            fig.add_vline(
                x=today_dt,
                line_dash="dash",
                line_color="#ff4d4f",
                line_width=3,
                opacity=1.0,
                annotation_text="오늘",
                annotation_position="top",
                annotation_font_size=14,
                annotation_font_color="#ff4d4f",
                annotation_bgcolor="rgba(255, 255, 255, 0.8)",
                annotation_borderpad=4,
            )
        except Exception:
            # 날짜 범위 밖이면 표시하지 않음
            pass
        
        fig.update_layout(
            height=max(400, 40 * len(filtered["캠페인"].unique())),
            xaxis_title="기간",
            yaxis_title="캠페인",
            legend_title="캠페인",
            margin=dict(l=200, r=10, t=30, b=10),  # 왼쪽 여백 증가로 캠페인 이름 표시 공간 확보
        )
        
        # Y축 텍스트 좌측 정렬 및 스타일
        fig.update_yaxes(
            ticklabelposition="outside left",
            tickangle=0,
            tickfont=dict(size=12),
        )

        st.plotly_chart(fig, use_container_width=True)


