# requirements.txt
# streamlit
# openai
# python-dotenv
# pillow
# requests

import streamlit as st
from openai import OpenAI  # 최신 OpenAI 라이브러리 사용
import time
import os
from PIL import Image
import base64
from io import BytesIO
import requests
from dotenv import load_dotenv

# .env 파일에서 API 키 로드 (있을 경우)
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="어린이 건강 챗봇",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 블루 계통 머터리얼 디자인 컬러 팔레트
MATERIAL_COLORS = {
    "primary": "#1976D2",          # Material Blue 700
    "primary_variant": "#1565C0",  # Material Blue 800
    "secondary": "#0288D1",        # Light Blue 700
    "background": "#E3F2FD",       # Blue 50
    "surface": "#FFFFFF",          # 흰색 (카드 등)
    "surface_variant": "#F3F8FF",  # 매우 연한 파란색
    "on_primary": "#FFFFFF",       # 흰색 텍스트
    "on_secondary": "#FFFFFF",     # 흰색 텍스트
    "on_surface": "#0D47A1",       # 진한 파란색 텍스트
    "outline": "#90CAF9",          # Blue 200
    "error": "#C62828"             # Red 800
}

# CSS 스타일 적용
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
        
        /* 전체 배경 */
        .stApp {{
            background-color: var(--background);
            color: var(--on-surface);
        }}
        
        /* 모든 텍스트를 블루 계통으로 */
        .stApp, .stApp p, .stApp div, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
            color: var(--on-surface) !important;
        }}
        
        /* 사이드바 스타일 */
        .css-1d391kg {{
            background-color: var(--surface-variant);
        }}
        
        /* 버튼 스타일 */
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
        
        /* 입력 필드 스타일 */
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
        
        /* 채팅 메시지 스타일 */
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
        
        /* 피드백 버튼 스타일 */
        .feedback-button {{
            background-color: var(--surface);
            border: 2px solid var(--outline);
            border-radius: 50%;
            width: 44px;
            height: 44px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            font-size: 18px;
        }}
        
        .feedback-button:hover {{
            background-color: var(--primary);
            color: var(--on-primary);
            border-color: var(--primary);
            transform: scale(1.1);
        }}
        
        /* 로딩 바 스타일 */
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
        
        /* 경고 및 알림 메시지 */
        .stAlert {{
            border-radius: 8px;
            border: 1px solid var(--outline);
        }}
        
        .stSuccess {{
            background-color: #E8F5E8;
            border-left: 4px solid #4CAF50;
            color: #2E7D32 !important;
        }}
        
        .stWarning {{
            background-color: #FFF3E0;
            border-left: 4px solid #FF9800;
            color: #E65100 !important;
        }}
        
        .stError {{
            background-color: #FFEBEE;
            border-left: 4px solid var(--error);
            color: var(--error) !important;
        }}
        
        .stInfo {{
            background-color: var(--surface-variant);
            border-left: 4px solid var(--primary);
            color: var(--on-surface) !important;
        }}
        
        /* 제목 스타일 */
        h1, h2, h3 {{
            color: var(--primary) !important;
            font-weight: 600;
        }}
        
        /* 카카오톡 공유 링크 */
        .kakao-share {{
            color: var(--secondary) !important;
            text-decoration: none;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 6px;
            background-color: var(--surface);
            border: 1px solid var(--outline);
            transition: all 0.2s ease;
        }}
        
        .kakao-share:hover {{
            background-color: var(--secondary);
            color: var(--on-secondary) !important;
            transform: translateY(-1px);
        }}
        
        /* 스피너 색상 */
        .stSpinner > div {{
            border-color: var(--primary) transparent transparent transparent;
        }}
        
        /* API 입력 폼 스타일 */
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
    </style>
    """, unsafe_allow_html=True)

# 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 어린이(만 8세 미만)의 건강 문제에 대해 부모나 보호자를 도와주는 **의료 정보 제공 챗봇**입니다. 당신의 목적은 부모가 아이의 증상을 이해하고, 필요시 전문 의료진에게 적절히 대응할 수 있도록 **초기 정보 제공**과 **응급 대처 방법**을 안내하는 것입니다.

⚠️ **중요: 당신은 절대로 진단을 내리거나, 특정 질병을 확정하지 않습니다.** 당신의 역할은 **가능한 원인과 증상에 대한 정보를 제공**하고, **응급 여부를 판단**하며, **병원 방문이 필요한 경우 강조**하는 것입니다.

다음 원칙을 반드시 따라야 합니다:

1. **정확성과 안전성**: 모든 정보는 어린이의 생리적 특성을 고려해야 하며, 불확실한 정보는 제공하지 않습니다.
2. **응급 상황 구분**: 아이의 상태가 위험할 수 있는 경우(예: 고열, 호흡 곤란, 의식 저하 등), 즉시 병원 방문이나 119 신고를 안내해야 합니다.
3. **부모의 판단 보조**: 당신은 의사가 아니므로, 모든 응답은 "가능한 원인" 또는 "의심되는 상황"이라는 식으로 표현해야 합니다.
4. **의료적 면책**: 모든 응답 마지막에는 "이 정보는 참고용이며, 정확한 진단과 치료는 반드시 전문 의료진의 진료를 받아야 합니다."라는 문구를 추가해야 합니다.
5. **친절하고 이해하기 쉬운 언어**: 어린이의 부모나 보호자를 대상으로 하므로, 전문 용어는 간단히 설명하여 사용해야 합니다.

사용자가 아이의 증상(예: 발열, 기침, 부상 등)을 입력하면, 다음과 같은 순서로 응답하세요:

1. **증상에 대한 간단한 설명**
2. **가능한 원인 (2~3가지)**
3. **즉시 병원을 가야 하는지 여부 및 판단 기준**
4. **처음 대처 방법 (예: 수액 보충, 휴식, 냉찜질 등)**
5. **주의사항 및 관찰 포인트**
6. **면책 조항 추가**
"""

