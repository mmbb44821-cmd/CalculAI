import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

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
        body { margin: 0; font-family: system-ui, -apple-system, sans-serif; }
        .calc-shell {
            background: #111827;
            border-radius: 16px;
            padding: 14px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 20px rgba(0,0,0,0.18);
            max-width: 330px;
            margin: 0 auto;
        }
        .calc-display {
            width: 100%;
            background: #0f172a;
            color: #f8fafc;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 12px 14px;
            font-size: 1.2rem;
            text-align: right;
            margin-bottom: 12px;
            box-sizing: border-box;
            min-height: 52px;
            outline: none;
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
            transition: background 0.2s, transform 0.1s;
        }
        .calc-btn.operator { background: #374151; }
        .calc-btn.primary { background: #2563eb; }
        .calc-btn:hover { filter: brightness(1.15); }
        .calc-btn:active { transform: scale(0.96); }
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
            if (n < 0) return NaN;
            if (n === 0 || n === 1) return 1;
            let result = 1;
            for (let i = 2; i <= n; i += 1) result *= i;
            return result;
        };

        function setDisplay(value) {
            display.value = value;
            expr = value === 'Error' ? '' : value;
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
            safeExpr = safeExpr.replace(/√\(/g, 'Math.sqrt(');
            safeExpr = safeExpr.replace(/%/g, '/100');
            safeExpr = safeExpr.replace(/(\d+)!/g, (_, n) => `factorial(${n})`);
            safeExpr = safeExpr.replace(/\|([^|]+)\|/g, (_, val) => `Math.abs(${val})`);

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
                
                if (/[^0-9\+\-\*\/\%\.\(\)\,\sMathsqrtabsfactorial]/.test(safeExpr.replace(/factorial|Math\.sqrt|Math\.abs/g, ''))) {
                    throw new Error("Invalid characters detected");
                }

                const result = Function('factorial', 'Math', `return (${safeExpr});`)(factorial, Math);
                
                if (!isFinite(result) || isNaN(result)) {
                    setDisplay('Error');
                    return;
                }

                const finalValue = Number.isInteger(result) ? result : Number(result.toFixed(8));
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
        components.html(calc_html, height=520, scrolling=False)

    return "client-side"

render_calculator()

# =========================================================
# MAIN CONTENT: AI CALCULAI (Google Gemini)
# =========================================================
st.title("⚡ CalculAI (Powered by Google Gemini)")
st.subheader("ผู้ช่วยแก้โจทย์ & เครื่องมือสร้างข้อสอบคณิตศาสตร์อัจฉริยะ (ป.1 - ม.6)")

# ดึง Gemini API Key จาก Streamlit Secrets หรือช่องกรอก
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    api_key = st.text_input("🔑 ไม่พบ API Key ใน Secrets กรุณาใส่ Google Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ กรุณาระบุ Google Gemini API Key ก่อนใช้งานระบบ AI ครับ")
    st.stop()

# เชื่อมต่อ Client ไปยัง Google Gemini API
client = genai.Client(api_key=api_key)

def generate_response(prompt_text):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction="คุณคือครูสอนคณิตศาสตร์อัจฉริยะ แสดงวิธีทำและอธิบายขั้นตอนการแก้โจทย์อย่างเป็นระบบ เข้าใจง่าย",
                temperature=0.3,
            )
        )
        return response.text
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเรียกใช้ Gemini API: {e}")
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
    
    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""

    if col1.button("📐 แก้สมการ: 4x + 12 = 36"):
        st.session_state.chat_input = "ช่วยแก้สมการ 4x + 12 = 36 แสดงวิธีทำอย่างละเอียด"
    if col2.button("📊 หาอนุพันธ์: f(x) = 3x² + 5x - 2"):
        st.session_state.chat_input = "ช่วยหาอนุพันธ์ของ f(x) = 3x² + 5x - 2 พร้อมอธิบายสเต็ป"
    if col3.button("🍕 โจทย์ปัญหาเศษส่วน ป.5"):
        st.session_state.chat_input = "แม่มีเงิน 2,500 บาท ซื้อของไป 3/5 ของเงินทั้งหมด แม่เหลือเงินกี่บาท?"

    user_query = st.text_input("พิมพ์โจทย์คณิตศาสตร์ตรงนี้...", key="chat_input")
    
    if st.button("ส่งคำถาม", type="primary", key="btn_chat"):
        if user_query.strip():
            with st.spinner("Gemini กำลังประมวลผลคำตอบ..."):
                output = generate_response(user_query)
                if output:
                    st.markdown("### 📝 คำตอบและวิธีทำ:")
                    st.write(output)
        else:
                    st.warning("กรุณากรอกโจทย์คณิตศาสตร์ก่อนส่งคำถามครับ")

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
            with st.spinner("Gemini กำลังสร้างชุดโจทย์..."):
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
            with st.spinner("Gemini กำลังสร้างโจทย์ตามสั่ง..."):
                output = generate_response(custom_p)
                if output:
                    st.markdown("---")
                    st.write(output)
