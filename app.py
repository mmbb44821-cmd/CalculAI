import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# SETUP & CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="CalculAI - Powered by Gemini",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ CalculAI (Powered by Google Gemini)")

# 1. ดึง Gemini API Key จาก Secrets
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")

if not gemini_api_key:
    gemini_api_key = st.text_input("🔑 กรุณากรอก Google Gemini API Key:", type="password")

if not gemini_api_key:
    st.warning("⚠️ กรุณาระบุ API Key ก่อนเริ่มใช้งานครับ")
    st.stop()

# 2. เชื่อมต่อ Client ไปยัง Google Gemini API
client = genai.Client(api_key=gemini_api_key)

# 3. ฟังก์ชันสำหรับส่งคำถามไปยัง Gemini
def generate_response(prompt_text):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # รุ่นที่ประมวลผลเร็วและเก่งคณิตศาสตร์/โค้ด
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction="คุณคือครูสอนคณิตศาสตร์อัจฉริยะ แสดงวิธีทำและอธิบายขั้นตอนการแก้โจทย์อย่างเป็นระบบ เข้าใจง่าย ใช้ภาษาไทยที่สุภาพ",
                temperature=0.2, # ปรับอุณหภูมิให้ต่ำลงเพื่อความแม่นยำทางคณิตศาสตร์
            )
        )
        return response.text
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเรียกใช้ Gemini API: {e}")
        return None

# ---------------------------------------------------------
# UI STREAMLIT (ตัวอย่างการใช้งาน)
# ---------------------------------------------------------
user_query = st.text_input("พิมพ์โจทย์คณิตศาสตร์ตรงนี้...")

if st.button("ส่งคำถาม", type="primary"):
    if user_query.strip():
        with st.spinner("Gemini กำลังวิเคราะห์โจทย์..."):
            output = generate_response(user_query)
            if output:
                st.markdown("### 📝 คำตอบและวิธีทำ:")
                st.write(output)
