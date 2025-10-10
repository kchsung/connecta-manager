#!/bin/bash

# Supabase Edge Functions 배포 스크립트

echo "🚀 Supabase Edge Functions 배포 시작..."

# Supabase CLI가 설치되어 있는지 확인
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI가 설치되지 않았습니다."
    echo "다음 명령어로 설치하세요: npm install -g supabase"
    exit 1
fi

# 로그인 상태 확인
if ! supabase status &> /dev/null; then
    echo "❌ Supabase에 로그인되지 않았습니다."
    echo "다음 명령어로 로그인하세요: supabase login"
    exit 1
fi

# 프로젝트 연결 확인
if ! supabase projects list &> /dev/null; then
    echo "❌ Supabase 프로젝트에 연결되지 않았습니다."
    echo "다음 명령어로 프로젝트를 연결하세요: supabase link --project-ref YOUR_PROJECT_REF"
    exit 1
fi

echo "✅ Supabase CLI 설정 확인 완료"

# 함수 배포
echo "📦 함수 배포 중..."

# 공통 유틸리티 함수들
echo "  - 공통 유틸리티 함수 배포 중..."
# _shared 폴더는 별도 배포하지 않음 (다른 함수에서 import됨)

# 캠페인 관리 함수
echo "  - 캠페인 관리 함수 배포 중..."
supabase functions deploy campaigns

# 인플루언서 관리 함수
echo "  - 인플루언서 관리 함수 배포 중..."
supabase functions deploy influencers

# 캠페인 참여 관리 함수
echo "  - 캠페인 참여 관리 함수 배포 중..."
supabase functions deploy campaign-participations

# 캠페인 콘텐츠 관리 함수
echo "  - 캠페인 콘텐츠 관리 함수 배포 중..."
supabase functions deploy campaign-contents

# 분석 및 통계 함수
echo "  - 분석 및 통계 함수 배포 중..."
supabase functions deploy analytics

echo "✅ 모든 함수 배포 완료!"

# 배포된 함수 목록 확인
echo "📋 배포된 함수 목록:"
supabase functions list

echo ""
echo "🎉 배포가 완료되었습니다!"
echo ""
echo "사용 방법:"
echo "1. Supabase 대시보드에서 Functions 탭 확인"
echo "2. 각 함수의 URL을 확인하여 API 호출"
echo "3. 인증 토큰을 헤더에 포함하여 요청"
echo ""
echo "예시:"
echo "curl -X GET 'https://YOUR_PROJECT_REF.supabase.co/functions/v1/campaigns' \\"
echo "  -H 'Authorization: Bearer YOUR_JWT_TOKEN'"

