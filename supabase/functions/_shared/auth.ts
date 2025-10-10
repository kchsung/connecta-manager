import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// 인증 헤더에서 JWT 토큰 추출
export function getAuthToken(request: Request): string | null {
  const authHeader = request.headers.get('Authorization')
  if (!authHeader) return null
  
  const token = authHeader.replace('Bearer ', '')
  return token
}

// 인증된 Supabase 클라이언트 생성
export function createAuthenticatedClient(request: Request) {
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
export async function verifyUser(request: Request) {
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

// RLS를 위한 사용자 ID 반환
export async function getUserId(request: Request): Promise<string | null> {
  const { user } = await verifyUser(request)
  return user?.id || null
}

