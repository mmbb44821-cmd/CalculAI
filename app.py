import streamlit as st
import google.generativeai as genai

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="CalculAI - ผู้ช่วยคณิตศาสตร์",
    page_icon="⚡",
    layout="wide"
)

# ดึง API Key จาก Secrets หลังบ้านก่อน (ถ้ามี)
api_key = st.secrets.get("GEMINI_API_KEY", "")

# แถบด้านข้าง (Sidebar) สำหรับจัดการ API Key
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

# ตรวจสอบ API Key ก่อนเริ่มทำงาน
if not api_key:
    st.warning("⚠️ กรุณาระบุ Gemini API Key ในแถบด้านข้างก่อนใช้งานครับ")
    st.stop()

# กำหนดค่าการเชื่อมต่อ API
genai.configure(api_key=api_key)

# เรียกใช้โมเดล Gemini รุ่นอัปเดต
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"ไม่สามารถโหลดโมเดลได้: {e}")

# แท็บตัวเลือกการใช้งาน
tab1, tab2, tab3 = st.tabs([
    "💬 แชทถาม-ตอบ & แก้โจทย์", 
    "🎯 เครื่องมือสร้างโจทย์ (ตามระดับ/เรื่อง)", 
    "🪄 สร้างโจทย์ด้วยพรอมต์อิสระ"
])

with tab1:
    st.write("💡 **ลองกดถามโจทย์ตัวอย่าง:**")
    col1, col2, col3 = st.columns(3)
    
    prompt_input = ""
    if col1.button("📐 แก้สมการ: 4x + 12 = 36"):
        prompt_input = "ช่วยแก้สมการ 4x + 12 = 36 แสดงวิธีทำอย่างละเอียด"
    if col2.button("📊 หาอนุพันธ์: f(x) = 3x² + 5x - 2"):
        prompt_input = "ช่วยหาอนุพันธ์ของ f(x) = 3x² + 5x - 2 พร้อมอธิบายสเต็ป"
    if col3.button("🍕 โจทย์ปัญหาเศษส่วน ป.5"):
        prompt_input = "แต่งโจทย์ปัญหาเรื่องการบวกเศษส่วนสำหรับนักเรียน ป.5 พร้อมเฉลย"

    user_query = st.text_input("พิมพ์โจทย์คณิตศาสตร์ตรงนี้... (เช่น หาพื้นที่สามเหลี่ยมฐาน 10 สูง 5)", value=prompt_input)
    
    if st.button("ส่งคำถาม", type="primary") or user_query:
        if user_query:
            with st.spinner("กำลังคิดหาคำตอบ..."):
                try:
                    response = model.generate_content(user_query)
                    st.markdown("### 📝 คำตอบและวิธีทำ:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
