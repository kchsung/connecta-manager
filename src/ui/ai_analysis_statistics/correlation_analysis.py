"""
AI 분석과 실제 성과 상관관계 분석 컴포넌트
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from ...supabase.simple_client import get_client

def get_campaigns():
    """캠페인 목록 조회"""
    try:
        from ...supabase.simple_client import simple_client
        campaigns = simple_client.get_campaigns()
        return campaigns
    except Exception as e:
        st.error(f"캠페인 목록 조회 중 오류: {str(e)}")
        return []

def get_campaign_performance_data(campaign_id):
    """캠페인 성과 데이터 조회 (AI 분석 + 실제 성과) - 매핑 테이블 사용"""
    try:
        from ...supabase.simple_client import simple_client
        client = simple_client.get_client()
        if not client:
            return None
        
        # 1. 캠페인 참여자 데이터 조회
        participations = client.table("campaign_influencer_participations").select(
            "id, influencer_id, sample_status"
        ).eq("campaign_id", campaign_id).execute()
        
        if not participations.data:
            return pd.DataFrame()
        
        participation_ids = [p['id'] for p in participations.data]
        
        # 2. 콘텐츠 데이터 조회
        contents = client.table("campaign_influencer_contents").select(
            "id, participation_id, content_url, posted_at, likes, comments, shares, views, clicks, conversions"
        ).in_("participation_id", participation_ids).execute()
        
        if not contents.data:
            return pd.DataFrame()
        
        content_ids = [c['id'] for c in contents.data]
        
        # 3. 매핑 테이블을 통한 인플루언서 정보 조회
        mappings = client.table("cic_influencer_map").select(
            "content_id, participation_id, influencer_id, platform, sns_id"
        ).in_("content_id", content_ids).execute()
        
        if not mappings.data:
            return pd.DataFrame()
        
        # 4. AI 분석 데이터 조회 (sns_id 기준)
        sns_ids = [m['sns_id'] for m in mappings.data if m['sns_id']]
        platforms = [m['platform'] for m in mappings.data if m['platform']]
        
    # Debug 메시지 제거
        
        ai_analyses = []
        if sns_ids and platforms:
            # sns_id와 platform으로 AI 분석 데이터 조회
            for i, sns_id in enumerate(sns_ids):
                platform = platforms[i] if i < len(platforms) else 'instagram'
                ai_data = client.table("ai_influencer_analyses_new").select(
                    "influencer_id, engagement_score, activity_score, communication_score, growth_potential_score, overall_score, followers, category, analyzed_at"
                ).eq("influencer_id", sns_id).eq("platform", platform).execute()
                
                if ai_data.data:
                    ai_analyses.extend(ai_data.data)
        
        # Debug 메시지 제거
        
        # 5. 데이터 병합
        performance_data = []
        ai_data_count = 0
        
        for content in contents.data:
            content_id = content['id']
            participation_id = content['participation_id']
            
            # 매핑 정보 찾기
            mapping = next((m for m in mappings.data if m['content_id'] == content_id), None)
            if not mapping:
                print(f"Debug - No mapping found for content_id: {content_id}")
                continue
            
            # 참여자 정보 찾기
            participation = next((p for p in participations.data if p['id'] == participation_id), None)
            if not participation:
                print(f"Debug - No participation found for participation_id: {participation_id}")
                continue
            
            # AI 분석 정보 찾기 (sns_id 기준)
            ai_analysis = None
            if mapping['sns_id'] and mapping['platform'] and ai_analyses:
                ai_analysis = next((a for a in ai_analyses 
                                  if a['influencer_id'] == mapping['sns_id']), None)
                if ai_analysis:
                    ai_data_count += 1
            
            # 데이터 포인트 생성
            data_point = {
                'content_id': content_id,
                'participation_id': participation_id,
                'influencer_id': mapping['influencer_id'],
                'sns_id': mapping['sns_id'],
                'platform': mapping['platform'],
                'sample_status': participation['sample_status'],
                'content_url': content['content_url'],
                'posted_at': content['posted_at'],
                'likes': content['likes'] or 0,
                'comments': content['comments'] or 0,
                'shares': content['shares'] or 0,
                'views': content['views'] or 0,
                'clicks': content['clicks'] or 0,
                'conversions': content['conversions'] or 0,
            }
            
            # AI 분석 데이터 추가
            if ai_analysis:
                data_point.update({
                    'engagement_score': ai_analysis.get('engagement_score'),
                    'activity_score': ai_analysis.get('activity_score'),
                    'communication_score': ai_analysis.get('communication_score'),
                    'growth_potential_score': ai_analysis.get('growth_potential_score'),
                    'overall_score': ai_analysis.get('overall_score'),
                    'followers': ai_analysis.get('followers'),
                    'category': ai_analysis.get('category'),
                    'analyzed_at': ai_analysis.get('analyzed_at')
                })
            else:
                data_point.update({
                    'engagement_score': None,
                    'activity_score': None,
                    'communication_score': None,
                    'growth_potential_score': None,
                    'overall_score': None,
                    'followers': None,
                    'category': None,
                    'analyzed_at': None
                })
            
            performance_data.append(data_point)
        
        # Debug 메시지 제거
        
        return pd.DataFrame(performance_data)
            
    except Exception as e:
        st.error(f"캠페인 성과 데이터 조회 중 오류: {str(e)}")
        return None

def render_correlation_analysis():
    """AI 분석과 실제 성과 상관관계 분석"""
    st.markdown("### 🔗 인공지능 성과 상관관계 분석")
    st.markdown("AI 분석 결과와 실제 캠페인 성과 간의 상관관계를 분석합니다.")
    
    # 캠페인 선택
    campaigns = get_campaigns()
    if not campaigns:
        st.warning("분석할 수 있는 캠페인이 없습니다.")
        return
    
    # 캠페인 선택 UI
    campaign_options = {f"{campaign['campaign_name']} ({campaign['created_at'][:10]})": campaign['id'] 
                       for campaign in campaigns}
    
    selected_campaign_name = st.selectbox(
        "분석할 캠페인을 선택하세요:",
        options=list(campaign_options.keys()),
        key="campaign_selector"
    )
    
    if not selected_campaign_name:
        st.info("캠페인을 선택해주세요.")
        return
    
    selected_campaign_id = campaign_options[selected_campaign_name]
    
    # 성과 데이터 조회
    with st.spinner("캠페인 성과 데이터를 조회하는 중..."):
        performance_data = get_campaign_performance_data(selected_campaign_id)
    
    if performance_data is None:
        st.error("성과 데이터를 불러올 수 없습니다.")
        return
    
    if performance_data.empty:
        st.warning("선택한 캠페인에 대한 성과 데이터가 없습니다.")
        return
    
    # AI 분석 데이터가 있는 콘텐츠만 필터링
    ai_data = performance_data.dropna(subset=['engagement_score', 'overall_score'])
    
    if ai_data.empty:
        st.warning("AI 분석 데이터가 있는 콘텐츠가 없습니다.")
        return
    
    st.success(f"총 {len(performance_data)}개의 콘텐츠 중 {len(ai_data)}개의 콘텐츠에 AI 분석 데이터가 있습니다.")
    
    # 1. AI 점수와 실제 성과 상관관계 분석
    st.markdown("#### 📊 AI 점수와 실제 성과 상관관계")
    
    # 상관관계 계산 (shares 제외) - 0으로 나누기 방지
    correlation_columns = ['engagement_score', 'activity_score', 'communication_score', 
                          'growth_potential_score', 'overall_score', 'likes', 'comments', 
                          'views', 'clicks', 'conversions']
    
    # NaN 값과 무한대 값 제거
    correlation_data_clean = ai_data[correlation_columns].replace([np.inf, -np.inf], np.nan).dropna()
    
    if len(correlation_data_clean) > 1:
        correlation_data = correlation_data_clean.corr()
    else:
        # 데이터가 부족한 경우 빈 상관관계 매트릭스 생성
        correlation_data = pd.DataFrame(index=correlation_columns, columns=correlation_columns)
    
    # AI 점수와 성과 지표 간 상관관계만 추출 (shares 제외)
    ai_scores = ['engagement_score', 'activity_score', 'communication_score', 'growth_potential_score', 'overall_score']
    performance_metrics = ['likes', 'comments', 'views', 'clicks', 'conversions']
    
    ai_performance_corr = correlation_data.loc[ai_scores, performance_metrics]
    
    # 히트맵 생성
    fig = px.imshow(
        ai_performance_corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=px.colors.sequential.Viridis,
        title="AI 점수와 실제 성과 간 상관관계",
        labels=dict(color="상관계수")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 해석 추가
    with st.expander("📈 해석", expanded=False):
        st.markdown("""
        - **진한 색상 (높은 상관계수)**: AI 점수와 성과 지표 간 강한 관계
        - **연한 색상 (낮은 상관계수)**: AI 점수와 성과 지표 간 약한 관계
        - **0.3 이상**의 상관계수는 실무에서 의미있는 관계로 간주
        - **양수**: AI 점수가 높을수록 성과도 높아짐
        - **음수**: AI 점수가 높을수록 성과는 낮아짐
        """)
    
    # 2. AI 점수별 성과 분석
    st.markdown("#### 📈 AI 점수별 평균 성과")
    
    # AI 점수 구간별 성과 분석
    ai_data = ai_data.copy()  # SettingWithCopyWarning 방지
    ai_data['overall_score_group'] = pd.cut(ai_data['overall_score'], 
                                           bins=[0, 3, 6, 8, 10], 
                                           labels=['낮음(0-3)', '보통(3-6)', '높음(6-8)', '매우높음(8-10)'])
    
    score_performance = ai_data.groupby('overall_score_group', observed=True).agg({
        'likes': 'mean',
        'comments': 'mean', 
        'views': 'mean',
        'clicks': 'mean',
        'conversions': 'mean'
    }).round(2)
    
    # 막대 그래프 생성
    fig = px.bar(
        score_performance.reset_index(),
        x='overall_score_group',
        y=['likes', 'comments', 'views', 'clicks', 'conversions'],
        barmode='group',
        title="AI 종합점수 구간별 평균 성과",
        labels={'value': '평균 성과', 'variable': '성과 지표'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 해석 추가
    with st.expander("📈 해석", expanded=False):
        st.markdown("""
        - **AI 종합점수가 높을수록** 대부분의 성과 지표가 증가하는 경향
        - **좋아요, 댓글, 조회수** 등이 AI 점수와 함께 증가하는지 확인
        - **클릭, 전환** 등 비즈니스 지표와의 관계도 중요
        - **구간별 차이**가 명확할수록 AI 점수의 예측력이 높음
        """)
    
    # 3. 개별 AI 점수와 성과 상관관계
    st.markdown("#### 🎯 개별 AI 점수와 성과 상관관계")
    
    # 참여도 점수와 좋아요 수
    fig1 = px.scatter(
        ai_data,
        x='engagement_score',
        y='likes',
        color='category',
        size='followers',
        title="참여도 점수 vs 좋아요 수",
        labels={'engagement_score': '참여도 점수', 'likes': '좋아요 수'}
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # 종합점수와 조회수
    fig2 = px.scatter(
        ai_data,
        x='overall_score',
        y='views',
        color='category',
        size='followers',
        title="종합점수 vs 조회수",
        labels={'overall_score': '종합점수', 'views': '조회수'}
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # 해석 추가
    with st.expander("📈 해석", expanded=False):
        st.markdown("""
        - **산점도 패턴**: 점들이 대각선을 따라 분포하면 강한 상관관계
        - **버블 크기**: 팔로워 수가 많을수록 큰 버블로 표시
        - **색상 구분**: 카테고리별로 다른 색상으로 구분
        - **오른쪽 위**: AI 점수와 성과가 모두 높은 우수 콘텐츠
        - **왼쪽 아래**: AI 점수와 성과가 모두 낮은 개선 필요 콘텐츠
        """)
    
    # 4. AI 지표별 상관관계 상세 분석
    st.markdown("#### 📊 AI 지표별 상관관계 상세 분석")
    
    # AI 지표와 성과 지표 간의 상관관계 매트릭스 (shares 제외)
    ai_metrics = ['engagement_score', 'activity_score', 'communication_score', 'growth_potential_score', 'overall_score']
    performance_metrics = ['likes', 'comments', 'views', 'clicks', 'conversions']
    
    # 상관관계 계산 - 0으로 나누기 방지
    correlation_data_clean = ai_data[ai_metrics + performance_metrics].replace([np.inf, -np.inf], np.nan).dropna()
    
    if len(correlation_data_clean) > 1:
        correlation_matrix = correlation_data_clean.corr()
        ai_performance_corr = correlation_matrix.loc[ai_metrics, performance_metrics]
    else:
        # 데이터가 부족한 경우 빈 상관관계 매트릭스 생성
        ai_performance_corr = pd.DataFrame(index=ai_metrics, columns=performance_metrics)
    
    # 상관관계 히트맵
    fig = px.imshow(
        ai_performance_corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=px.colors.sequential.RdBu,
        title="AI 지표와 성과 지표 간 상관관계 매트릭스",
        labels=dict(color="상관계수")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 해석 추가
    with st.expander("📈 해석", expanded=False):
        st.markdown("""
        - **상세 상관관계 매트릭스**: 각 AI 지표와 성과 지표 간의 정확한 상관계수
        - **빨간색 (양수)**: AI 지표가 높을수록 성과도 높아짐
        - **파란색 (음수)**: AI 지표가 높을수록 성과는 낮아짐
        - **진한 색상**: 강한 상관관계 (0.5 이상)
        - **연한 색상**: 약한 상관관계 (0.3 미만)
        - **실무 활용**: 0.3 이상의 상관계수를 가진 지표를 우선적으로 활용
        """)
    
    # 5. AI 지표별 성과 예측력 순위
    st.markdown("#### 🎯 AI 지표별 성과 예측력 순위")
    
    # 각 AI 지표별로 성과 지표들과의 평균 상관관계 계산
    ai_prediction_power = {}
    for ai_metric in ai_metrics:
        correlations = []
        for perf_metric in performance_metrics:
            # 0으로 나누기 방지를 위해 유효한 데이터만 사용
            valid_data = ai_data[[ai_metric, perf_metric]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(valid_data) > 1:  # 최소 2개 데이터 필요
                try:
                    corr = valid_data[ai_metric].corr(valid_data[perf_metric])
                    if not pd.isna(corr) and not np.isinf(corr):
                        correlations.append(abs(corr))  # 절댓값으로 강도 측정
                except Exception:
                    # 상관관계 계산 실패 시 건너뛰기
                    continue
        ai_prediction_power[ai_metric] = np.mean(correlations) if correlations else 0
    
    # 예측력 순위 정렬
    prediction_ranking = sorted(ai_prediction_power.items(), key=lambda x: x[1], reverse=True)
    
    # 막대 그래프로 표시
    ranking_df = pd.DataFrame(prediction_ranking, columns=['AI 지표', '평균 상관계수'])
    ranking_df['AI 지표명'] = ranking_df['AI 지표'].map({
        'engagement_score': '참여도 점수',
        'activity_score': '활동성 점수', 
        'communication_score': '커뮤니케이션 점수',
        'growth_potential_score': '성장잠재력 점수',
        'overall_score': '종합점수'
    })
    
    fig = px.bar(
        ranking_df,
        x='AI 지표명',
        y='평균 상관계수',
        title="AI 지표별 성과 예측력 순위 (평균 상관계수)",
        color='평균 상관계수',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # 해석 추가
    with st.expander("📈 해석", expanded=False):
        st.markdown("""
        - **높은 막대**: 해당 AI 지표가 성과 예측에 더 유용함
        - **낮은 막대**: 해당 AI 지표의 성과 예측력이 낮음
        - **순위 1위**: 가장 신뢰할 수 있는 성과 예측 지표
        - **순위 하위**: 개선이 필요하거나 다른 지표에 비해 덜 중요
        - **실무 활용**: 상위 3개 지표를 우선적으로 모니터링
        """)
    
    # 6. 개별 AI 지표와 성과 지표 상관관계 분석
    st.markdown("#### 🔍 개별 AI 지표와 성과 지표 상관관계")
    
    # 상관관계 기준 설명
    with st.expander("📊 상관관계 강도 기준", expanded=False):
        st.markdown("""
        **상관관계 강도 기준:**
        - **매우 강함 (0.7 이상)**: 매우 강한 선형 관계
        - **강함 (0.5-0.7)**: 강한 선형 관계  
        - **보통 (0.3-0.5)**: 보통 수준의 선형 관계
        - **약함 (0.2-0.3)**: 약한 선형 관계
        - **매우 약함 (0.1-0.2)**: 매우 약한 선형 관계
        - **거의 없음 (0.1 미만)**: 거의 없는 선형 관계
        
        **해석 가이드:**
        - **0.2-0.3**: 실제 데이터에서는 의미있는 상관관계로 간주
        - **0.3-0.5**: 중간 정도의 상관관계, 실무에서 유용
        - **0.5 이상**: 강한 상관관계, 예측에 활용 가능
        - **0.7 이상**: 매우 강한 상관관계, 높은 신뢰도
        """)
    
    # 각 AI 지표별로 가장 높은 상관관계를 가진 성과 지표 찾기
    for ai_metric in ai_metrics:
        st.markdown(f"**{ranking_df[ranking_df['AI 지표'] == ai_metric]['AI 지표명'].iloc[0]}**")
        
        # 해당 AI 지표와 성과 지표들의 상관관계
        metric_correlations = []
        for perf_metric in performance_metrics:
            # 0으로 나누기 방지를 위해 유효한 데이터만 사용
            valid_data = ai_data[[ai_metric, perf_metric]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(valid_data) > 1:  # 최소 2개 데이터 필요
                try:
                    corr = valid_data[ai_metric].corr(valid_data[perf_metric])
                    if not pd.isna(corr) and not np.isinf(corr):
                        metric_correlations.append({
                            '성과지표': perf_metric,
                            '상관계수': corr,
                            '절댓값': abs(corr)
                        })
                except Exception:
                    # 상관관계 계산 실패 시 건너뛰기
                    continue
        
        if metric_correlations:
            metric_df = pd.DataFrame(metric_correlations).sort_values('절댓값', ascending=False)
            
            # 상위 3개 성과 지표 표시
            col1, col2, col3 = st.columns(3)
            for i, (_, row) in enumerate(metric_df.head(3).iterrows()):
                with [col1, col2, col3][i]:
                    # 상관관계 강도 기준 조정 (더 현실적인 기준)
                    corr_abs = abs(row['상관계수'])
                    if corr_abs >= 0.7:
                        strength = "매우 강함"
                        delta_color = "normal"
                    elif corr_abs >= 0.5:
                        strength = "강함"
                        delta_color = "normal"
                    elif corr_abs >= 0.3:
                        strength = "보통"
                        delta_color = "normal"
                    elif corr_abs >= 0.2:
                        strength = "약함"
                        delta_color = "normal"
                    elif corr_abs >= 0.1:
                        strength = "매우 약함"
                        delta_color = "normal"
                    else:
                        strength = "거의 없음"
                        delta_color = "normal"
                    
                    st.metric(
                        f"{row['성과지표']}",
                        f"{row['상관계수']:.3f}",
                        delta=f"{strength}",
                        delta_color=delta_color
                    )
        
        st.markdown("---")
    
    # 7. AI 지표 조합별 성과 예측력 분석
    st.markdown("#### 🔮 AI 지표 조합별 성과 예측력 분석")
    
    # AI 지표 조합과 성과 지표 간의 상관관계 분석
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    
    # 각 성과 지표별로 AI 지표들의 예측력 분석
    performance_analysis = {}
    
    for perf_metric in performance_metrics:
        # 유효한 데이터만 필터링
        valid_data = ai_data.dropna(subset=ai_metrics + [perf_metric])
        
        if len(valid_data) < 5:  # 최소 5개 데이터 필요
            continue
        
        # 무한대 값이나 NaN 값이 있는지 확인
        if valid_data[perf_metric].isin([np.inf, -np.inf]).any():
            continue
            
        # AI 지표들을 특성으로, 성과 지표를 타겟으로 설정
        X = valid_data[ai_metrics].values
        y = valid_data[perf_metric].values
        
        # 무한대 값이 있는지 확인
        if np.isinf(X).any() or np.isinf(y).any():
            continue
        
        try:
            # 선형 회귀 모델 훈련
            model = LinearRegression()
            model.fit(X, y)
            
            # 예측 및 R² 점수 계산
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            
            # R² 점수가 유효한지 확인
            if not np.isnan(r2) and not np.isinf(r2):
                # 특성 중요도 (계수 절댓값)
                feature_importance = dict(zip(ai_metrics, np.abs(model.coef_)))
                
                performance_analysis[perf_metric] = {
                    'r2_score': r2,
                    'feature_importance': feature_importance,
                    'data_count': len(valid_data)
                }
        except Exception as e:
            # 모델 훈련 실패 시 해당 성과 지표 건너뛰기
            continue
    
    # 성과 지표별 예측력 표시
    if performance_analysis:
        perf_df = pd.DataFrame([
            {
                '성과지표': metric,
                'R² 점수': analysis['r2_score'],
                '데이터 수': analysis['data_count']
            }
            for metric, analysis in performance_analysis.items()
        ]).sort_values('R² 점수', ascending=False)
        
        fig = px.bar(
            perf_df,
            x='성과지표',
            y='R² 점수',
            title="AI 지표 조합으로 각 성과지표 예측력 (R² 점수)",
            color='R² 점수',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 해석 추가
        with st.expander("📈 해석", expanded=False):
            st.markdown("""
            - **R² 점수**: AI 지표 조합이 해당 성과를 얼마나 잘 예측하는지 (0-1 범위)
            - **0.7 이상**: 매우 우수한 예측력 (70% 이상 설명 가능)
            - **0.5-0.7**: 좋은 예측력 (50-70% 설명 가능)
            - **0.3-0.5**: 보통 예측력 (30-50% 설명 가능)
            - **0.3 미만**: 낮은 예측력 (30% 미만 설명)
            - **실무 활용**: R² 0.5 이상인 성과 지표를 우선적으로 AI로 예측
            """)
        
        # 각 성과 지표별로 가장 중요한 AI 지표 표시
        st.markdown("#### 🎯 성과 지표별 주요 예측 AI 지표")
        
        for metric, analysis in performance_analysis.items():
            if analysis['r2_score'] > 0.1:  # R² > 0.1인 경우만 표시
                st.markdown(f"**{metric}** (R² = {analysis['r2_score']:.3f})")
                
                # AI 지표 중요도 순위
                importance_df = pd.DataFrame([
                    {'AI 지표': ai_metric, '중요도': importance}
                    for ai_metric, importance in analysis['feature_importance'].items()
                ]).sort_values('중요도', ascending=False)
                
                # 상위 3개 AI 지표 표시
                col1, col2, col3 = st.columns(3)
                for i, (_, row) in enumerate(importance_df.head(3).iterrows()):
                    with [col1, col2, col3][i]:
                        ai_metric_name = {
                            'engagement_score': '참여도',
                            'activity_score': '활동성',
                            'communication_score': '커뮤니케이션',
                            'growth_potential_score': '성장잠재력',
                            'overall_score': '종합점수'
                        }.get(row['AI 지표'], row['AI 지표'])
                        
                        st.metric(
                            f"{ai_metric_name}",
                            f"{row['중요도']:.3f}",
                            delta=f"{'높음' if row['중요도'] > 0.5 else '보통' if row['중요도'] > 0.2 else '낮음'}"
                        )
                
                st.markdown("---")
    
    # 6. 데이터 요약 테이블
    st.markdown("#### 📋 분석 요약")
    
    # 무한대 값과 NaN 값 처리
    def safe_mean(series):
        """무한대 값과 NaN 값을 제거하고 평균 계산"""
        clean_series = series.replace([np.inf, -np.inf], np.nan).dropna()
        return clean_series.mean() if len(clean_series) > 0 else 0
    
    summary_data = {
        '지표': ['총 콘텐츠 수', 'AI 분석 데이터 수', '평균 종합점수', '평균 좋아요 수', '평균 조회수', '평균 댓글 수', '평균 클릭 수', '평균 전환 수'],
        '값': [
            len(performance_data),
            len(ai_data),
            round(safe_mean(ai_data['overall_score']), 2),
            round(safe_mean(ai_data['likes']), 0),
            round(safe_mean(ai_data['views']), 0),
            round(safe_mean(ai_data['comments']), 0),
            round(safe_mean(ai_data['clicks']), 0),
            round(safe_mean(ai_data['conversions']), 0)
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, width='stretch')
    
    # 해석 추가
    with st.expander("📈 해석", expanded=False):
        st.markdown("""
        - **총 콘텐츠 수**: 분석 대상이 된 전체 콘텐츠 수
        - **AI 분석 데이터 수**: AI 분석이 완료된 콘텐츠 수
        - **평균 종합점수**: AI가 평가한 전체적인 품질 점수 (0-10)
        - **평균 성과 지표**: 실제로 달성된 성과 수치들
        - **데이터 품질**: AI 분석 데이터 비율이 높을수록 신뢰할 수 있는 분석
        - **비즈니스 가치**: 클릭, 전환 등 비즈니스 지표가 높을수록 실질적 성과
        """)
    
    # 8. AI 지표별 인사이트 제공
    st.markdown("#### 💡 AI 지표별 주요 인사이트")
    
    # AI 지표별 예측력 순위에서 인사이트 도출
    if prediction_ranking:
        best_ai_metric = prediction_ranking[0]
        worst_ai_metric = prediction_ranking[-1]
        
        ai_metric_names = {
            'engagement_score': '참여도 점수',
            'activity_score': '활동성 점수',
            'communication_score': '커뮤니케이션 점수',
            'growth_potential_score': '성장잠재력 점수',
            'overall_score': '종합점수'
        }
        
        st.info(f"**가장 예측력이 높은 AI 지표**: {ai_metric_names.get(best_ai_metric[0], best_ai_metric[0])} (평균 상관계수: {best_ai_metric[1]:.3f})")
        st.info(f"**가장 예측력이 낮은 AI 지표**: {ai_metric_names.get(worst_ai_metric[0], worst_ai_metric[0])} (평균 상관계수: {worst_ai_metric[1]:.3f})")
    
    # 성과 예측 정확도 평가
    if performance_analysis:
        avg_r2 = np.mean([analysis['r2_score'] for analysis in performance_analysis.values()])
        
        if avg_r2 > 0.5:
            st.success("✅ AI 지표들이 실제 성과를 매우 잘 예측하고 있습니다.")
        elif avg_r2 > 0.3:
            st.warning("⚠️ AI 지표들이 어느 정도 성과를 예측하지만 개선이 필요합니다.")
        elif avg_r2 > 0.1:
            st.info("ℹ️ AI 지표들이 일부 성과를 예측하지만 상당한 개선이 필요합니다.")
        else:
            st.error("❌ AI 지표들과 실제 성과 간의 예측력이 매우 낮습니다.")
        
        # 가장 예측 가능한 성과 지표
        best_performance = max(performance_analysis.items(), key=lambda x: x[1]['r2_score'])
        st.info(f"**가장 예측 가능한 성과 지표**: {best_performance[0]} (R² = {best_performance[1]['r2_score']:.3f})")
    
    # AI 지표별 개선 권장사항
    st.markdown("#### 🔧 AI 지표 개선 권장사항")
    
    if prediction_ranking:
        for i, (metric, score) in enumerate(prediction_ranking):
            metric_name = ai_metric_names.get(metric, metric)
            
            # 더 현실적인 기준으로 조정
            if score >= 0.4:
                st.success(f"✅ **{metric_name}**: 우수한 예측력을 보입니다. (평균 상관계수: {score:.3f})")
            elif score >= 0.2:
                st.warning(f"⚠️ **{metric_name}**: 보통 수준의 예측력입니다. (평균 상관계수: {score:.3f})")
            elif score >= 0.1:
                st.info(f"ℹ️ **{metric_name}**: 약한 예측력이지만 의미있는 수준입니다. (평균 상관계수: {score:.3f})")
            else:
                st.error(f"❌ **{metric_name}**: 매우 낮은 예측력을 보입니다. (평균 상관계수: {score:.3f})")
    
    # 데이터 품질 평가
    st.markdown("#### 📊 데이터 품질 평가")
    
    total_contents = len(performance_data)
    ai_analyzed_contents = len(ai_data)
    ai_coverage = (ai_analyzed_contents / total_contents) * 100 if total_contents > 0 else 0
    
    st.metric("AI 분석 데이터 커버리지", f"{ai_coverage:.1f}%", f"{ai_analyzed_contents}/{total_contents}")
    
    if ai_coverage > 80:
        st.success("✅ 높은 AI 분석 데이터 커버리지로 신뢰할 수 있는 분석 결과입니다.")
    elif ai_coverage > 50:
        st.warning("⚠️ 보통 수준의 AI 분석 데이터 커버리지입니다. 더 많은 데이터 수집을 권장합니다.")
    else:
        st.error("❌ 낮은 AI 분석 데이터 커버리지로 분석 결과의 신뢰성이 제한적입니다.")