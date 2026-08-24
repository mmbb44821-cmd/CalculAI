import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------
# CONFIGURATION & PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="CalculAI - Smart Math Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM CSS (GLASSMORPHISM MODERN THEME)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* Hero Header Card */
    .hero-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .hero-title {
        background: linear-gradient(90deg, #a855f7 0%, #6366f1 50%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem !important;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* Custom Chat Message */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        padding: 1rem 1.25rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(255, 255, 255, 0.03);
        padding: 8px 12px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 12px;
        color: #94a3b8;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
    }

    /* Button Enhancements */
    .stButton>button {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #a855f7, #6366f1) !important;
        border-color: transparent !important;
        box-shadow: 0 5px 15px rgba(168, 85, 247, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ **ตั้งค่าระบบ (Settings)**")
    
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        api_key = st.text_input("🔑 ใส่ Gemini API Key:", type="password", help="รับฟรีได้ที่ aistudio.google.com")
    else:
        st.success("🟢 API Key พร้อมใช้งานแล้ว", icon="✅")
        
    st.divider()
    st.markdown("### 🤖 **โมเดลที่ใช้งาน**")
    st.caption("CalculAI Core (Gemini 1.5 Flash)")
    
    st.divider()
    if st.button("🗑️ ล้างประวัติการคุย", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------
st.markdown("""
<div class="hero-card">
    <div class="hero-title">⚡ CalculAI</div>
    <div class="hero-subtitle">ผู้ช่วยแก้โจทย์ & เครื่องมือสร้างข้อสอบคณิตศาสตร์อัจฉริยะ (ป.1 - ม.6)</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN TABS SYSTEM
# ---------------------------------------------------------
tab_chat, tab_gen_structured, tab_gen_custom = st.tabs([
    "💬 แชทถาม-ตอบ & แก้โจทย์", 
    "🎯 เครื่องมือสร้างโจทย์ (ตามระดับ/เรื่อง)", 
    "🪄 สร้างโจทย์ด้วยพรอมต์อิสระ"
])

# =========================================================
# TAB 1: CHAT & SOLVER
# =========================================================
with tab_chat:
    st.markdown("##### 💡 **ลองกดถามโจทย์ตัวอย่าง:**")
    col1, col2, col3 = st.columns(3)
    sample_prompt = None

    if col1.button("📐 แก้สมการ: 4x + 12 = 36", use_container_width=True):
        sample_prompt = "หาค่า x จากสมการ 4x + 12 = 36 พร้อมอธิบายวิธีทำแบบเป็นขั้นตอน"
    if col2.button("📊 หาอนุพันธ์: f(x) = 3x² + 5x - 2", use_container_width=True):
        sample_prompt = "จงหาดิฟ (Derivative) ของ f(x) = 3x^2 + 5x - 2 พร้อมบอกสูตรที่ใช้"
    if col3.button("🍕 โจทย์ปัญหาเศษส่วน ป.5", use_container_width=True):
        sample_prompt = "สร้างโจทย์ปัญหาเรื่องการบวกเศษส่วนสำหรับเด็ก ป.5 จำนวน 1 ข้อพร้อมเฉลย"

    st.write("")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    user_input = st.chat_input("พิมพ์โจทย์คณิตศาสตร์ตรงนี้... (เช่น หาพื้นที่สามเหลี่ยมฐาน 10 สูง 5)")
    prompt = sample_prompt or user_input

    if prompt:
        if not api_key:
            st.error("⚠️ กรุณาระบุ Gemini API Key ในแถบด้านข้างก่อนใช้งานครับ")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            sys_prompt = f"""คุณคือ CalculAI ผู้ช่วยและติวเตอร์คณิตศาสตร์อัจฉริยะ 
            - แสดงวิธีทำเป็นขั้นตอนอย่างเป็นระบบ
            - ใช้ LaTeX สวยงามสำหรับสูตรคณิตศาสตร์ (เช่น $x^2 + y^2 = r^2$)
            - ตอบเป็นภาษาไทย มีสัญลักษณ์และอิโมจิน่าอ่าน
            
            โจทย์ที่ต้องตอบ: {prompt}"""

            with st.chat_message("assistant", avatar="⚡"):
                with st.spinner("🧠 CalculAI กำลังคิดวิธีทำและคำนวณ..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(sys_prompt)
                        
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# =========================================================
# TAB 2: STRUCTURED PROBLEM GENERATOR
# =========================================================
with tab_gen_structured:
    st.markdown("### 🎯 **เครื่องมือออกข้อสอบและแบบฝึกหัด**")
    st.caption("กำหนดระดับชั้น ความยาก และบทเรียนเพื่อสร้างชุดโจทย์แบบเฉพาะเจาะจง")

    with st.container():
        col_grade, col_diff = st.columns([1, 2])
        
        with col_grade:
            grade_list = [f"ป.{i}" for i in range(1, 7)] + [f"ม.{i}" for i in range(1, 7)]
            selected_grade = st.selectbox("🎓 เลือกระดับชั้นเรียน:", grade_list, index=6)
            num_questions = st.slider("🔢 จำนวนโจทย์ (ข้อ):", min_value=1, max_value=10, value=3)

        with col_diff:
            difficulty = st.slider(
                "🔥 เลือกระดับความยาก (1 - 100):", 
                min_value=1, 
                max_value=100, 
                value=40,
                help="1-20: พื้นฐานเข้าใจง่าย / 21-60: ปานกลางปรกติ / 61-80: โจทย์ประยุกต์ / 81-100: ระดับแข่งขัน/ข้อสอบเข้า"
            )
            
            if difficulty <= 25:
                st.info("🟢 ระดับ: ง่าย / ปรับพื้นฐาน")
            elif difficulty <= 60:
                st.warning("🟡 ระดับ: ปานกลาง / การบ้านทั่วไป")
            elif difficulty <= 85:
                st.error("🟠 ระดับ: ยาก / โจทย์ประยุกต์สอบเข้า")
            else:
                st.error("🔴 ระดับ: โคตรยาก / โจทย์แข่งขันโอลิมปิก")

        topic_input = st.text_input(
            "📚 พิมพ์เรื่อง/บทเรียนที่ต้องการออกโจทย์:", 
            placeholder="เช่น สมการเชิงเส้นตัวแปรเดียว, เวกเตอร์, พาราโบลา, แคลคูลัส, โจทย์ปัญหาเศษส่วน"
        )
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            include_solutions = st.checkbox("✅ ต้องการเฉลยละเอียดแบบแสดงวิธีทำ", value=True)
        with col_opt2:
            include_hints = st.checkbox("💡 ใส่คำใบ้/สูตรที่ต้องใช้ประจำข้อ", value=True)

        generate_btn = st.button("🚀 สร้างโจทย์คณิตศาสตร์เลย!", use_container_width=True)

    if generate_btn:
        if not api_key:
            st.error("⚠️ กรุณาระบุ Gemini API Key ในแถบด้านข้างก่อนครับ")
        elif not topic_input.strip():
            st.warning("⚠️ กรุณากรอกเรื่องที่เรียนก่อนกดสร้างโจทย์นะครับ")
        else:
            prompt_gen = f"""คุณคือ CalculAI ผู้เชี่ยวชาญการสร้างข้อสอบและแบบฝึกหัดคณิตศาสตร์
            โปรดสร้างแบบฝึกหัดคณิตศาสตร์ตามเงื่อนไขต่อไปนี้:
            
            1. ระดับชั้น: {selected_grade}
            2. เรื่อง/หัวข้อ: {topic_input}
            3. ระดับความยาก: {difficulty}/100 (1=ง่ายมาก, 100=ยากระดับแข่งขัน)
            4. จำนวนโจทย์: {num_questions} ข้อ
            
            เงื่อนไขการจัดรูปแบบ:
            - หัวข้อใหญ่ต้องระบุ ระดับชั้น เรื่อง และระดับความยากชัดเจน
            - แสดงโจทย์ทีละข้อให้ชัดเจน ใช้สัญลักษณ์ LaTeX ($...$) จัดสูตรคณิตศาสตร์ให้อ่านง่าย
            - {"รวมส่วน '💡 คำใบ้/สูตรสำคัญ' สำหรับแต่ละข้อ" if include_hints else ""}
            - {"รวมส่วน '📝 เฉลยอย่างละเอียด' แบบแสดงขั้นตอนคิดเป็นข้อๆ ไว้ที่ส่วนท้ายของชุดโจทย์" if include_solutions else "ไม่ต้องใส่เฉลย"}
            - ใช้ภาษาไทย สไตล์เป็นกันเอง สวยงาม อ่านง่ายน่าทำ"""

            with st.spinner("✨ CalculAI กำลังสร้างชุดโจทย์คุณภาพสูง..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt_gen)
                    
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# =========================================================
# TAB 3: CUSTOM PROMPT GENERATOR
# =========================================================
with tab_gen_custom:
    st.markdown("### 🪄 **สั่งสร้างโจทย์ด้วยพรอมต์อิสระ (Custom Prompt)**")
    st.caption("พิมพ์อธิบายโจทย์ในสไตล์ที่คุณต้องการได้เต็มที่ ไม่มีขีดจำกัด!")

    custom_prompt = st.text_area(
        "✍️ พิมพ์สั่งสไตล์หรือลักษณะโจทย์ที่ต้องการ:",
        height=150,
        placeholder="ตัวอย่าง:\n- ออกโจทย์ปัญหาคณิตศาสตร์เกี่ยวกับการซื้อขายของในเกมออนไลน์ สำหรับเด็ก ม.2 จำนวน 3 ข้อ พร้อมเฉลย\n- ขอโจทย์แคลคูลัสประยุกต์กับวิศวกรรมแบบตลกร้าย 1 ข้อ\n- ออกข้อสอบตัวเลือก 4 ตัวเลือก เรื่องสถิติ ม.6 พร้อมเฉลยคำตอบที่ถูกต้อง"
    )

    custom_btn = st.button("✨ สร้างโจทย์ตามสั่ง", use_container_width=True)

    if custom_btn:
        if not api_key:
            st.error("⚠️ กรุณาระบุ Gemini API Key ในแถบด้านข้างก่อนครับ")
        elif not custom_prompt.strip():
            st.warning("⚠️ กรุณาพิมพ์คำสั่ง/พรอมต์ก่อนกดปุ่มครับ")
        else:
            full_custom_prompt = f"""คุณคือ CalculAI สร้างโจทย์คณิตศาสตร์อัจฉริยะ
            โปรดสร้างโจทย์คณิตศาสตร์ตามคำสั่งของผู้ใช้ดังต่อไปนี้:
            
            "{custom_prompt}"
            
            ข้อกำหนดเพิ่มเติม:
            - จัดรูปแบบคำตอบให้สวยงาม อ่านง่าย ใช้สัญลักษณ์คณิตศาสตร์ LaTeX ($...$)
            - ให้คำตอบเป็นภาษาไทยและใช้อิโมจิตกแต่งให้น่าสนใจ"""

            with st.spinner("🪄 CalculAI กำลังรังสรรค์โจทย์ตามสั่ง..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(full_custom_prompt)
                    
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
