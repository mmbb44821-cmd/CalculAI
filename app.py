import math
import re
import streamlit as st
from openai import OpenAI

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="CalculAI - ผู้ช่วยคณิตศาสตร์",
    page_icon="⚡",
    layout="wide"
)

# =========================================================
# SYSTEM & CALCULATOR FUNCTIONS
# =========================================================
if "calc_expr" not in st.session_state:
    st.session_state.calc_expr = ""

def sync_input():
    st.session_state.calc_expr = st.session_state.calc_input_key

def calc_append(val):
    st.session_state.calc_expr += str(val)
    st.session_state.calc_input_key = st.session_state.calc_expr

def calc_backspace():
    st.session_state.calc_expr = st.session_state.calc_expr[:-1]
    st.session_state.calc_input_key = st.session_state.calc_expr

def calc_clear():
    st.session_state.calc_expr = ""
    st.session_state.calc_input_key = ""

def calc_eval():
    expr = st.session_state.calc_expr
    if not expr:
        return
    try:
        # แปลงสัญลักษณ์เป็นไวยากรณ์ Python
        safe_expr = expr.replace("×", "*").replace("÷", "/")
        safe_expr = safe_expr.replace("%", "/100")

        # จัดการ Factorial (n!) เช่น 5! -> math.factorial(5)
        safe_expr = re.sub(r'(\d+)!', r'math.factorial(\1)', safe_expr)
        # จัดการ Absolute Value |x| -> abs(x)
        safe_expr = re.sub(r'\|([^|]+)\|', r'abs(\1)', safe_expr)

        # นิยามฟังก์ชันปลอดภัยสำหรับ eval
        allowed_globals = {"__builtins__": None, "math": math, "abs": abs}
        res = eval(safe_expr, allowed_globals)

        # จัดการแสดงผลตัวเลข
        if isinstance(res, float) and res.is_integer():
            res = int(res)
        st.session_state.calc_expr = str(res)
        st.session_state.calc_input_key = str(res)
    except Exception:
        st.session_state.calc_expr = "Error"
        st.session_state.calc_input_key = "Error"

# =========================================================
# SIDEBAR: CALCULATOR
# =========================================================
with st.sidebar:
    st.header("🧮 เครื่องคิดเลข")
    
    # ช่องพิมพ์ (รองรับทั้งการพิมพ์คีย์บอร์ดและการกดปุ่ม)
    st.text_input(
        "หน้าจอคำนวณ", 
        value=st.session_state.calc_expr, 
        key="calc_input_key",
        on_change=sync_input
    )

    # ปุ่มกดเครื่องคิดเลข
    c1, c2, c3, c4 = st.columns(4)
    c1.button("C", use_container_width=True, on_click=calc_clear)
    c2.button("⌫", use_container_width=True, on_click=calc_backspace)
    c3.button("(", use_container_width=True, on_click=calc_append, args=("(",))
    c4.button(")", use_container_width=True, on_click=calc_append, args=(")",))

    c1, c2, c3, c4 = st.columns(4)
    c1.button("|x|", use_container_width=True, on_click=calc_append, args=("|",))
    c2.button("n!", use_container_width=True, on_click=calc_append, args=("!",))
    c3.button("√", use_container_width=True, on_click=calc_append, args=("math.sqrt(",))
    c4.button("÷", use_container_width=True, on_click=calc_append, args=("÷",))

    c1, c2, c3, c4 = st.columns(4)
    c1.button("7", use_container_width=True, on_click=calc_append, args=("7",))
    c2.button("8", use_container_width=True, on_click=calc_append, args=("8",))
    c3.button("9", use_container_width=True, on_click=calc_append, args=("9",))
    c4.button("×", use_container_width=True, on_click=calc_append, args=("×",))

    c1, c2, c3, c4 = st.columns(4)
    c1.button("4", use_container_width=True, on_click=calc_append, args=("4",))
    c2.button("5", use_container_width=True, on_click=calc_append, args=("5",))
    c3.button("6", use_container_width=True, on_click=calc_append, args=("6",))
    c4.button("-", use_container_width=True, on_click=calc_append, args=("-",))

    c1, c2, c3, c4 = st.columns(4)
    c1.button("1", use_container_width=True, on_click=calc_append, args=("1",))
    c2.button("2", use_container_width=True, on_click=calc_append, args=("2",))
    c3.button("3", use_container_width=True, on_click=calc_append, args=("3",))
    c4.button("+", use_container_width=True, on_click=calc_append, args=("+",))

    c1, c2, c3, c4 = st.columns(4)
    c1.button("0", use_container_width=True, on_click=calc_append, args=("0",))
    c2.button(".", use_container_width=True, on_click=calc_append, args=(".",))
    c3.button("%", use_container_width=True, on_click=calc_append, args=("%",))
    c4.button("^", use_container_width=True, on_click=calc_append, args=("**",))

    st.button("=", type="primary", use_container_width=True, on_click=calc_eval)

    st.markdown("---")
    st.caption("💡 **วิธีใช้ปุ่มพิเศษ:**")
    st.caption("• **|x|** : ใส่ค่าสัมบูรณ์ เช่น `|-5|` -> 5")
    st.caption("• **√** : กดปุ่ม `√` แล้วพิมพ์ตัวเลขพร้อมปิดวงเล็บ")
    st.caption("• **^** : คือยกกำลัง เช่น `2**3` -> 8")

