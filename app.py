import time
import streamlit as st
from google import genai

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="CalculAI - ผู้ช่วยคณิตศาสตร์",
    page_icon="⚡",
    layout="wide"
)

# ดึง API Key จาก Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

# แถบด้านข้าง (Sidebar)
with st.sidebar:
    st.header("⚙️ การตั้งค่าระบบ")
    if api_key:
        st.success("🟢 ดึง Gemini API Key จาก Secrets สำเร็จ")
    else:
        user_key = st.text_input("🔑 ใส่ Gemini API Key:", type="password")
        if user_key:
            api_key = user_key

st.title("⚡ CalculAI")
st.subheader("ผู้ช่วยแก้โจทย์ & เครื่องมือสร้างข้อสอบคณิตศาสตร์อัจฉริยะ (ป.1 - ม.6)")

if not api_key:
    st.warning("⚠️ กรุณาระบุ Gemini API Key ในแถบด้านข้างก่อนใช้งานครับ")
    st.stop()

# สร้าง Client ด้วย SDK ตัวใหม่ล่าสุด (google-genai)
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อระบบได้: {e}")
    st.stop()

# ฟังก์ชันดึงคำตอบ พร้อมระบบสลับโมเดลและลองใหม่อัตโนมัติ
def generate_response(prompt_text):
    # รายชื่อโมเดลที่จะเรียงลำดับลองใช้
    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-2.5-pro']
    
    for model_name in models_to_try:
        for attempt in range(2): # ลองยิงซ้ำโมเดลละ 2 ครั้งกรณีติด Quota
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                err_str = str(e)
                # ถ้าติดโควตา (429/Quota) ให้รอ 4 วินาทีแล้วลองใหม่
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota" in err_str:
                    time.sleep(4)
                    continue
                # ถ้าโมเดลไม่มีอยู่จริง (404) ให้ข้ามไปลองโมเดลถัดไป
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    break
                else:
                    st.error(f"เกิดข้อผิดพลาดจาก API ({model_name}): {err_str}")
                    return None
                    
    st.warning("⏳ ขณะนี้โควตา API ฟรีเต็มชั่วคราว กรุณารอประมาณ 30 วินาที แล้วกดใหม่อีกครั้งครับ")
    return None

# แท็บตัวเลือกการใช้งาน
tab1, tab2, tab3 = st.tabs([
    "💬 แชทถาม-ตอบ & แก้โจทย์", 
    "🎯 เครื่องมือสร้างโจทย์ (ตามระดับ/เรื่อง)", 
    "🪄 สร้างโจทย์ด้วยพรอมต์อิสระ"
])

# =========================================================
# TAB 1: CHAT & SOLVER
# =========================================================
with tab1:
    st.write("💡 **ลองกดถามโจทย์ตัวอย่าง:**")
    col1, col2, col3 = st.columns(3)
    
    prompt_input = ""
    if col1.button("📐 แก้สมการ: 4x + 12 = 36"):
        prompt_input = "ช่วยแก้สมการ 4x + 12 = 36 แสดงวิธีทำอย่างละเอียด"
    if col2.button("📊 หาอนุพันธ์: f(x) = 3x² + 5x - 2"):
        prompt_input = "ช่วยหาอนุพันธ์ของ f(x) = 3x² + 5x - 2 พร้อมอธิบายสเต็ป"
    if col3.button("🍕 โจทย์ปัญหาเศษส่วน ป.5"):
        prompt_input = "แม่มีเงิน 2,500 บาท ซื้อของไป 3/5 ของเงินทั้งหมด แม่เหลือเงินกี่บาท?"

    user_query = st.text_input("พิมพ์โจทย์คณิตศาสตร์ตรงนี้...", value=prompt_input, key="chat_input")
    
    if st.button("ส่งคำถาม", type="primary", key="btn_chat"):
        if user_query:
            with st.spinner("กำลังประมวลผลคำตอบ..."):
                output = generate_response(user_query)
                if output:
                    st.markdown("### 📝 คำตอบและวิธีทำ:")
                    st.write(output)

# =========================================================
# TAB 2: STRUCTURED GENERATOR
# =========================================================
with tab2:
    st.markdown("### 🎯 เครื่องมือออกข้อสอบและแบบฝึกหัด")
    col_g, col_d = st.columns(2)
    with col_g:
        grade = st.selectbox("🎓 เลือกระดับชั้น:", [f"ป.{i}" for i in range(1, 7)] + [f"ม.{i}" for i in range(1, 7)])
        num_q = st.slider("🔢 จำนวนโจทย์ (ข้อ):", 1, 10, 3)
    with col_d:
        topic = st.text_input("📚 บทเรียน/เรื่องที่ต้องการ:", placeholder="เช่น สมการ, เวกเตอร์, เศษส่วน")
        show_sol = st.checkbox("✅ รวมเฉลยละเอียด", value=True)

    if st.button("🚀 สร้างโจทย์เลย!", use_container_width=True, key="btn_tab2"):
        if not topic.strip():
            st.warning("กรุณากรอกเรื่องที่ต้องการสร้างโจทย์ก่อนครับ")
        else:
            prompt_t2 = f"สร้างโจทย์คณิตศาสตร์ ระดับ {grade} เรื่อง {topic} จำนวน {num_q} ข้อ {'พร้อมเฉลยละเอียด' if show_sol else 'ไม่ต้องมีเฉลย'}"
            with st.spinner("กำลังสร้างชุดโจทย์..."):
                output = generate_response(prompt_t2)
                if output:
                    st.markdown("---")
                    st.write(output)

# =========================================================
# TAB 3: CUSTOM PROMPT GENERATOR
# =========================================================
with tab3:
    st.markdown("### 🪄 สั่งสร้างโจทย์ด้วยคำสั่งอิสระ")
    custom_p = st.text_area("✍️ พิมพ์คำสั่งสร้างโจทย์ที่ต้องการ:", height=120, placeholder="เช่น ออกโจทย์คณิตตลกร้าย 1 ข้อ เรื่องการคำนวณภาษี พร้อมวิธีคิด")
    if st.button("✨ สร้างโจทย์ตามสั่ง", use_container_width=True, key="btn_tab3"):
        if not custom_p.strip():
            st.warning("กรุณากรอกคำสั่งก่อนครับ")
        else:
            with st.spinner("กำลังสร้างโจทย์ตามสั่ง..."):
                output = generate_response(custom_p)
                if output:
                    st.markdown("---")
                    st.write(output)
