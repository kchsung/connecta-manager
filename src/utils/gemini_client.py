"""
Gemini API 클라이언트 유틸리티
"""
import streamlit as st
import os
import json
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def get_gemini_client():
    """Gemini API 클라이언트 반환"""
    if not GEMINI_AVAILABLE:
        st.error("google-generativeai 패키지가 설치되지 않았습니다. pip install google-generativeai를 실행해주세요.")
        return None
    
    # API 키 읽기 (환경변수 우선, 그 다음 secrets)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            # secrets에서 직접 읽기 시도
            if hasattr(st, 'secrets') and st.secrets:
                api_key = st.secrets.get("GEMINI_API_KEY")
                # 만약 None이면 문자열로 시도 (TOML 형식에 따라)
                if api_key is None:
                    try:
                        api_key = st.secrets["GEMINI_API_KEY"]
                    except (KeyError, TypeError):
                        pass
        except (KeyError, AttributeError, TypeError) as e:
            api_key = None
    
    # 키 검증
    if not api_key:
        st.error("Gemini API 키가 설정되지 않았습니다.")
        st.info("💡 `.streamlit/secrets.toml` 파일에 `GEMINI_API_KEY = \"your-api-key\"` 형식으로 추가해주세요.")
        return None
    
    # 키가 문자열인지 확인하고 공백 제거
    if isinstance(api_key, str):
        api_key = api_key.strip()
    
    if not api_key or api_key == "your-gemini-api-key-here" or len(api_key) < 10:
        st.error("Gemini API 키가 유효하지 않습니다.")
        return None
    
    try:
        genai.configure(api_key=api_key)
        return genai
    except Exception as e:
        st.error(f"Gemini API 클라이언트 초기화 실패: {e}")
        return None


def get_available_models():
    """사용 가능한 Gemini 모델 목록 조회"""
    try:
        client = get_gemini_client()
        if not client:
            return []
        
        models = genai.list_models()
        available = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available.append(model.name.replace('models/', ''))
        return available
    except Exception as e:
        # 모델 목록 조회 실패 시 기본 모델 반환
        return ["gemini-pro"]


def normalize_category(category: str) -> str:
    """카테고리를 표준 카테고리로 정규화"""
    if not category:
        return "일반"
    
    # 표준 카테고리 목록
    standard_categories = [
        "일반", "뷰티", "패션", "푸드", "여행", 
        "라이프스타일", "테크", "게임", "스포츠", "애견", "기타"
    ]
    
    category_lower = category.lower().strip()
    
    # 정확히 일치하는 경우
    for std_cat in standard_categories:
        if category_lower == std_cat.lower():
            return std_cat
    
    # "/"로 구분된 경우 (예: "스포츠/러닝" → "스포츠/라이프스타일")
    if "/" in category:
        parts = [p.strip() for p in category.split("/")]
        normalized_parts = []
        
        for part in parts:
            part_lower = part.lower()
            # 각 부분을 표준 카테고리로 매핑
            matched = False
            for std_cat in standard_categories:
                if part_lower == std_cat.lower() or part_lower in std_cat.lower() or std_cat.lower() in part_lower:
                    normalized_parts.append(std_cat)
                    matched = True
                    break
            
            if not matched:
                # 매핑되지 않으면 원본 유지
                normalized_parts.append(part)
        
        return "/".join(normalized_parts)
    
    # 부분 일치로 매핑 시도
    for std_cat in standard_categories:
        std_cat_lower = std_cat.lower()
        if category_lower in std_cat_lower or std_cat_lower in category_lower:
            return std_cat
    
    # 매핑 실패 시 원본 반환 (필터링에서 처리)
    return category


def get_valid_model_name(requested_model: str = None) -> str:
    """유효한 모델명 반환 (사용 가능한 모델 중에서 선택)"""
    # 기본 모델 목록 (우선순위 순)
    default_models = [
        "gemini-pro",  # 가장 안정적
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ]
    
    # 사용 가능한 모델 조회 시도
    try:
        available = get_available_models()
        if available:
            # 요청된 모델이 사용 가능한지 확인
            if requested_model and requested_model in available:
                return requested_model
            
            # 기본 모델 중 사용 가능한 첫 번째 모델 반환
            for model in default_models:
                if model in available:
                    return model
            
            # 사용 가능한 모델 중 첫 번째 반환
            return available[0]
    except:
        pass
    
    # 모델 목록 조회 실패 시 기본값 반환
    return requested_model or default_models[0]


