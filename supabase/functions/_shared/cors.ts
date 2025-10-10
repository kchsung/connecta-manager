// CORS 헤더 설정
export const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
}

// CORS 응답 생성
export function createCorsResponse(status: number = 200, body?: any) {
  return new Response(
    body ? JSON.stringify(body) : null,
    {
      status,
      headers: corsHeaders,
    }
  )
}

// OPTIONS 요청 처리
export function handleOptions() {
  return createCorsResponse(200)
}

