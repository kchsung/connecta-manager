import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// ============================================================================
// 공통 유틸리티 함수들
// ============================================================================

// CORS 헤더 설정
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
}

// CORS 응답 생성
function createCorsResponse(status: number = 200, body?: any) {
  return new Response(
    body ? JSON.stringify(body) : null,
    {
      status,
      headers: corsHeaders,
    }
  )
}

// OPTIONS 요청 처리
function handleOptions() {
  return createCorsResponse(200)
}

// 인증 헤더에서 JWT 토큰 추출
function getAuthToken(request: Request): string | null {
  const authHeader = request.headers.get('Authorization')
  console.log('🔍 Authorization header:', authHeader ? 'Present' : 'Missing')
  
  if (!authHeader) {
    console.log('❌ No Authorization header found')
    return null
  }
  
  const token = authHeader.replace('Bearer ', '')
  console.log('🔑 Token extracted:', token ? `${token.substring(0, 20)}...` : 'Empty')
  return token
}

// 인증된 Supabase 클라이언트 생성
function createAuthenticatedClient(request: Request) {
  const supabaseUrl = Deno.env.get('SUPABASE_URL')!
  const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  
  const token = getAuthToken(request)
  
  const supabase = createClient(supabaseUrl, supabaseServiceKey, {
    global: {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    },
  })
  
  return supabase
}

// 사용자 인증 확인
async function verifyUser(request: Request) {
  const supabase = createAuthenticatedClient(request)
  
  try {
    const { data: { user }, error } = await supabase.auth.getUser()
    
    if (error || !user) {
      return { user: null, error: 'Unauthorized' }
    }
    
    return { user, error: null }
  } catch (error) {
    return { user: null, error: 'Authentication failed' }
  }
}

// ============================================================================
// 타입 정의
// ============================================================================

interface Campaign {
  id?: string
  campaign_name: string
  campaign_description?: string
  campaign_type: 'seeding' | 'promotion' | 'sales'
  start_date: string
  end_date?: string
  status: 'planned' | 'active' | 'paused' | 'completed' | 'cancelled'
  campaign_instructions?: string
  tags?: string
  created_by?: string
  created_at?: string
  updated_at?: string
}

interface Influencer {
  id?: string
  platform: 'instagram' | 'youtube' | 'tiktok' | 'twitter'
  content_category: string
  influencer_name?: string
  sns_id: string
  sns_url: string
  contact_method: 'dm' | 'email' | 'phone' | 'kakao'
  followers_count?: number
  phone_number?: string
  kakao_channel_id?: string
  email?: string
  shipping_address?: string
  interested_products?: string
  owner_comment?: string
  manager_rating?: number
  content_rating?: number
  comments_count?: number
  foreign_followers_ratio?: number
  activity_score?: number
  preferred_mode?: 'seeding' | 'promotion' | 'sales'
  price_krw?: number
  tags?: string
  created_by?: string
  created_at?: string
  updated_at?: string
  active?: boolean
  post_count?: number
  profile_text?: string
  profile_image_url?: string
  first_crawled?: boolean
}

interface CampaignParticipation {
  id?: string
  campaign_id: string
  influencer_id: string
  manager_comment?: string
  influencer_requests?: string
  memo?: string
  sample_status: '요청' | '발송' | '수령' | '완료' | '취소'
  influencer_feedback?: string
  content_uploaded?: boolean
  cost_krw?: number
  content_links?: string[]
  created_by?: string
  created_at?: string
  updated_at?: string
}

interface CampaignContent {
  id?: string
  participation_id: string
  content_url: string
  posted_at?: string
  caption?: string
  qualitative_note?: string
  likes?: number
  comments?: number
  is_rels?: number
  views?: number
  clicks?: number
  conversions?: number
  created_by?: string
  created_at?: string
  updated_at?: string
}

// ============================================================================
// 캠페인 관리 함수들
// ============================================================================

async function handleGetCampaigns(supabase: any, userId: string, campaignId?: string | null) {
  try {
    let query = supabase
      .from('campaigns')
      .select('*')
      .eq('created_by', userId)
      .order('created_at', { ascending: false })

    if (campaignId) {
      query = query.eq('id', campaignId)
    }

    const { data, error } = await query

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '데이터 조회 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(200, {
      success: true,
      data: campaignId ? (data[0] || null) : data,
      message: campaignId ? '캠페인을 조회했습니다.' : '캠페인 목록을 조회했습니다.'
    })
  } catch (error) {
    console.error('Get campaigns error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '캠페인 조회 중 오류가 발생했습니다.'
    })
  }
}

