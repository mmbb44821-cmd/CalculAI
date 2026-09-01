import math
import re
import streamlit as st  # type: ignore[import-not-found]
import streamlit.components.v1 as components
from openai import OpenAI

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="CalculAI - ผู้ช่วยคณิตศาสตร์",
    page_icon="⚡",
    layout="wide"
)

# =========================================================
# CLIENT-SIDE CALCULATOR (browser only)
# =========================================================
def render_calculator():
    calc_html = """
    <style>
        body { margin: 0; }
        .calc-shell {
            background: #111827;
            border-radius: 16px;
            padding: 14px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 20px rgba(0,0,0,0.18);
        }
        .calc-display {
            width: 100%;
            background: #0f172a;
            color: white;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px 10px;
            font-size: 1.1rem;
            text-align: right;
            margin-bottom: 12px;
        }
        .calc-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px;
        }
        .calc-btn {
            border: none;
            border-radius: 10px;
            padding: 12px 8px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            background: #1f2937;
            color: white;
        }
        .calc-btn.operator { background: #374151; }
        .calc-btn.primary { background: #2563eb; }
        .calc-btn:hover { filter: brightness(1.08); }
    </style>
    <div class="calc-shell">
        <input id="calc-display" class="calc-display" value="" readonly />
        <div class="calc-grid">
            <button class="calc-btn operator" data-action="clear">C</button>
            <button class="calc-btn operator" data-action="backspace">⌫</button>
            <button class="calc-btn" data-action="append" data-value="(">(</button>
            <button class="calc-btn" data-action="append" data-value=")">)</button>

            <button class="calc-btn" data-action="append" data-value="|">|x|</button>
            <button class="calc-btn" data-action="append" data-value="!">n!</button>
            <button class="calc-btn" data-action="append" data-value="√(">√</button>
            <button class="calc-btn operator" data-action="append" data-value="÷">÷</button>

            <button class="calc-btn" data-action="append" data-value="7">7</button>
            <button class="calc-btn" data-action="append" data-value="8">8</button>
            <button class="calc-btn" data-action="append" data-value="9">9</button>
            <button class="calc-btn operator" data-action="append" data-value="×">×</button>

            <button class="calc-btn" data-action="append" data-value="4">4</button>
            <button class="calc-btn" data-action="append" data-value="5">5</button>
            <button class="calc-btn" data-action="append" data-value="6">6</button>
            <button class="calc-btn operator" data-action="append" data-value="-">-</button>

            <button class="calc-btn" data-action="append" data-value="1">1</button>
            <button class="calc-btn" data-action="append" data-value="2">2</button>
            <button class="calc-btn" data-action="append" data-value="3">3</button>
            <button class="calc-btn operator" data-action="append" data-value="+">+</button>

            <button class="calc-btn" data-action="append" data-value="0">0</button>
            <button class="calc-btn" data-action="append" data-value=".">.</button>
            <button class="calc-btn" data-action="append" data-value="%">%</button>
            <button class="calc-btn operator" data-action="append" data-value="**">^</button>

            <button class="calc-btn primary" style="grid-column: span 4;" data-action="calculate">=</button>
        </div>
    </div>
    <script>
        const display = document.getElementById('calc-display');
        let expr = '';

        const factorial = (n) => {
            let result = 1;
            for (let i = 2; i <= n; i += 1) result *= i;
            return result;
        };

        function setDisplay(value) {
            display.value = value;
            expr = value;
        }

        function appendValue(value) {
            expr += value;
            display.value = expr;
        }

        function clearValue() {
            expr = '';
            display.value = '';
        }

        function backspaceValue() {
            expr = expr.slice(0, -1);
            display.value = expr;
        }

        function normalizeExpression(input) {
            let safeExpr = input.replace(/×/g, '*').replace(/÷/g, '/');
            safeExpr = safeExpr.replace(/√/g, 'sqrt');
            safeExpr = safeExpr.replace(/Math\.sqrt\(/g, 'sqrt(');
            safeExpr = safeExpr.replace(/sqrt\s*\(/g, 'Math.sqrt(');
            safeExpr = safeExpr.replace(/%/g, '/100');
            safeExpr = safeExpr.replace(/(\d+)!/g, (_, n) => `factorial(${n})`);
            safeExpr = safeExpr.replace(/\|([^|]+)\|/g, (_, value) => `Math.abs(${value})`);

            const openParen = (safeExpr.match(/\(/g) || []).length;
            const closeParen = (safeExpr.match(/\)/g) || []).length;
            if (openParen > closeParen) {
                safeExpr += ')'.repeat(openParen - closeParen);
            }

            return safeExpr;
        }

        function calculateValue() {
            if (!expr) return;
            try {
                const safeExpr = normalizeExpression(expr);
                const result = Function('factorial', 'Math', `return (${safeExpr});`)(factorial, Math);
                const finalValue = Number.isInteger(result) ? result : Number(result.toFixed(10));
                setDisplay(String(finalValue));
            } catch (error) {
                setDisplay('Error');
            }
        }

        document.querySelectorAll('.calc-btn').forEach((button) => {
            button.addEventListener('click', () => {
                const action = button.dataset.action;
                const value = button.dataset.value || '';

                if (action === 'append') appendValue(value);
                if (action === 'clear') clearValue();
                if (action === 'backspace') backspaceValue();
                if (action === 'calculate') calculateValue();
            });
        });
    </script>
    """

    with st.sidebar:
        st.header("🧮 เครื่องคิดเลข")
        st.caption("Client-side calculator: กดแล้วคำนวณทันทีบนเว็บ")
        components.html(calc_html, height=500, scrolling=False)

    return "client-side"


render_calculator()

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
