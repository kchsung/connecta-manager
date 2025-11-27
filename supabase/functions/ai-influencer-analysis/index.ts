import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // CORS preflight request
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Supabase 클라이언트 생성
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const { action, data } = await req.json()

    switch (action) {
      case 'get_crawling_data':
        return await getCrawlingData(supabaseClient)
      
      case 'check_recent_analysis':
        return await checkRecentAnalysis(supabaseClient, data)
      
      case 'save_analysis_result':
        return await saveAnalysisResult(supabaseClient, data)
      
      case 'get_analysis_data':
        return await getAnalysisData(supabaseClient, data)
      
      case 'get_statistics':
        return await getStatistics(supabaseClient)
      
      case 'get_campaign_analysis':
        return await getCampaignAnalysis(supabaseClient, data)
      
      case 'save_campaign_analysis':
        return await saveCampaignAnalysis(supabaseClient, data)
      
      default:
        return new Response(
          JSON.stringify({ error: 'Invalid action' }),
          { 
            status: 400, 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
          }
        )
    }
  } catch (error) {
    console.error('Error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})

// 크롤링 완료된 데이터 조회
async function getCrawlingData(supabaseClient: any) {
  try {
    const { data, error } = await supabaseClient
      .from('tb_instagram_crawling')
      .select('*')
      .eq('status', 'COMPLETE')

    if (error) throw error

    return new Response(
      JSON.stringify({ success: true, data }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}

// 최근 분석 여부 확인 (1달 이내)
async function checkRecentAnalysis(supabaseClient: any, data: any) {
  try {
    const { influencer_id, platform } = data
    const oneMonthAgo = new Date()
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)

    const { data: analysisData, error } = await supabaseClient
      .from('ai_influencer_analyses')
      .select('analyzed_at')
      .eq('influencer_id', influencer_id)
      .eq('platform', platform)
      .gte('analyzed_at', oneMonthAgo.toISOString())

    if (error) throw error

    const isRecentlyAnalyzed = analysisData && analysisData.length > 0

    return new Response(
      JSON.stringify({ success: true, isRecentlyAnalyzed }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}

// AI 분석 결과 저장
async function saveAnalysisResult(supabaseClient: any, data: any) {
  try {
    const { crawling_data, analysis_result } = data

    // 기존 데이터 확인
    const { data: existingData, error: checkError } = await supabaseClient
      .from('ai_influencer_analyses')
      .select('id')
      .eq('influencer_id', crawling_data.influencer_id)
      .eq('platform', crawling_data.platform)

    if (checkError) throw checkError

    // 데이터 준비
    const analysisData = {
      influencer_id: crawling_data.influencer_id,
      platform: crawling_data.platform,
      name: crawling_data.name || '',
      alias: crawling_data.alias || '',
      followers: crawling_data.followers || 0,
      followings: crawling_data.followings || 0,
      posts_count: crawling_data.posts_count || 0,
      category: analysis_result.category || '기타',
      tags: analysis_result.tags || [],
      follow_network_analysis: analysis_result.follow_network_analysis || {},
      comment_authenticity_analysis: analysis_result.comment_authenticity_analysis || {},
      content_analysis: analysis_result.content_analysis || {},
      evaluation: analysis_result.evaluation || {},
      insights: analysis_result.insights || {},
      summary: analysis_result.summary || '',
      recommendation: analysis_result.recommendation || '보통',
      notes: analysis_result.notes || {},
      source: 'ai_auto',
      analyzed_at: new Date().toISOString(),
      analyzed_on: new Date().toISOString().split('T')[0]
    }

    let result
    if (existingData && existingData.length > 0) {
      // 업데이트
      const { data: updateData, error: updateError } = await supabaseClient
        .from('ai_influencer_analyses')
        .update(analysisData)
        .eq('id', existingData[0].id)
        .select()

      if (updateError) throw updateError
      result = updateData
    } else {
      // 새로 생성
      const { data: insertData, error: insertError } = await supabaseClient
        .from('ai_influencer_analyses')
        .insert(analysisData)
        .select()

      if (insertError) throw insertError
      result = insertData
    }

    return new Response(
      JSON.stringify({ success: true, data: result }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}

// AI 분석 데이터 조회
async function getAnalysisData(supabaseClient: any, data: any) {
  try {
    const { search_term, category_filter, recommendation_filter } = data

    let query = supabaseClient.from('ai_influencer_analyses').select('*')

    // 검색 조건
    if (search_term) {
      query = query.or(`name.ilike.%${search_term}%,tags.cs.{${search_term}}`)
    }

    // 카테고리 필터
    if (category_filter && category_filter !== '전체') {
      query = query.eq('category', category_filter)
    }

    // 추천도 필터
    if (recommendation_filter && recommendation_filter !== '전체') {
      query = query.eq('recommendation', recommendation_filter)
    }

    const { data: analysisData, error } = await query
      .order('analyzed_at', { ascending: false })

    if (error) throw error

    return new Response(
      JSON.stringify({ success: true, data: analysisData }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}

// 통계 데이터 조회
async function getStatistics(supabaseClient: any) {
  try {
    // 총 분석 수
    const { count: totalCount, error: totalError } = await supabaseClient
      .from('ai_influencer_analyses')
      .select('*', { count: 'exact', head: true })

    if (totalError) throw totalError

    // 최근 7일 분석 수
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)

    const { count: recentCount, error: recentError } = await supabaseClient
      .from('ai_influencer_analyses')
      .select('*', { count: 'exact', head: true })
      .gte('analyzed_at', sevenDaysAgo.toISOString())

    if (recentError) throw recentError

    // 평균 종합점수
    const { data: scoresData, error: scoresError } = await supabaseClient
      .from('ai_influencer_analyses')
      .select('overall_score')
      .not('overall_score', 'is', null)

    if (scoresError) throw scoresError

    const avgScore = scoresData && scoresData.length > 0 
      ? scoresData.reduce((sum: number, item: any) => sum + (item.overall_score || 0), 0) / scoresData.length
      : 0

    // 추천도 분포
    const { data: recommendationsData, error: recommendationsError } = await supabaseClient
      .from('ai_influencer_analyses')
      .select('recommendation')

    if (recommendationsError) throw recommendationsError

    const recommendationDist: { [key: string]: number } = {}
    if (recommendationsData) {
      recommendationsData.forEach((item: any) => {
        if (item.recommendation) {
          recommendationDist[item.recommendation] = (recommendationDist[item.recommendation] || 0) + 1
        }
      })
    }

    // 카테고리별 통계
    const { data: categoriesData, error: categoriesError } = await supabaseClient
      .from('ai_influencer_analyses')
      .select('category')

    if (categoriesError) throw categoriesError

    const categoryStats: { [key: string]: number } = {}
    if (categoriesData) {
      categoriesData.forEach((item: any) => {
        if (item.category) {
          categoryStats[item.category] = (categoryStats[item.category] || 0) + 1
        }
      })
    }

    // 점수 분포
    const scoreDistribution = scoresData ? scoresData.map((item: any) => item.overall_score) : []

    const statistics = {
      totalCount: totalCount || 0,
      recentCount: recentCount || 0,
      avgScore,
      recommendationDist,
      categoryStats,
      scoreDistribution
    }

    return new Response(
      JSON.stringify({ success: true, data: statistics }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}

// 캠페인 분석 결과 조회
async function getCampaignAnalysis(supabaseClient: any, data: any) {
  try {
    const { campaign_id } = data

    if (!campaign_id) {
      return new Response(
        JSON.stringify({ success: false, error: 'campaign_id is required' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    const { data: analysisData, error } = await supabaseClient
      .from('campaign_analyses')
      .select('*')
      .eq('campaign_id', campaign_id)
      .single()

    if (error) {
      // 데이터가 없는 경우 (404)는 정상적인 경우일 수 있음
      if (error.code === 'PGRST116') {
        return new Response(
          JSON.stringify({ success: true, data: null }),
          { 
            status: 200, 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
          }
        )
      }
      throw error
    }

    return new Response(
      JSON.stringify({ success: true, data: analysisData }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}

// 캠페인 분석 결과 저장
async function saveCampaignAnalysis(supabaseClient: any, data: any) {
  try {
    const { campaign_id, analysis_result } = data

    if (!campaign_id || !analysis_result) {
      return new Response(
        JSON.stringify({ success: false, error: 'campaign_id and analysis_result are required' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // 기존 데이터 확인
    const { data: existingData, error: checkError } = await supabaseClient
      .from('campaign_analyses')
      .select('id')
      .eq('campaign_id', campaign_id)
      .single()

    // 데이터 준비
    const analysisData = {
      campaign_id,
      analysis_result,
      analyzed_at: new Date().toISOString()
    }

    let result
    if (existingData && !checkError) {
      // 업데이트 (campaign_id가 unique이므로 upsert 사용)
      const { data: updateData, error: updateError } = await supabaseClient
        .from('campaign_analyses')
        .update(analysisData)
        .eq('id', existingData.id)
        .select()
        .single()

      if (updateError) throw updateError
      result = updateData
    } else {
      // 새로 생성
      const { data: insertData, error: insertError } = await supabaseClient
        .from('campaign_analyses')
        .insert(analysisData)
        .select()
        .single()

      if (insertError) throw insertError
      result = insertData
    }

    return new Response(
      JSON.stringify({ success: true, data: result }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}
