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
                # 카카오톡 공유 버튼
                if st.session_state.get('kakao_key'):
                    # 실제 카카오 키로 대체된 공유 버튼 생성
                    share_button_html = create_kakao_share_button(
                        message["content"], 
                        message['id']
                    ).replace('YOUR_KAKAO_APP_KEY', st.session_state.kakao_key)
                    st.markdown(share_button_html, unsafe_allow_html=True)
                else:
                    # 카카오 키가 없으면 복사 기능으로 대체
                    if st.button("💬 내용 복사", key=f"copy_{message['id']}", help="내용을 복사합니다"):
                        clean_content = message["content"].replace('<br>', '\n').replace('</br>', '\n')
                        summary = clean_content[:500] + "..." if len(clean_content) > 500 else clean_content
                        
                        st.markdown(f"""
                        <textarea id="copy_text_{message['id']}" style="position: absolute; left: -9999px;">{summary}</textarea>
                        <script>
                            var copyText = document.getElementById("copy_text_{message['id']}");
                            copyText.select();
                            document.execCommand("copy");
                        </script>
                        """, unsafe_allow_html=True)
                        st.info("📋 내용이 클립보드에 복사되었습니다!")
            
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