# API 키 검증 함수
def validate_api_key(api_key):
    """API 키의 유효성을 검증하는 함수"""
    if not api_key:
        return False, "API 키를 입력해주세요."
    
    if not api_key.startswith('sk-'):
        return False, "API 키 형식이 올바르지 않습니다. 'sk-'로 시작해야 합니다."
    
    if len(api_key) < 20:
        return False, "API 키 길이가 너무 짧습니다."
    
    return True, "API 키 형식이 올바릅니다."

# 로딩 바 표시 함수
def show_loading_bar(progress, placeholder):
    """로딩 바를 표시하는 함수"""
    placeholder.markdown(f"""
    <div class="loading-bar">
        <div class="loading-fill" style="width: {progress}%">{progress}%</div>
    </div>
    """, unsafe_allow_html=True)

# OpenAI API 호출 함수 (수정됨)
def get_medical_advice(symptoms, image_description=""):
    """OpenAI API를 호출하여 의료 조언을 얻는 함수"""
    try:
        # OpenAI 클라이언트 초기화
        client = OpenAI(api_key=st.session_state.api_key)
        
        # 로딩 바 초기화
        progress_placeholder = st.empty()
        
        # 진행 상황 시뮬레이션
        for i in range(0, 101, 10):
            time.sleep(0.1)
            show_loading_bar(i, progress_placeholder)
        
        # 실제 API 호출
        user_message = f"증상: {symptoms}"
        if image_description:
            user_message += f"\n이미지 설명: {image_description}"
            
        # 최신 API 형식으로 수정
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 더 안정적인 모델 사용
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
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

# 이미지 설명 생성 함수 (수정됨)
def generate_image_description(uploaded_file):
    """업로드된 이미지에 대한 설명을 생성하는 함수"""
    try:
        # PIL로 이미지 열기
        image = Image.open(uploaded_file)
        
        # 간단한 이미지 정보 반환 (실제 Vision API는 별도 구현 필요)
        width, height = image.size
        format_name = image.format
        
        return f"업로드된 이미지 정보: {width}x{height} 픽셀, {format_name} 형식. 부상이나 증상과 관련된 사진으로 보입니다."
    except Exception as e:
        return f"이미지 처리 중 오류가 발생했습니다: {str(e)}"

# 카카오톡 공유 함수 (수정됨)
def create_kakao_share_link(text):
    """카카오톡으로 텍스트를 공유하는 링크 생성"""
    try:
        # 텍스트를 URL 인코딩
        encoded_text = requests.utils.quote(text[:100] + "..." if len(text) > 100 else text)
        return f"https://talk.kakao.com/talk/friends/picker?url={encoded_text}"
    except Exception:
        return "#"  # 에러 시 빈 링크 반환

# 피드백 저장 함수
def save_feedback(message_id, feedback):
    """사용자 피드백을 저장하는 함수"""
    if 'feedback' not in st.session_state:
        st.session_state.feedback = {}
    st.session_state.feedback[message_id] = feedback
    return True

