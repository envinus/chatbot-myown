# requirements.txt
# streamlit
# openai
# pillow
# requests

import streamlit as st
from openai import OpenAI
import time
import os
from PIL import Image
import base64
from io import BytesIO
import requests
import urllib.parse

# 페이지 설정
st.set_page_config(
    page_title="어린이 건강 챗봇",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 블루 계통 머터리얼 디자인 컬러 팔레트
MATERIAL_COLORS = {
    "primary": "#1976D2",
    "primary_variant": "#1565C0",
    "secondary": "#0288D1",
    "background": "#E3F2FD",
    "surface": "#FFFFFF",
    "surface_variant": "#F3F8FF",
    "on_primary": "#FFFFFF",
    "on_secondary": "#FFFFFF",
    "on_surface": "#0D47A1",
    "outline": "#90CAF9",
    "error": "#C62828"
}

# CSS 스타일 적용 (기존과 동일)
def apply_custom_css():
    st.markdown(f"""
    <style>
        :root {{
            --primary: {MATERIAL_COLORS['primary']};
            --primary-variant: {MATERIAL_COLORS['primary_variant']};
            --secondary: {MATERIAL_COLORS['secondary']};
            --background: {MATERIAL_COLORS['background']};
            --surface: {MATERIAL_COLORS['surface']};
            --surface-variant: {MATERIAL_COLORS['surface_variant']};
            --on-primary: {MATERIAL_COLORS['on_primary']};
            --on-secondary: {MATERIAL_COLORS['on_secondary']};
            --on-surface: {MATERIAL_COLORS['on_surface']};
            --outline: {MATERIAL_COLORS['outline']};
            --error: {MATERIAL_COLORS['error']};
        }}
        
        .stApp {{
            background-color: var(--background);
            color: var(--on-surface);
        }}
        
        .stApp, .stApp p, .stApp div, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
            color: var(--on-surface) !important;
        }}
        
        .css-1d391kg {{
            background-color: var(--surface-variant);
        }}
        
        .stButton>button {{
            background-color: var(--primary);
            color: var(--on-primary);
            border-radius: 8px;
            border: none;
            padding: 12px 24px;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(25, 118, 210, 0.2);
        }}
        
        .stButton>button:hover {{
            background-color: var(--primary-variant);
            box-shadow: 0 4px 8px rgba(25, 118, 210, 0.3);
            transform: translateY(-1px);
        }}
        
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
            background-color: var(--surface);
            border: 2px solid var(--outline);
            border-radius: 8px;
            color: var(--on-surface);
            padding: 12px;
        }}
        
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 1px var(--primary);
        }}
        
        .chat-message {{
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.1);
            border: 1px solid var(--outline);
        }}
        
        .chat-message.user {{
            background-color: var(--surface);
            border-left: 4px solid var(--primary);
        }}
        
        .chat-message.bot {{
            background-color: var(--surface-variant);
            border-left: 4px solid var(--secondary);
        }}
        
        .chat-message strong {{
            color: var(--primary) !important;
            font-weight: 600;
        }}
        
        .loading-bar {{
            width: 100%;
            background-color: var(--outline);
            border-radius: 10px;
            margin: 16px 0;
            overflow: hidden;
        }}
        
        .loading-fill {{
            height: 24px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 10px;
            text-align: center;
            line-height: 24px;
            color: var(--on-primary);
            font-size: 12px;
            font-weight: 500;
            transition: width 0.3s ease;
        }}
        
        .api-form {{
            max-width: 600px;
            margin: 50px auto;
            padding: 40px;
            background-color: var(--surface);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(25, 118, 210, 0.2);
            border: 1px solid var(--outline);
        }}
        
        .api-title {{
            text-align: center;
            color: var(--primary);
            margin-bottom: 30px;
        }}
        
        .api-instructions {{
            background-color: var(--surface-variant);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            border-left: 4px solid var(--primary);
        }}
        
        .image-only-mode {{
            background-color: #E8F5E8;
            border: 2px solid #4CAF50;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
        }}
        
        .image-analysis-result {{
            background-color: var(--surface-variant);
            border-left: 4px solid var(--secondary);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .share-button {{
            background-color: #FEE500;
            color: #3A1D1D;
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            border: 1px solid #FDD835;
            cursor: pointer;
            margin-right: 5px;
        }}
        
        .share-button:hover {{
            background-color: #FDD835;
            text-decoration: none;
            color: #3A1D1D;
        }}
        
        .email-button {{
            background-color: #388E3C;
            color: white;
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            cursor: pointer;
        }}
        
        .email-button:hover {{
            background-color: #2E7D32;
            text-decoration: none;
            color: white;
        }}
    </style>
    """, unsafe_allow_html=True)

# 향상된 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 어린이(만 8세 미만)의 건강 문제에 대해 부모나 보호자를 도와주는 **의료 정보 제공 챗봇**입니다. 

⚠️ **중요: 당신은 절대로 진단을 내리거나, 특정 질병을 확정하지 않습니다.** 당신의 역할은 **가능한 원인과 증상에 대한 정보를 제공**하고, **응급 여부를 판단**하며, **병원 방문이 필요한 경우 강조**하는 것입니다.

다음 원칙을 반드시 따라야 합니다:

1. **정확성과 안전성**: 모든 정보는 어린이의 생리적 특성을 고려해야 하며, 불확실한 정보는 제공하지 않습니다.
2. **응급 상황 구분**: 아이의 상태가 위험할 수 있는 경우(예: 고열, 호흡 곤란, 의식 저하 등), 즉시 병원 방문이나 119 신고를 안내해야 합니다.
3. **부모의 판단 보조**: 당신은 의사가 아니므로, 모든 응답은 "가능한 원인" 또는 "의심되는 상황"이라는 식으로 표현해야 합니다.
4. **의료적 면책**: 모든 응답 마지막에는 "이 정보는 참고용이며, 정확한 진단과 치료는 반드시 전문 의료진의 진료를 받아야 합니다."라는 문구를 추가해야 합니다.
5. **친절하고 이해하기 쉬운 언어**: 어린이의 부모나 보호자를 대상으로 하므로, 전문 용어는 간단히 설명하여 사용해야 합니다.

사용자가 아이의 증상(텍스트 또는 이미지)을 입력하면, 다음과 같은 순서로 응답하세요:

1. **증상에 대한 간단한 설명**
2. **가능한 원인 (2~3가지)**
3. **즉시 병원을 가야 하는지 여부 및 판단 기준**
4. **초기 대처 방법 (예: 수액 보충, 휴식, 냉찜질 등)**
5. **주의사항 및 관찰 포인트**
6. **면책 조항 추가**
"""

# 이미지 전용 시스템 프롬프트
IMAGE_SYSTEM_PROMPT = """
당신은 어린이 건강 상담 전문 챗봇입니다. 사용자가 업로드한 이미지를 보고 어린이의 건강 상태를 분석해주세요.

**이미지 분석 시 다음을 수행하세요:**

1. **이미지에서 관찰되는 증상 설명**
   - 피부 상태, 상처, 발진, 부기, 변색 등을 자세히 설명
   - 위치, 크기, 모양, 색깔 등 구체적으로 기술

2. **가능한 원인 분석**
   - 관찰된 증상에 대한 2-3가지 가능한 원인 제시
   - 어린이에게 흔한 질환이나 상황 우선 고려

3. **응급도 판단**
   - 즉시 병원 방문이 필요한지 판단
   - 응급 신호가 있는지 확인 (심각한 감염징후, 심한 외상 등)

4. **초기 대처 방법**
   - 집에서 할 수 있는 응급처치나 관리 방법
   - 피해야 할 행동들

5. **추가 관찰 포인트**
   - 부모가 지켜봐야 할 증상 변화
   - 병원 방문 시기 판단 기준

⚠️ **중요:** 이미지만으로는 완전한 진단이 불가능하므로, 모든 조언은 "이미지상으로 보이는 증상을 바탕으로 한 추정"임을 명시하고, 정확한 진단을 위해서는 반드시 전문 의료진의 진료를 받도록 안내하세요.
"""

# API 키 검증 함수
def validate_api_key(api_key):
    if not api_key:
        return False, "API 키를 입력해주세요."
    if not api_key.startswith('sk-'):
        return False, "API 키 형식이 올바르지 않습니다. 'sk-'로 시작해야 합니다."
    if len(api_key) < 20:
        return False, "API 키 길이가 너무 짧습니다."
    return True, "API 키 형식이 올바릅니다."

# 로딩 바 표시 함수
def show_loading_bar(progress, placeholder):
    placeholder.markdown(f"""
    <div class="loading-bar">
        <div class="loading-fill" style="width: {progress}%">{progress}%</div>
    </div>
    """, unsafe_allow_html=True)

# 이미지를 base64로 인코딩하는 함수
def encode_image_to_base64(uploaded_file):
    """업로드된 이미지를 base64로 인코딩"""
    try:
        # 파일을 다시 읽기 위해 포인터를 처음으로 이동
        uploaded_file.seek(0)
        # 이미지를 바이트로 읽고 base64로 인코딩
        image_bytes = uploaded_file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        return base64_image
    except Exception as e:
        st.error(f"이미지 인코딩 중 오류가 발생했습니다: {str(e)}")
        return None

# 향상된 이미지 분석 함수
def analyze_medical_image(uploaded_file):
    """GPT-4 Vision을 사용하여 의료 이미지 분석"""
    try:
        client = OpenAI(api_key=st.session_state.api_key)
        
        # 이미지를 base64로 인코딩
        base64_image = encode_image_to_base64(uploaded_file)
        if not base64_image:
            return "이미지 처리 중 오류가 발생했습니다."
        
        # 로딩 바 초기화
        progress_placeholder = st.empty()
        
        # 진행 상황 시뮬레이션
        for i in range(0, 101, 20):
            time.sleep(0.2)
            show_loading_bar(i, progress_placeholder)
        
        # GPT-4 Vision API 호출
        response = client.chat.completions.create(
            model="gpt-4o",  # Vision 기능을 지원하는 모델
            messages=[
                {
                    "role": "system",
                    "content": IMAGE_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 이미지를 보고 어린이의 건강 상태를 분석해주세요. 관찰되는 증상, 가능한 원인, 응급도, 초기 대처방법을 포함하여 종합적으로 설명해주세요."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.3  # 의료 정보이므로 낮은 온도로 설정
        )
        
        # 로딩 바 제거
        progress_placeholder.empty()
        
        return response.choices[0].message.content
        
    except Exception as e:
        # 로딩 바 제거
        if 'progress_placeholder' in locals():
            progress_placeholder.empty()
        return f"이미지 분석 중 오류가 발생했습니다: {str(e)}\n\n⚠️ API 키가 올바른지, 그리고 GPT-4 Vision 모델 사용 권한이 있는지 확인해주세요."

# 기존 텍스트+이미지 상담 함수 (수정됨)
def get_medical_advice(symptoms="", uploaded_file=None):
    """OpenAI API를 호출하여 의료 조언을 얻는 함수"""
    try:
        client = OpenAI(api_key=st.session_state.api_key)
        
        # 로딩 바 초기화
        progress_placeholder = st.empty()
        
        # 진행 상황 시뮬레이션
        for i in range(0, 101, 10):
            time.sleep(0.1)
            show_loading_bar(i, progress_placeholder)
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # 이미지가 있고 텍스트 증상이 있는 경우
        if uploaded_file and symptoms.strip():
            base64_image = encode_image_to_base64(uploaded_file)
            if base64_image:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"증상: {symptoms}\n\n첨부된 이미지도 함께 분석해주세요."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                })
            else:
                messages.append({"role": "user", "content": f"증상: {symptoms}"})
        
        # 텍스트 증상만 있는 경우
        elif symptoms.strip():
            messages.append({"role": "user", "content": f"증상: {symptoms}"})
        
        # 실제 API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1200,
            temperature=0.7
        )
        
        # 로딩 바 제거
        progress_placeholder.empty()
        
        return response.choices[0].message.content
        
    except Exception as e:
        # 로딩 바 제거
        if 'progress_placeholder' in locals():
            progress_placeholder.empty()
        return f"죄송합니다. 오류가 발생했습니다: {str(e)}\n\n⚠️ API 키가 올바른지 확인해주세요."

# 개선된 카카오톡 공유 함수
def create_kakao_share_script(message_content, message_id):
    """카카오톡 공유를 위한 JavaScript 생성"""
    # 메시지 내용 정리 (HTML 태그 제거 및 요약)
    clean_content = message_content.replace('<br>', '\n').replace('</br>', '\n')
    # 150자로 제한
    summary = clean_content[:150] + "..." if len(clean_content) > 150 else clean_content
    
    # JavaScript 카카오톡 공유 코드
    share_script = f"""
    <script src="https://developers.kakao.com/sdk/js/kakao.js"></script>
    <script>
        // 카카오 SDK 초기화 (실제 앱 키로 교체 필요)
        if (!window.Kakao.isInitialized()) {{
            window.Kakao.init('YOUR_KAKAO_APP_KEY'); // 실제 카카오 앱 키로 교체
        }}
        
        function shareToKakao_{message_id}() {{
            Kakao.Link.sendDefault({{
                objectType: 'text',
                text: '{summary}',
                link: {{
                    mobileWebUrl: window.location.href,
                    webUrl: window.location.href,
                }},
                buttonTitle: '자세히 보기',
            }});
        }}
    </script>
    """
    return share_script

# 피드백 저장 함수
def save_feedback(message_id, feedback):
    if 'feedback' not in st.session_state:
        st.session_state.feedback = {}
    st.session_state.feedback[message_id] = feedback
    return True

# API 키 입력 폼
def show_api_key_form():
    st.markdown('<div class="api-form">', unsafe_allow_html=True)
    st.markdown('<h1 class="api-title">🔐 OpenAI API 키 인증</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="api-instructions">
        <h3>서비스 사용을 위해 API 키가 필요합니다</h3>
        <p>이 챗봇은 OpenAI의 GPT-4 Vision 모델을 사용하여 어린이 건강 상담을 제공합니다.</p>
        <p><strong>API 키 발급 방법:</strong></p>
        <ol>
            <li>OpenAI 웹사이트(<a href="https://platform.openai.com/" target="_blank">platform.openai.com</a>)에 접속</li>
            <li>회원가입 또는 로그인</li>
            <li>API 키 생성</li>
            <li>GPT-4 Vision 사용 권한 확인</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input(
        "OpenAI API 키를 입력하세요",
        type="password",
        placeholder="sk-...",
        help="OpenAI 플랫폼에서 발급받은 API 키를 입력해주세요"
    )
    
    if st.button("🔑 인증하기", type="primary", use_container_width=True):
        is_valid, message = validate_api_key(api_key)
        if is_valid:
            st.session_state.api_key = api_key
            st.session_state.authenticated = True
            st.success("✅ API 키 인증이 완료되었습니다!")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ {message}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 메인 애플리케이션
def main():
    # CSS 적용
    apply_custom_css()
    
    # 세션 상태 초기화
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    
    # API 키 인증되지 않은 경우
    if not st.session_state.authenticated:
        show_api_key_form()
        return
    
    # 사이드바
    with st.sidebar:
        st.title("👶 어린이 건강 챗봇")
        st.markdown("---")
        
        # API 상태 표시
        st.markdown("### 🔐 API 상태")
        st.success("✅ API 인증 완료")
        
        # API 키 재설정 버튼
        if st.button("🔑 API 키 재설정", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.api_key = ""
            st.rerun()
        
        st.markdown("---")
        
        # 사용 방법
        st.markdown("### 📖 사용 방법")
        st.markdown("1. 👶 아이의 증상을 텍스트로 입력 또는")
        st.markdown("2. 📸 **사진만 첨부해도 자동 분석!**")
        st.markdown("3. 🩺 전문적인 조언을 받아보세요")
        st.markdown("4. 👍👎 피드백을 남겨주세요")
        
        st.markdown("---")
        
        # 카카오톡 공유 설정 안내
        st.markdown("### 💬 카카오톡 공유 안내")
        st.info("카카오톡 공유 기능을 사용하려면 카카오 개발자 사이트에서 앱을 등록하고 JavaScript 키를 발급받아야 합니다.")
        
        st.markdown("---")
        
        # 면책 조항
        st.markdown("### ⚠️ 중요 안내")
        st.markdown("*이 서비스는 참고용이며, 정확한 진단은 반드시 전문 의료진의 진료를 받아야 합니다.*")
        
        # 대화 초기화 버튼
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.session_state.feedback = {}
            st.rerun()
    
    # 메인 콘텐츠
    st.title("👶 어린이 건강 상담 챗봇")
    st.markdown("아이의 증상을 텍스트로 설명하거나, **사진만 첨부해도 자동으로 분석**해드립니다!")
    
    # 입력 섹션
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            symptoms = st.text_area(
                "아이의 증상을 자세히 입력해주세요 (선택사항):",
                height=120,
                placeholder="예: 아이가 39도 열이 나고 기침을 합니다... (사진만 첨부해도 분석 가능!)",
                help="증상을 자세히 설명할수록 더 정확한 조언을 받을 수 있습니다."
            )
        
        with col2:
            uploaded_file = st.file_uploader(
                "📸 사진 첨부",
                type=["jpg", "jpeg", "png"],
                help="부상이나 발진 등의 사진을 첨부하면 자동으로 분석합니다."
            )
            
            if uploaded_file is not None:
                st.image(uploaded_file, caption="첨부된 사진", use_column_width=True)
                st.markdown("""
                <div class="image-only-mode">
                    <strong>🔍 이미지 자동 분석 모드</strong><br>
                    사진만으로도 분석이 가능합니다!
                </div>
                """, unsafe_allow_html=True)
    
    # 제출 버튼들
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        # 일반 상담 버튼 (텍스트 + 이미지)
        if st.button("🩺 종합 상담 받기", type="primary", use_container_width=True):
            if symptoms.strip() or uploaded_file is not None:
                # 사용자 메시지 저장
                user_message_id = f"user_{len(st.session_state.messages)}"
                content_text = symptoms if symptoms.strip() else "이미지를 첨부했습니다."
                
                st.session_state.messages.append({
                    "id": user_message_id,
                    "role": "user",
                    "content": content_text,
                    "has_image": uploaded_file is not None
                })
                
                # 챗봇 응답 생성
                with st.spinner("🤖 전문가 상담 중..."):
                    bot_response = get_medical_advice(symptoms, uploaded_file)
                    bot_message_id = f"bot_{len(st.session_state.messages)}"
                    st.session_state.messages.append({
                        "id": bot_message_id,
                        "role": "bot",
                        "content": bot_response
                    })
                
                st.rerun()
            else:
                st.warning("⚠️ 증상을 입력하거나 사진을 첨부해주세요.")
    
    with button_col2:
        # 이미지 전용 분석 버튼
        if st.button("📸 이미지만 분석하기", type="secondary", use_container_width=True):
            if uploaded_file is not None:
                # 사용자 메시지 저장
                user_message_id = f"user_{len(st.session_state.messages)}"
                st.session_state.messages.append({
                    "id": user_message_id,
                    "role": "user",
                    "content": "이미지 자동 분석을 요청했습니다.",
                    "has_image": True,
                    "image_only": True
                })
                
                # 이미지 전용 분석
                with st.spinner("📸 이미지 분석 중..."):
                    bot_response = analyze_medical_image(uploaded_file)
                    bot_message_id = f"bot_{len(st.session_state.messages)}"
                    st.session_state.messages.append({
                        "id": bot_message_id,
                        "role": "bot",
                        "content": bot_response,
                        "image_analysis": True
                    })
                
                st.rerun()
            else:
                st.warning("📸 먼저 분석할 사진을 첨부해주세요.")
    
    # 채팅 기록 표시
    if st.session_state.messages:
        st.markdown("---")
        st.markdown("### 💬 상담 기록")
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                # 이미지 전용 모드 표시
                if message.get("image_only", False):
                    icon = "📸"
                    mode_text = " (이미지 자동 분석)"
                else:
                    icon = "👨‍👩‍👧‍👦"
                    mode_text = ""
                
                st.markdown(f"""
                <div class="chat-message user">
                    <div>
                        <strong>{icon} 부모님{mode_text}:</strong><br><br>
                        {message["content"]}
                        {"<br><br>📸 <em>이미지가 첨부되었습니다</em>" if message.get('has_image') else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 봇 응답에 분석 타입 표시
                if message.get("image_analysis", False):
                    bot_title = "📸 이미지 분석 결과"
                    analysis_class = "image-analysis-result"
                else:
                    bot_title = "🩺 건강 상담 챗봇"
                    analysis_class = ""
                
                st.markdown(f"""
                <div class="chat-message bot {analysis_class}">
                    <div>
                        <strong>{bot_title}:</strong><br><br>
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 피드백 및 공유 버튼
                col1, col2, col3, col4 = st.columns([1, 1, 2, 6])
                
                with col1:
                    if st.button("👍", key=f"good_{message['id']}", help="도움이 되었어요"):
                        if save_feedback(message['id'], "좋아요"):
                            st.success("✅ 피드백 감사합니다!")
                
                with col2:
                    if st.button("👎", key=f"bad_{message['id']}", help="별로였어요"):
                        if save_feedback(message['id'], "별로에요"):
                            st.success("✅ 피드백 감사합니다. 개선하겠습니다!")
                
                with col3:
                    # 카카오톡 공유 버튼 (복사 기능으로 대체)
                    if st.button("💬 카카오톡 공유", key=f"kakao_{message['id']}", help="내용을 복사합니다"):
                        # 클립보드에 복사하는 기능
                        clean_content = message["content"].replace('<br>', '\n').replace('</br>', '\n')
                        summary = clean_content[:500] + "..." if len(clean_content) > 500 else clean_content
                        
                        # pyperclip이 설치되어 있지 않으므로 대체 방법 사용
                        st.markdown(f"""
                        <textarea id="copy_text_{message['id']}" style="position: absolute; left: -9999px;">{summary}</textarea>
                        <script>
                            var copyText = document.getElementById("copy_text_{message['id']}");
                            copyText.select();
                            document.execCommand("copy");
                        </script>
                        """, unsafe_allow_html=True)
                        st.info("📋 내용이 클립보드에 복사되었습니다. 카카오톡에 붙여넣기해주세요!")
                
                with col4:
                    # 이메일 공유 버튼
                    email_subject = urllib.parse.quote("어린이 건강 상담 결과")
                    email_body = urllib.parse.quote(message['content'][:1000])
                    email_link = f"mailto:?subject={email_subject}&body={email_body}"
                    
                    st.markdown(f"""
                    <a href="{email_link}" class="email-button" target="_blank">
                        📧 이메일로 보내기
                    </a>
                    """, unsafe_allow_html=True)
    
    else:
        # 첫 방문 시 안내 메시지
        st.info("""
        🩺 **건강 상담 챗봇**
        
        안녕하세요! 어린이 건강 상담 챗봇입니다. 👶
        
        **🆕 새로운 기능:**
        • 📝 **텍스트 상담**: 증상을 자세히 설명해주세요
        • 📸 **이미지 자동 분석**: 사진만 첨부해도 즉시 분석!  
        • 🔄 **종합 분석**: 텍스트 + 이미지 함께 분석
        
        피부 발진, 상처, 부상, 이상 증상 등의 사진을 첨부하시면 AI가 자동으로 분석하여 상세한 건강 조언을 제공합니다.
        """)
        
        st.warning("⚠️ **중요**: 이 서비스는 참고용이며, 응급상황 시에는 즉시 119에 신고하거나 병원에 방문하세요.")
        
        # 기능 데모 카드들
        st.markdown("### 🌟 주요 기능")
        
        demo_col1, demo_col2, demo_col3 = st.columns(3)
        
        with demo_col1:
            with st.container():
                st.markdown("#### 📝 텍스트 상담")
                st.write("아이의 증상을 자세히 설명해주세요")
                st.caption("예: 열, 기침, 복통 등")
        
        with demo_col2:
            with st.container():
                st.markdown("#### 📸 이미지 분석") 
                st.write("사진만 첨부하면 자동으로 분석")
                st.caption("예: 발진, 상처, 부상 등")
        
        with demo_col3:
            with st.container():
                st.markdown("#### 🔄 종합 분석")
                st.write("텍스트와 이미지를 함께 분석")
                st.caption("가장 정확한 상담")

if __name__ == "__main__":
    main()