async function handleCreateCampaign(req: Request, supabase: any, userId: string) {
  try {
    const body = await req.json()
    const campaignData: Partial<Campaign> = {
      ...body,
      created_by: userId
    }

    if (!campaignData.campaign_name || !campaignData.campaign_type || !campaignData.start_date) {
      return createCorsResponse(400, {
        success: false,
        error: 'Missing required fields',
        message: '필수 필드가 누락되었습니다.'
      })
    }

    const { data, error } = await supabase
      .from('campaigns')
      .insert([campaignData])
      .select()
      .single()

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '캠페인 생성 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(201, {
      success: true,
      data,
      message: '캠페인이 성공적으로 생성되었습니다.'
    })
  } catch (error) {
    console.error('Create campaign error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '캠페인 생성 중 오류가 발생했습니다.'
    })
  }
}

async function handleUpdateCampaign(req: Request, supabase: any, userId: string, campaignId: string) {
  try {
    const body = await req.json()
    
    const { data: existingCampaign, error: checkError } = await supabase
      .from('campaigns')
      .select('id')
      .eq('id', campaignId)
      .eq('created_by', userId)
      .single()

    if (checkError || !existingCampaign) {
      return createCorsResponse(404, {
        success: false,
        error: 'Campaign not found',
        message: '캠페인을 찾을 수 없습니다.'
      })
    }

    console.log('🔍 Edge Function - 업데이트 데이터:', body)
    
    const { data, error } = await supabase
      .from('campaigns')
      .update({
        ...body,
        updated_at: new Date().toISOString()
      })
      .eq('id', campaignId)
      .eq('created_by', userId)
      .select()
      .single()

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '캠페인 업데이트 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(200, {
      success: true,
      data,
      message: '캠페인이 성공적으로 업데이트되었습니다.'
    })
  } catch (error) {
    console.error('Update campaign error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '캠페인 업데이트 중 오류가 발생했습니다.'
    })
  }
}

async function handleDeleteCampaign(supabase: any, userId: string, campaignId: string) {
  try {
    const { data: existingCampaign, error: checkError } = await supabase
      .from('campaigns')
      .select('id')
      .eq('id', campaignId)
      .eq('created_by', userId)
      .single()

    if (checkError || !existingCampaign) {
      return createCorsResponse(404, {
        success: false,
        error: 'Campaign not found',
        message: '캠페인을 찾을 수 없습니다.'
      })
    }

    const { error } = await supabase
      .from('campaigns')
      .delete()
      .eq('id', campaignId)
      .eq('created_by', userId)

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '캠페인 삭제 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(200, {
      success: true,
      message: '캠페인이 성공적으로 삭제되었습니다.'
    })
  } catch (error) {
    console.error('Delete campaign error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '캠페인 삭제 중 오류가 발생했습니다.'
    })
  }
}

// ============================================================================
// 인플루언서 관리 함수들
// ============================================================================

async function handleGetInfluencers(
  supabase: any, 
  userId: string, 
  influencerId?: string | null,
  platform?: string | null,
  search?: string | null
) {
  try {
    let query = supabase
      .from('connecta_influencers')
      .select('*')
      .order('created_at', { ascending: false })

    if (influencerId) {
      query = query.eq('id', influencerId)
    } else {
      if (platform) {
        query = query.eq('platform', platform)
      }
      if (search) {
        query = query.or(`influencer_name.ilike.%${search}%,sns_id.ilike.%${search}%`)
      }
    }

    const { data, error } = await query

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '데이터 조회 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(200, {
      success: true,
      data: influencerId ? (data[0] || null) : data,
      message: influencerId ? '인플루언서를 조회했습니다.' : '인플루언서 목록을 조회했습니다.'
    })
  } catch (error) {
    console.error('Get influencers error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '인플루언서 조회 중 오류가 발생했습니다.'
    })
  }
}

async function handleCreateInfluencer(req: Request, supabase: any, userId: string) {
  try {
    const body = await req.json()
    const influencerData: Partial<Influencer> = {
      ...body,
      created_by: userId
    }

    if (!influencerData.platform || !influencerData.sns_id || !influencerData.sns_url) {
      return createCorsResponse(400, {
        success: false,
        error: 'Missing required fields',
        message: '필수 필드가 누락되었습니다.'
      })
    }

    const { data: existingInfluencer } = await supabase
      .from('connecta_influencers')
      .select('id')
      .eq('platform', influencerData.platform)
      .eq('sns_id', influencerData.sns_id)
      .single()

    if (existingInfluencer) {
      return createCorsResponse(409, {
        success: false,
        error: 'Duplicate influencer',
        message: '이미 존재하는 인플루언서입니다.'
      })
    }

    const { data, error } = await supabase
      .from('connecta_influencers')
      .insert([influencerData])
      .select()
      .single()

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '인플루언서 생성 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(201, {
      success: true,
      data,
      message: '인플루언서가 성공적으로 생성되었습니다.'
    })
  } catch (error) {
    console.error('Create influencer error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '인플루언서 생성 중 오류가 발생했습니다.'
    })
  }
}

