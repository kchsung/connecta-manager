# Supabase Edge Functions 수동 배포 가이드

CLI 설치에 문제가 있을 때 Supabase 대시보드에서 직접 배포하는 방법입니다.

## 1. Supabase 대시보드 접속

1. [Supabase 대시보드](https://supabase.com/dashboard)에 로그인
2. 프로젝트 선택
3. **Edge Functions** 탭으로 이동

## 2. 함수 생성 및 배포

### 캠페인 관리 함수 (`campaigns`)

1. **"Create a new function"** 클릭
2. 함수 이름: `campaigns`
3. **"Create function"** 클릭
4. 다음 코드를 복사해서 붙여넣기:

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

// CORS 헤더 설정
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
}

function createCorsResponse(status: number = 200, body?: any) {
  return new Response(
    body ? JSON.stringify(body) : null,
    {
      status,
      headers: corsHeaders,
    }
  )
}

function handleOptions() {
  return createCorsResponse(200)
}

// 인증 헤더에서 JWT 토큰 추출
function getAuthToken(request: Request): string | null {
  const authHeader = request.headers.get('Authorization')
  if (!authHeader) return null
  const token = authHeader.replace('Bearer ', '')
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

// 캠페인 관리 Edge Function
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
    const campaignId = url.searchParams.get('id')

    switch (req.method) {
      case 'GET':
        return await handleGetCampaigns(supabase, user.id, campaignId)
      
      case 'POST':
        return await handleCreateCampaign(req, supabase, user.id)
      
      case 'PUT':
        if (!campaignId) {
          return createCorsResponse(400, {
            success: false,
            error: 'Missing campaign ID',
            message: '캠페인 ID가 필요합니다.'
          })
        }
        return await handleUpdateCampaign(req, supabase, user.id, campaignId)
      
      case 'DELETE':
        if (!campaignId) {
          return createCorsResponse(400, {
            success: false,
            error: 'Missing campaign ID',
            message: '캠페인 ID가 필요합니다.'
          })
        }
        return await handleDeleteCampaign(supabase, user.id, campaignId)
      
      default:
        return createCorsResponse(405, {
          success: false,
          error: 'Method not allowed',
          message: '지원하지 않는 HTTP 메서드입니다.'
        })
    }
  } catch (error) {
    console.error('Campaign function error:', error)
    return createCorsResponse(500, {
      success: false,
      error: 'Internal server error',
      message: '서버 오류가 발생했습니다.'
    })
  }
})

// 캠페인 목록 조회
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

// 캠페인 생성
async function handleCreateCampaign(req: Request, supabase: any, userId: string) {
  try {
    const body = await req.json()
    const campaignData = {
      ...body,
      created_by: userId
    }

    // 필수 필드 검증
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

// 캠페인 업데이트
async function handleUpdateCampaign(req: Request, supabase: any, userId: string, campaignId: string) {
  try {
    const body = await req.json()
    
    // 먼저 캠페인이 사용자의 것인지 확인
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

// 캠페인 삭제
async function handleDeleteCampaign(supabase: any, userId: string, campaignId: string) {
  try {
    // 먼저 캠페인이 사용자의 것인지 확인
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
```

5. **"Deploy"** 클릭

## 3. 다른 함수들도 동일한 방식으로 생성

- `influencers` 함수
- `campaign-participations` 함수  
- `campaign-contents` 함수
- `analytics` 함수

각각에 대해 위와 동일한 과정을 반복하되, 해당 함수의 코드를 사용하세요.

## 4. 테스트

함수 배포 후 다음과 같이 테스트할 수 있습니다:

```javascript
// 함수 URL 형식
https://YOUR_PROJECT_REF.supabase.co/functions/v1/FUNCTION_NAME

// 예시
const response = await fetch('https://YOUR_PROJECT_REF.supabase.co/functions/v1/campaigns', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
});
```

## 5. 주의사항

1. **RLS 정책 먼저 설정**: `rls_policies.sql`을 Supabase SQL Editor에서 실행
2. **인증 토큰 필요**: 모든 API 호출에 JWT 토큰 포함
3. **환경 변수**: Supabase에서 자동으로 설정됨