# =========================================================
# MAIN CONTENT: AI CALCULAI (Ox Alpha System)
# =========================================================
st.title("⚡ CalculAI (Powered by Ox Alpha)")
st.subheader("ผู้ช่วยแก้โจทย์ & เครื่องมือสร้างข้อสอบคณิตศาสตร์อัจฉริยะ (ป.1 - ม.6)")

# ดึง OpenRouter API Key จาก Secrets
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

if not api_key:
    api_key = st.text_input("🔑 ไม่พบ API Key ใน Secrets กรุณาใส่ OpenRouter API Key:", type="password")

if not api_key:
    st.warning("⚠️ กรุณาระบุ OpenRouter API Key ก่อนใช้งานระบบ AI ครับ")
    st.stop()

# เชื่อมต่อ Client ไปยัง OpenRouter API
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def generate_response(prompt_text):
    try:
        response = client.chat.completions.create(
            model="stealth/ox-alpha",
            messages=[
                {
                    "role": "system",
                    "content": "คุณคือครูสอนคณิตศาสตร์อัจฉริยะ แสดงวิธีทำและอธิบายขั้นตอนการแก้โจทย์อย่างเป็นระบบ เข้าใจง่าย"
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเรียกใช้ API: {e}")
        return None

# แท็บตัวเลือกการใช้งาน AI
tab1, tab2, tab3 = st.tabs([
    "💬 แชทถาม-ตอบ & แก้โจทย์", 
    "🎯 เครื่องมือสร้างโจทย์ (ตามระดับ/เรื่อง)", 
    "🪄 สร้างโจทย์ด้วยพรอมต์อิสระ"
])

# TAB 1: CHAT & SOLVER
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
            with st.spinner("Ox Alpha กำลังประมวลผลคำตอบ..."):
                output = generate_response(user_query)
                if output:
                    st.markdown("### 📝 คำตอบและวิธีทำ:")
                    st.write(output)

# TAB 2: STRUCTURED GENERATOR
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
            with st.spinner("Ox Alpha กำลังสร้างชุดโจทย์..."):
                output = generate_response(prompt_t2)
                if output:
                    st.markdown("---")
                    st.write(output)

# TAB 3: CUSTOM PROMPT GENERATOR
with tab3:
    st.markdown("### 🪄 สั่งสร้างโจทย์ด้วยคำสั่งอิสระ")
    custom_p = st.text_area("✍️ พิมพ์คำสั่งสร้างโจทย์ที่ต้องการ:", height=120, placeholder="เช่น ออกโจทย์คณิตตลกร้าย 1 ข้อ เรื่องการคำนวณภาษี พร้อมวิธีคิด")
    if st.button("✨ สร้างโจทย์ตามสั่ง", use_container_width=True, key="btn_tab3"):
        if not custom_p.strip():
            st.warning("กรุณากรอกคำสั่งก่อนครับ")
        else:
            with st.spinner("Ox Alpha กำลังสร้างโจทย์ตามสั่ง..."):
                output = generate_response(custom_p)
                if output:
                    st.markdown("---")
                    st.write(output)