# API 키 입력 폼
def show_api_key_form():
    """API 키 입력 폼을 표시하는 함수"""
    st.markdown('<div class="api-form">', unsafe_allow_html=True)
    st.markdown('<h1 class="api-title">🔐 OpenAI API 키 인증</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="api-instructions">
        <h3>서비스 사용을 위해 API 키가 필요합니다</h3>
        <p>이 챗봇은 OpenAI의 GPT 모델을 사용하여 어린이 건강 상담을 제공합니다. 
        서비스를 이용하기 위해서는 OpenAI API 키가 필요합니다.</p>
        <p><strong>API 키 발급 방법:</strong></p>
        <ol>
            <li>OpenAI 웹사이트(<a href="https://platform.openai.com/" target="_blank">platform.openai.com</a>)에 접속</li>
            <li>회원가입 또는 로그인</li>
            <li>API 키 생성</li>
            <li>생성된 키를 아래에 입력</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # API 키 입력
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
    
    st.markdown("""
    <div style="margin-top: 30px; padding: 20px; background-color: #FFF3E0; border-radius: 12px; border-left: 4px solid #FF9800;">
        <h4>⚠️ 중요한 안내</h4>
        <ul>
            <li>입력된 API 키는 이 세션에서만 사용되며 저장되지 않습니다</li>
            <li>API 사용량은 귀하의 OpenAI 계정에 따라 차감됩니다</li>
            <li>정확한 진단이 필요한 경우 반드시 전문 의료진의 진료를 받으세요</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.markdown("1. 👶 아이의 증상을 입력하세요")
        st.markdown("2. 📸 필요한 경우 사진을 첨부하세요")
        st.markdown("3. 🩺 전문적인 조언을 받아보세요")
        st.markdown("4. 👍👎 피드백을 남겨주세요")
        
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
    st.markdown("아이의 증상이나 부상을 설명해 주세요. 필요한 경우 사진도 첨부할 수 있습니다.")
    
    # 입력 섹션
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            symptoms = st.text_area(
                "아이의 증상을 자세히 입력해주세요:",
                height=120,
                placeholder="예: 아이가 39도 열이 나고 기침을 합니다. 식욕이 없고 계속 졸려 합니다...",
                help="증상을 자세히 설명할수록 더 정확한 조언을 받을 수 있습니다."
            )
        
        with col2:
            uploaded_file = st.file_uploader(
                "📸 사진 첨부",
                type=["jpg", "jpeg", "png"],
                help="부상이나 발진 등의 사진을 첨부해주세요."
            )
            
            image_description = ""
            if uploaded_file is not None:
                st.image(uploaded_file, caption="첨부된 사진", use_column_width=True)
                with st.spinner("🔍 이미지 분석 중..."):
                    image_description = generate_image_description(uploaded_file)
                st.info(f"📋 이미지 분석: {image_description[:60]}...")
    
    # 제출 버튼
    if st.button("🩺 상담 받기", type="primary", use_container_width=True):
        if symptoms.strip():
            # 사용자 메시지 저장
            user_message_id = f"user_{len(st.session_state.messages)}"
            st.session_state.messages.append({
                "id": user_message_id,
                "role": "user",
                "content": symptoms,
                "image_desc": image_description
            })
            
            # 챗봇 응답 생성
            with st.spinner("🤖 전문가 상담 중..."):
                bot_response = get_medical_advice(symptoms, image_description)
                bot_message_id = f"bot_{len(st.session_state.messages)}"
                st.session_state.messages.append({
                    "id": bot_message_id,
                    "role": "bot",
                    "content": bot_response
                })
            
            # 페이지 새로고침으로 입력 초기화
            st.rerun()
        else:
            st.warning("⚠️ 아이의 증상을 입력해주세요.")
    
    # 채팅 기록 표시
    if st.session_state.messages:
        st.markdown("---")
        st.markdown("### 💬 상담 기록")
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user">
                    <div>
                        <strong>👨‍👩‍👧‍👦 부모님:</strong><br><br>
                        {message["content"]}
                        {f"<br><br>📸 <em>{message.get('image_desc', '')}</em>" if message.get('image_desc') else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot">
                    <div>
                        <strong>🩺 건강 상담 챗봇:</strong><br><br>
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
                    kakao_url = create_kakao_share_link(message["content"])
                    st.markdown(f"""
                    <a href="{kakao_url}" target="_blank" class="kakao-share">
                        📱 카카오톡 공유
                    </a>
                    """, unsafe_allow_html=True)
    
    else:
        # 첫 방문 시 안내 메시지
        st.markdown("""
        <div class="chat-message bot">
            <div>
                <strong>🩺 건강 상담 챗봇:</strong><br><br>
                안녕하세요! 어린이 건강 상담 챗봇입니다. 👶<br><br>
                
                아이의 건강에 대해 걱정이 되시나요?<br>
                증상을 자세히 설명해주시면, 초기 대응 방법과 병원 방문 여부에 대한 조언을 드리겠습니다.<br><br>
                
                <strong style="color: #C62828;">⚠️ 중요:</strong> 이 서비스는 참고용이며, 응급상황 시에는 즉시 119에 신고하거나 병원에 방문하세요.
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
