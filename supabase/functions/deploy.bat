@echo off
REM Supabase Edge Functions 배포 스크립트 (Windows)

echo 🚀 Supabase Edge Functions 배포 시작...

REM Supabase CLI가 설치되어 있는지 확인
supabase --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Supabase CLI가 설치되지 않았습니다.
    echo 다음 명령어로 설치하세요: npm install -g supabase
    pause
    exit /b 1
)

REM 로그인 상태 확인
supabase status >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Supabase에 로그인되지 않았습니다.
    echo 다음 명령어로 로그인하세요: supabase login
    pause
    exit /b 1
)

echo ✅ Supabase CLI 설정 확인 완료

REM 함수 배포
echo 📦 함수 배포 중...

REM 캠페인 관리 함수
echo   - 캠페인 관리 함수 배포 중...
supabase functions deploy campaigns

REM 인플루언서 관리 함수
echo   - 인플루언서 관리 함수 배포 중...
supabase functions deploy influencers

REM 캠페인 참여 관리 함수
echo   - 캠페인 참여 관리 함수 배포 중...
supabase functions deploy campaign-participations

REM 캠페인 콘텐츠 관리 함수
echo   - 캠페인 콘텐츠 관리 함수 배포 중...
supabase functions deploy campaign-contents

REM 분석 및 통계 함수
echo   - 분석 및 통계 함수 배포 중...
supabase functions deploy analytics

echo ✅ 모든 함수 배포 완료!

REM 배포된 함수 목록 확인
echo 📋 배포된 함수 목록:
supabase functions list

echo.
echo 🎉 배포가 완료되었습니다!
echo.
echo 사용 방법:
echo 1. Supabase 대시보드에서 Functions 탭 확인
echo 2. 각 함수의 URL을 확인하여 API 호출
echo 3. 인증 토큰을 헤더에 포함하여 요청
echo.
echo 예시:
echo curl -X GET "https://YOUR_PROJECT_REF.supabase.co/functions/v1/campaigns" ^
echo   -H "Authorization: Bearer YOUR_JWT_TOKEN"

pause