def get_openai_client():
    """OpenAI API 클라이언트 반환"""
    if not OPENAI_AVAILABLE:
        st.error("openai 패키지가 설치되지 않았습니다. pip install openai를 실행해주세요.")
        return None
    
    # API 키 읽기 (환경변수 우선, 그 다음 secrets)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            # secrets에서 직접 읽기 시도
            if hasattr(st, 'secrets') and st.secrets:
                api_key = st.secrets.get("OPENAI_API_KEY")
                # 만약 None이면 문자열로 시도 (TOML 형식에 따라)
                if api_key is None:
                    try:
                        api_key = st.secrets["OPENAI_API_KEY"]
                    except (KeyError, TypeError):
                        pass
        except (KeyError, AttributeError, TypeError) as e:
            api_key = None
    
    # 키 검증
    if not api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다.")
        st.info("💡 `.streamlit/secrets.toml` 파일에 `OPENAI_API_KEY = \"your-api-key\"` 형식으로 추가해주세요.")
        return None
    
    # 키가 문자열인지 확인하고 공백 제거
    if isinstance(api_key, str):
        api_key = api_key.strip()
    
    if not api_key or api_key == "your-openai-api-key-here" or len(api_key) < 10:
        st.error("OpenAI API 키가 유효하지 않습니다.")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"OpenAI API 클라이언트 초기화 실패: {e}")
        return None


def analyze_campaign_with_gemini(campaign_content: str) -> Optional[Dict[str, Any]]:
    """
    캠페인 내용을 OpenAI 프롬프트 ID를 사용하여 분석
    
    Args:
        campaign_content: 캠페인 내용 (campaigns 테이블의 정보)
    
    Returns:
        분석 결과 딕셔너리 (category, recommended_tags, details)
    """
    client = get_openai_client()
    if not client:
        return None
    
    try:
        # OpenAI 프롬프트 ID를 사용하여 응답 생성
        # campaign_content를 input 파라미터로 전달
        response = client.responses.create(
            prompt={
                "id": "pmpt_691993b8a8688190bc1546a32d5a194a074f9cef6a509528"
            },
            input=campaign_content
        )
        
        # 응답 텍스트 추출 (OpenAI responses API 표준 방식)
        response_text = None
        
        # 방법 1: output_text 속성 확인
        if hasattr(response, 'output_text') and response.output_text:
            response_text = response.output_text
        # 방법 2: output 배열에서 content[*].text 추출
        elif hasattr(response, 'output') and response.output:
            chunks = []
            for block in response.output:
                if hasattr(block, 'content') and block.content:
                    for c in block.content:
                        if hasattr(c, 'text') and c.text:
                            chunks.append(c.text)
            if chunks:
                response_text = "\n".join(chunks)
        
        if not response_text:
            st.error("응답에서 텍스트를 찾지 못했습니다.")
            return None
        
        # 문자열로 변환 및 공백 제거
        response_text = str(response_text).strip()
        
        # JSON 형식 추출 (여러 방법 시도)
        json_text = None
        
        # 방법 1: ```json 코드 블록에서 추출
        if "```json" in response_text:
            parts = response_text.split("```json")
            if len(parts) > 1:
                json_text = parts[1].split("```")[0].strip()
        
        # 방법 2: 일반 ``` 코드 블록에서 추출
        if not json_text and "```" in response_text:
            parts = response_text.split("```")
            if len(parts) > 1:
                json_text = parts[1].split("```")[0].strip()
        
        # 방법 3: { 로 시작하는 부분 찾기
        if not json_text:
            start_idx = response_text.find("{")
            if start_idx >= 0:
                # 마지막 } 찾기
                end_idx = response_text.rfind("}")
                if end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx+1].strip()
        
        # 방법 4: 전체 텍스트를 JSON으로 시도
        if not json_text:
            json_text = response_text
        
        # JSON 파싱 시도
        result = None
        try:
            result = json.loads(json_text)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시, 정규표현식으로 JSON 부분만 추출 시도
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', json_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                except:
                    pass
        
        if not result:
            # JSON 파싱 실패 시, 텍스트에서 정보 추출 시도
            st.warning("⚠️ JSON 형식으로 파싱할 수 없어 텍스트에서 정보를 추출합니다.")
            
            # 카테고리 추출 시도
            category = ""
            if "category" in response_text.lower() or "카테고리" in response_text:
                category_match = re.search(r'(?:category|카테고리)[\s:：]*["\']?([^"\'\n]+)["\']?', response_text, re.IGNORECASE)
                if category_match:
                    category = category_match.group(1).strip()
            
            # 태그 추출 시도
            recommended_tags = []
            if "tag" in response_text.lower() or "태그" in response_text:
                tags_match = re.search(r'(?:tags|태그|recommended_tags)[\s:：]*\[([^\]]+)\]', response_text, re.IGNORECASE)
                if tags_match:
                    tags_str = tags_match.group(1)
                    recommended_tags = [tag.strip().strip('"\'') for tag in tags_str.split(",")]
            
            return {
                "category": category or "일반",
                "recommended_tags": recommended_tags if recommended_tags else [],
                "details": response_text
            }
        
        # 정상적으로 파싱된 경우
        # 새로운 형식인지 확인 (campaign_summary가 있으면 새로운 형식)
        if 'campaign_summary' in result:
            # 새로운 형식: 그대로 반환
            # ideal_influencer_profile의 recommended_category 정규화
            if 'ideal_influencer_profile' in result:
                profile = result['ideal_influencer_profile']
                if 'recommended_category' in profile:
                    profile['recommended_category'] = normalize_category(profile['recommended_category'])
            return result
        else:
            # 기존 형식: 카테고리 정규화 후 반환
            category = result.get("category", "").strip()
            normalized_category = normalize_category(category)
            
            return {
                "category": normalized_category,
                "recommended_tags": result.get("recommended_tags", []),
                "details": result.get("details", "")
            }
    
    except json.JSONDecodeError as e:
        st.error(f"OpenAI API 응답 파싱 실패: {e}")
        return None
    except Exception as e:
        st.error(f"캠페인 분석 중 오류 발생: {e}")
        return None