// ============================================================================
// 분석 및 통계 함수들
// ============================================================================

async function getOverviewStats(supabase: any, userId: string) {
  try {
    const { data: campaignStats } = await supabase
      .from('campaigns')
      .select('status')
      .eq('created_by', userId)

    const { data: influencerStats } = await supabase
      .from('connecta_influencers')
      .select('platform, followers_count')
      .eq('created_by', userId)

    const { data: participationStats } = await supabase
      .from('campaign_influencer_participations')
      .select(`
        sample_status,
        cost_krw,
        campaigns!inner(created_by)
      `)
      .eq('campaigns.created_by', userId)

    const { data: contentStats } = await supabase
      .from('campaign_influencer_contents')
      .select(`
        likes,
        comments,
        is_rels,
        views,
        clicks,
        conversions,
        campaign_influencer_participations!inner(
          campaigns!inner(created_by)
        )
      `)
      .eq('campaign_influencer_participations.campaigns.created_by', userId)

    const totalCampaigns = campaignStats?.length || 0
    const activeCampaigns = campaignStats?.filter(c => c.status === 'active').length || 0
    const totalInfluencers = influencerStats?.length || 0
    const totalFollowers = influencerStats?.reduce((sum, inf) => sum + (inf.followers_count || 0), 0) || 0
    const totalParticipations = participationStats?.length || 0
    const totalCost = participationStats?.reduce((sum, p) => sum + (p.cost_krw || 0), 0) || 0
    const totalLikes = contentStats?.reduce((sum, c) => sum + (c.likes || 0), 0) || 0
    const totalComments = contentStats?.reduce((sum, c) => sum + (c.comments || 0), 0) || 0
    const totalViews = contentStats?.reduce((sum, c) => sum + (c.views || 0), 0) || 0
    const totalConversions = contentStats?.reduce((sum, c) => sum + (c.conversions || 0), 0) || 0

    return createCorsResponse(200, {
      success: true,
      data: {
        campaigns: {
          total: totalCampaigns,
          active: activeCampaigns,
          completed: campaignStats?.filter(c => c.status === 'completed').length || 0
        },
        influencers: {
          total: totalInfluencers,
          totalFollowers: totalFollowers,
          averageFollowers: totalInfluencers > 0 ? Math.round(totalFollowers / totalInfluencers) : 0
        },
        participations: {
          total: totalParticipations,
          totalCost: totalCost,
          averageCost: totalParticipations > 0 ? Math.round(totalCost / totalParticipations) : 0
        },
        performance: {
          totalLikes: totalLikes,
          totalComments: totalComments,
          totalViews: totalViews,
          totalConversions: totalConversions,
          engagementRate: totalViews > 0 ? ((totalLikes + totalComments) / totalViews * 100).toFixed(2) : 0,
          conversionRate: totalViews > 0 ? (totalConversions / totalViews * 100).toFixed(2) : 0
        }
      },
      message: '전체 통계를 조회했습니다.'
    })
  } catch (error) {
    console.error('Get overview stats error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '전체 통계 조회 중 오류가 발생했습니다.'
    })
  }
}

// ============================================================================
// 캠페인 참여 관련 핸들러 함수들
// ============================================================================

// 캠페인 참여 목록 조회
async function handleGetParticipations(
  supabase: any, 
  userId: string, 
  participationId?: string | null,
  campaignId?: string | null
) {
  try {
    console.log('🔍 참여 조회 파라미터:', {
      userId,
      participationId,
      campaignId
    })
    
    let query = supabase
      .from('campaign_influencer_participations')
      .select(`
        *,
        campaigns!inner(id, campaign_name, created_by),
        connecta_influencers!inner(id, influencer_name, sns_id, platform, followers_count)
      `)
      .eq('campaigns.created_by', userId)
      .order('created_at', { ascending: false })

    // 특정 참여 조회
    if (participationId) {
      query = query.eq('id', participationId)
    }
    
    // 특정 캠페인의 참여자들 조회
    if (campaignId) {
      query = query.eq('campaign_id', campaignId)
    }

    const { data, error } = await query

    console.log('🔍 쿼리 결과:', {
      dataCount: data?.length || 0,
      error: error?.message || null,
      data: data?.slice(0, 2) || [] // 처음 2개만 로그
    })

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '데이터 조회 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(200, {
      success: true,
      data: participationId ? (data[0] || null) : data,
      message: participationId ? '참여 정보를 조회했습니다.' : '참여 목록을 조회했습니다.'
    })
  } catch (error) {
    console.error('Get participations error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '참여 정보 조회 중 오류가 발생했습니다.'
    })
  }
}