def generate_proposal_with_openai(
    campaign_analysis_result: Dict[str, Any],
    influencer_analysis: Dict[str, Any]
) -> Optional[str]:
    """
    인플루언서별 캠페인 제안서 작성 (OpenAI 사용)
    
    Args:
        campaign_analysis_result: 캠페인 분석 결과 (campaign_analyses 테이블의 analysis_result)
        influencer_analysis: 인플루언서 분석 결과 (ai_influencer_analyses 테이블)
    
    Returns:
        마크다운 형태의 제안서
    """
    client = get_openai_client()
    if not client:
        return None
    
    try:
        # 입력 데이터 구성
        input_data = {
            "campaign_analysis": campaign_analysis_result,
            "influencer_analysis": influencer_analysis
        }
        
        # JSON 문자열로 변환
        input_text = json.dumps(input_data, ensure_ascii=False, indent=2)
        
        # OpenAI 프롬프트 ID를 사용하여 응답 생성
        response = client.responses.create(
            prompt={
                "id": "pmpt_6919ca4d95208190be84e9d60f0c8d810aab57b07dffc4a3"
            },
            input=input_text
        )
        
        # 응답 텍스트 추출 (OpenAI responses API 표준 방식)
        response_text = None
        
        # 방법 1: output_text 속성 확인
        if hasattr(response, 'output_text') and response.output_text:
            response_text = response.output_text
        # 방법 2: output 배열에서 content[*].text 추출
        elif hasattr(response, 'output') and response.output:
            chunks = []
            for block in response.output:
                if hasattr(block, 'content') and block.content:
                    for c in block.content:
                        if hasattr(c, 'text') and c.text:
                            chunks.append(c.text)
            if chunks:
                response_text = "\n".join(chunks)
        
        if not response_text:
            st.error("응답에서 텍스트를 찾지 못했습니다.")
            return None
        
        # 문자열로 변환 및 공백 제거
        return str(response_text).strip()
    
    except Exception as e:
        st.error(f"제안서 생성 중 오류 발생: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None


def generate_proposal_with_gemini(
    campaign_info: Dict[str, Any],
    influencer_analysis: Dict[str, Any]
) -> Optional[str]:
    """
    인플루언서별 캠페인 제안서 작성 (Gemini 사용 - 하위 호환성)
    
    Args:
        campaign_info: 캠페인 정보 (campaigns 테이블)
        influencer_analysis: 인플루언서 분석 결과 (ai_influencer_analyses 테이블)
    
    Returns:
        마크다운 형태의 제안서
    """
    client = get_gemini_client()
    if not client:
        return None
    
    prompt = """너는 인플루언서 마케팅 전문가야

주어진 인플루언서 분석 정보와 캠페인 정보를 활용해서 인플루언서에 맞는 제안서를 작성해줘

캠페인 정보:
{campaign_info}

인플루언서 분석 정보:
{influencer_analysis}

마크다운 형식으로 제안서를 작성해주세요. 다음 내용을 포함해주세요:
- 인플루언서 소개
- 캠페인과의 적합성
- 추천 콘텐츠 제안
- 예상 성과
"""
    
    try:
        # 캠페인 정보를 JSON 문자열로 변환
        campaign_json = json.dumps(campaign_info, ensure_ascii=False, indent=2)
        # 인플루언서 분석 정보를 JSON 문자열로 변환
        influencer_json = json.dumps(influencer_analysis, ensure_ascii=False, indent=2)
        
        # 모델명 설정 (secrets에서 가져오거나 기본값 사용)
        requested_model = st.secrets.get("GEMINI_MODEL", None)
        model_name = get_valid_model_name(requested_model)
        
        if requested_model and requested_model != model_name:
            st.info(f"ℹ️ 요청한 모델 '{requested_model}' 대신 사용 가능한 모델 '{model_name}'을 사용합니다.")
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt.format(
                campaign_info=campaign_json,
                influencer_analysis=influencer_json
            ),
            generation_config=genai.types.GenerationConfig(
                temperature=0.5
            )
        )
        
        return response.text.strip()
    
    except Exception as e:
        st.error(f"제안서 생성 중 오류 발생: {e}")
        return None