// 캠페인 참여 생성
async function handleCreateParticipation(req: Request, supabase: any, userId: string) {
  try {
    const body = await req.json()
    const participationData: Partial<CampaignParticipation> = {
      ...body,
      created_by: userId
    }

    // 필수 필드 검증
    if (!participationData.campaign_id || !participationData.influencer_id) {
      return createCorsResponse(400, {
        success: false,
        error: 'Missing required fields',
        message: '필수 필드가 누락되었습니다.'
      })
    }

    // 캠페인이 사용자의 것인지 확인
    const { data: campaign, error: campaignError } = await supabase
      .from('campaigns')
      .select('id')
      .eq('id', participationData.campaign_id)
      .eq('created_by', userId)
      .single()

    if (campaignError || !campaign) {
      return createCorsResponse(404, {
        success: false,
        error: 'Campaign not found',
        message: '캠페인을 찾을 수 없습니다.'
      })
    }

    // 중복 참여 체크
    const { data: existingParticipation } = await supabase
      .from('campaign_influencer_participations')
      .select('id')
      .eq('campaign_id', participationData.campaign_id)
      .eq('influencer_id', participationData.influencer_id)
      .single()

    if (existingParticipation) {
      return createCorsResponse(409, {
        success: false,
        error: 'Duplicate participation',
        message: '이미 참여 중인 인플루언서입니다.'
      })
    }

    const { data, error } = await supabase
      .from('campaign_influencer_participations')
      .insert([participationData])
      .select(`
        *,
        campaigns(id, campaign_name),
        connecta_influencers(id, influencer_name, sns_id, platform, followers_count)
      `)
      .single()

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '참여 생성 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(201, {
      success: true,
      data,
      message: '인플루언서가 캠페인에 성공적으로 추가되었습니다.'
    })
  } catch (error) {
    console.error('Create participation error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '참여 생성 중 오류가 발생했습니다.'
    })
  }
}

// 캠페인 참여 업데이트
async function handleUpdateParticipation(req: Request, supabase: any, userId: string, participationId: string) {
  try {
    const body = await req.json()
    
    // 먼저 참여가 사용자의 캠페인인지 확인
    const { data: existingParticipation, error: checkError } = await supabase
      .from('campaign_influencer_participations')
      .select(`
        id,
        campaigns!inner(id, created_by)
      `)
      .eq('id', participationId)
      .eq('campaigns.created_by', userId)
      .single()

    if (checkError || !existingParticipation) {
      return createCorsResponse(404, {
        success: false,
        error: 'Participation not found',
        message: '참여 정보를 찾을 수 없습니다.'
      })
    }

    const { data, error } = await supabase
      .from('campaign_influencer_participations')
      .update({
        ...body,
        updated_at: new Date().toISOString()
      })
      .eq('id', participationId)
      .select(`
        *,
        campaigns(id, campaign_name),
        connecta_influencers(id, influencer_name, sns_id, platform, followers_count)
      `)
      .single()

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '참여 정보 업데이트 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(200, {
      success: true,
      data,
      message: '참여 정보가 성공적으로 업데이트되었습니다.'
    })
  } catch (error) {
    console.error('Update participation error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '참여 정보 업데이트 중 오류가 발생했습니다.'
    })
  }
}

// 캠페인 참여 삭제
async function handleDeleteParticipation(supabase: any, userId: string, participationId: string) {
  try {
    // 먼저 참여가 사용자의 캠페인인지 확인
    const { data: existingParticipation, error: checkError } = await supabase
      .from('campaign_influencer_participations')
      .select(`
        id,
        campaigns!inner(id, created_by)
      `)
      .eq('id', participationId)
      .eq('campaigns.created_by', userId)
      .single()

    if (checkError || !existingParticipation) {
      return createCorsResponse(404, {
        success: false,
        error: 'Participation not found',
        message: '참여 정보를 찾을 수 없습니다.'
      })
    }

    const { error } = await supabase
      .from('campaign_influencer_participations')
      .delete()
      .eq('id', participationId)

    if (error) {
      console.error('Database error:', error)
      return createCorsResponse(500, {
        success: false,
        error: 'Database error',
        message: '참여 삭제 중 오류가 발생했습니다.'
      })
    }

    return createCorsResponse(200, {
      success: true,
      message: '참여가 성공적으로 삭제되었습니다.'
    })
  } catch (error) {
    console.error('Delete participation error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '참여 삭제 중 오류가 발생했습니다.'
    })
  }
}

// ============================================================================
// 메인 Edge Function
// ============================================================================

serve(async (req) => {
  // CORS 처리
  if (req.method === 'OPTIONS') {
    return handleOptions()
  }

  try {
    // 인증 확인
    const { user, error: authError } = await verifyUser(req)
    if (authError || !user) {
      return createCorsResponse(401, {
        success: false,
        error: 'Unauthorized',
        message: '로그인이 필요합니다.'
      })
    }

    const supabase = createAuthenticatedClient(req)
    const url = new URL(req.url)
    const path = url.pathname.split('/').pop() || ''
    const action = url.searchParams.get('action') || 'list'
    const id = url.searchParams.get('id')
    const platform = url.searchParams.get('platform')
    const search = url.searchParams.get('search')
    const type = url.searchParams.get('type') || 'overview'
    
    console.log('🔍 API 요청 정보:', {
      path,
      action,
      method: req.method,
      id,
      campaign_id: url.searchParams.get('campaign_id'),
      userId: user.id
    })

    // 라우팅 처리
    switch (action) {
      case 'campaigns':
        switch (req.method) {
          case 'GET':
            return await handleGetCampaigns(supabase, user.id, id)
          case 'POST':
            return await handleCreateCampaign(req, supabase, user.id)
          case 'PUT':
            if (!id) {
              return createCorsResponse(400, {
                success: false,
                error: 'Missing campaign ID',
                message: '캠페인 ID가 필요합니다.'
              })
            }
            return await handleUpdateCampaign(req, supabase, user.id, id)
          case 'DELETE':
            if (!id) {
              return createCorsResponse(400, {
                success: false,
                error: 'Missing campaign ID',
                message: '캠페인 ID가 필요합니다.'
              })
            }
            return await handleDeleteCampaign(supabase, user.id, id)
          default:
            return createCorsResponse(405, {
              success: false,
              error: 'Method not allowed',
              message: '지원하지 않는 HTTP 메서드입니다.'
            })
        }

      case 'influencers':
        switch (req.method) {
          case 'GET':
            return await handleGetInfluencers(supabase, user.id, id, platform, search)
          case 'POST':
            return await handleCreateInfluencer(req, supabase, user.id)
          default:
            return createCorsResponse(405, {
              success: false,
              error: 'Method not allowed',
              message: '지원하지 않는 HTTP 메서드입니다.'
            })
        }

      case 'analytics':
        if (req.method === 'GET') {
          if (type === 'overview') {
            return await getOverviewStats(supabase, user.id)
          }
        }
        return createCorsResponse(405, {
          success: false,
          error: 'Method not allowed',
          message: '지원하지 않는 HTTP 메서드입니다.'
        })

      case 'campaign-participations':
        switch (req.method) {
          case 'GET':
            return await handleGetParticipations(supabase, user.id, id, url.searchParams.get('campaign_id'))
          case 'POST':
            return await handleCreateParticipation(req, supabase, user.id)
          case 'PUT':
            if (!id) {
              return createCorsResponse(400, {
                success: false,
                error: 'Missing participation ID',
                message: '참여 ID가 필요합니다.'
              })
            }
            return await handleUpdateParticipation(req, supabase, user.id, id)
          case 'DELETE':
            if (!id) {
              return createCorsResponse(400, {
                success: false,
                error: 'Missing participation ID',
                message: '참여 ID가 필요합니다.'
              })
            }
            return await handleDeleteParticipation(supabase, user.id, id)
          default:
            return createCorsResponse(405, {
              success: false,
              error: 'Method not allowed',
              message: '지원하지 않는 HTTP 메서드입니다.'
            })
        }

      default:
        return createCorsResponse(404, {
          success: false,
          error: 'Not found',
          message: '요청한 엔드포인트를 찾을 수 없습니다.'
        })
    }
  } catch (error) {
    console.error('API function error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '서버 오류가 발생했습니다.'
    })
  }
})
