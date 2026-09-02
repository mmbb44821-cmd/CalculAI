import time
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="CalculAI - ผู้ช่วยคณิตศาสตร์",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# GLOBAL STYLES
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Kanit', system-ui, sans-serif;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background: radial-gradient(circle at 10% 0%, #1b1035 0%, #0b0f24 45%, #05070f 100%);
    }

    /* Hero header */
    .hero-wrap {
        background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(37,99,235,0.18));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 28px 32px;
        margin-bottom: 22px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.35);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin: 0;
    }
    .hero-sub {
        color: #cbd5e1;
        font-size: 1.02rem;
        margin-top: 6px;
        font-weight: 300;
    }
    .hero-badges { margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap; }
    .badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 500;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        color: #e2e8f0;
    }

    /* Section / glass cards */
    .glass-card {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 16px;
        backdrop-filter: blur(6px);
    }

    /* Answer box */
    .answer-box {
        background: linear-gradient(135deg, rgba(52,211,153,0.10), rgba(96,165,250,0.08));
        border: 1px solid rgba(52,211,153,0.28);
        border-radius: 16px;
        padding: 20px 22px;
        margin-top: 14px;
    }
    .answer-label {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-weight: 600;
        color: #34d399;
        font-size: 0.95rem;
        margin-bottom: 10px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255,255,255,0.03);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 500;
        font-size: 0.95rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.04);
        color: #e2e8f0;
        font-weight: 500;
        padding: 8px 16px;
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        border-color: #7c3aed;
        color: #c4b5fd;
        transform: translateY(-1px);
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #2563eb);
        border: none;
        color: white;
        box-shadow: 0 6px 18px rgba(124,58,237,0.35);
    }
    .stButton>button[kind="primary"]:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12081f 0%, #0a0e1c 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    .example-caption {
        color: #94a3b8;
        font-size: 0.88rem;
        margin-bottom: 6px;
        font-weight: 300;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CLIENT-SIDE CALCULATOR (browser only)
# =========================================================
def render_calculator():
    calc_html = """
    <style>
        body { margin: 0; font-family: 'Kanit', system-ui, sans-serif; }
        .calc-shell {
            background: linear-gradient(160deg, #16112b, #0d0f1f);
            border-radius: 18px;
            padding: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 24px rgba(0,0,0,0.35);
            max-width: 330px;
            margin: 0 auto;
        }
        .calc-display {
            width: 100%;
            background: #05070f;
            color: #f8fafc;
            border: 1px solid rgba(124,58,237,0.35);
            border-radius: 12px;
            padding: 14px 16px;
            font-size: 1.35rem;
            text-align: right;
            margin-bottom: 14px;
            box-sizing: border-box;
            min-height: 56px;
            outline: none;
            font-family: 'Kanit', monospace;
        }
        .calc-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px;
        }
        .calc-btn {
            border: none;
            border-radius: 12px;
            padding: 13px 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            background: rgba(255,255,255,0.06);
            color: #e2e8f0;
            transition: background 0.15s, transform 0.08s;
        }
        .calc-btn.operator { background: rgba(124,58,237,0.25); color: #c4b5fd; }
        .calc-btn.primary {
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            color: white;
            box-shadow: 0 6px 16px rgba(124,58,237,0.4);
        }
        .calc-btn:hover { filter: brightness(1.2); }
        .calc-btn:active { transform: scale(0.94); }
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
            safeExpr = safeExpr.replace(/√\\(/g, 'Math.sqrt(');
            safeExpr = safeExpr.replace(/%/g, '/100');
            safeExpr = safeExpr.replace(/(\\d+)!/g, (_, n) => `factorial(${n})`);
            safeExpr = safeExpr.replace(/\\|([^|]+)\\|/g, (_, val) => `Math.abs(${val})`);

            const openParen = (safeExpr.match(/\\(/g) || []).length;
            const closeParen = (safeExpr.match(/\\)/g) || []).length;
            if (openParen > closeParen) {
                safeExpr += ')'.repeat(openParen - closeParen);
            }

            return safeExpr;
        }

        function calculateValue() {
            if (!expr) return;
            try {
                const safeExpr = normalizeExpression(expr);

                if (/[^0-9\\+\\-\\*\\/\\%\\.\\(\\)\\,\\sMathsqrtabsfactorial]/.test(safeExpr.replace(/factorial|Math\\.sqrt|Math\\.abs/g, ''))) {
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
        st.markdown("### 🧮 เครื่องคิดเลข")
        st.caption("คำนวณด่วน ๆ ระหว่างทำโจทย์ (ทำงานในเบราว์เซอร์ล้วน)")
        components.html(calc_html, height=540, scrolling=False)

    return "client-side"

render_calculator()

# =========================================================
# HERO HEADER
# =========================================================
st.markdown("""
<div class="hero-wrap">
    <p class="hero-title">⚡ CalculAI</p>
    <p class="hero-sub">ผู้ช่วยแก้โจทย์ &amp; เครื่องมือสร้างข้อสอบคณิตศาสตร์อัจฉริยะ ตั้งแต่ระดับ ป.1 ถึง ม.6</p>
    <div class="hero-badges">
        <span class="badge">🤖 Powered by Google Gemini</span>
        <span class="badge">📐 แก้โจทย์ทีละขั้นตอน</span>
        <span class="badge">🎯 สร้างข้อสอบอัตโนมัติ</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ดึง Gemini API Key จาก Streamlit Secrets หรือช่องกรอก
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        api_key = st.text_input("🔑 ไม่พบ API Key ใน Secrets กรุณาใส่ Google Gemini API Key:", type="password")
        st.markdown('</div>', unsafe_allow_html=True)

if not api_key:
    st.warning("⚠️ กรุณาระบุ Google Gemini API Key ก่อนใช้งานระบบ AI ครับ")
    st.stop()

# เชื่อมต่อ Client ไปยัง Google Gemini API
client = genai.Client(api_key=api_key)


# โมเดลที่ต้องการใช้เป็นอันดับแรก (ถ้ามีอยู่จริงในรายชื่อที่ API คืนมา)
PREFERRED_MODEL_ORDER = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]

MAX_RETRIES_PER_MODEL = 3       # จำนวนครั้งที่ลองใหม่ต่อโมเดล เมื่อเจอ 503 (โหลดสูงชั่วคราว)
RETRY_DELAY_SECONDS = 3         # เวลาหน่วงก่อนลองใหม่ (วินาที) - เพิ่มขึ้นทุกครั้งที่ retry (backoff)


@st.cache_data(ttl=3600, show_spinner=False)
def get_available_models(_client):
    """
    ดึงรายชื่อโมเดลที่ใช้งานได้จริงจาก Gemini API ณ ขณะนี้ (ไม่ hardcode)
    เพื่อให้แอปปรับตัวอัตโนมัติเมื่อ Google เปลี่ยน/ปิดโมเดล
    คืนค่าเป็น list ของชื่อโมเดลที่รองรับ generateContent
    """
    try:
        models = _client.models.list()
        names = []
        for m in models:
            actions = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", None) or []
            model_name = m.name.replace("models/", "") if hasattr(m, "name") else str(m)
            # ถ้าไม่มีข้อมูล action ให้เก็บไว้ก่อน (บาง SDK version ไม่คืนฟิลด์นี้)
            if not actions or "generateContent" in actions:
                names.append(model_name)
        return names
    except Exception:
        return []


def build_model_priority_list(client_instance):
    """
    รวมโมเดลที่ต้องการ (PREFERRED_MODEL_ORDER) เข้ากับรายชื่อโมเดลจริงที่ API มีให้
    ลำดับ: โมเดลที่ต้องการก่อน (ถ้ามีจริง) -> ตามด้วยโมเดล flash อื่นๆ ที่เหลือ (กันเหนียว)
    """
    available = get_available_models(client_instance)

    if not available:
        # ถ้าดึงรายชื่อไม่ได้ (เช่น เน็ตมีปัญหา) ให้ fallback ไปใช้ลิสต์ที่กำหนดไว้ตรงๆ
        return PREFERRED_MODEL_ORDER

    ordered = [m for m in PREFERRED_MODEL_ORDER if m in available]
    extras = [m for m in available if "flash" in m.lower() and m not in ordered]
    result = ordered + extras
    return result if result else available


def generate_response(prompt_text):
    last_error = None
    model_list = build_model_priority_list(client)

    for model_name in model_list:
        for attempt in range(1, MAX_RETRIES_PER_MODEL + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                    config=types.GenerateContentConfig(
                        system_instruction="คุณคือครูสอนคณิตศาสตร์อัจฉริยะ แสดงวิธีทำและอธิบายขั้นตอนการแก้โจทย์อย่างเป็นระบบ เข้าใจง่าย",
                        temperature=0.3,
                    )
                )
                return response.text
            except Exception as e:
                last_error = e
                error_text = str(e)

                # 404 = โมเดลนี้ถูกปิด/ไม่มีแล้ว -> ข้ามไปโมเดลถัดไปทันที ไม่ต้อง retry ซ้ำ
                if "404" in error_text or "NOT_FOUND" in error_text:
                    break

                # 503 = โหลดสูงชั่วคราว -> รอสักครู่ (เพิ่มเวลารอทุกครั้ง) แล้วลองโมเดลเดิมใหม่
                if "503" in error_text or "UNAVAILABLE" in error_text:
                    if attempt < MAX_RETRIES_PER_MODEL:
                        time.sleep(RETRY_DELAY_SECONDS * attempt)
                        continue
                    else:
                        break

                # ข้อผิดพลาดประเภทอื่น (เช่น API key ผิด) -> ไม่มีประโยชน์ที่จะลองโมเดลอื่น
                st.error(f"เกิดข้อผิดพลาดในการเรียกใช้ Gemini API: {e}")
                return None

    st.error(
        f"ไม่สามารถเรียกใช้ Gemini API ได้ในขณะนี้ (ลองครบทุกโมเดลที่มีแล้ว): {last_error}\n\n"
        "สาเหตุที่เป็นไปได้: บัญชี/API key นี้อาจยังไม่รองรับโมเดลรุ่นล่าสุด "
        "ลองตรวจสอบสิทธิ์การใช้งานที่ Google AI Studio หรือสร้าง API key ใหม่"
    )
    return None

with st.sidebar:
    st.markdown("---")
    with st.expander("🔍 ตรวจสอบโมเดล (debug)"):
        if st.button("↻ ดึงรายชื่อโมเดลล่าสุด"):
            st.cache_data.clear()
        _available_models = get_available_models(client)
        if _available_models:
            st.caption("โมเดลที่ API key นี้เข้าถึงได้:")
            st.code("\n".join(_available_models))
        else:
            st.caption("ไม่สามารถดึงรายชื่อโมเดลได้ในขณะนี้ (จะใช้รายชื่อสำรองที่ตั้งไว้ในโค้ดแทน)")

# แท็บตัวเลือกการใช้งาน AI
tab1, tab2, tab3 = st.tabs([
    "💬  แชทถาม-ตอบ & แก้โจทย์",
    "🎯  สร้างโจทย์ (ตามระดับ/เรื่อง)",
    "🪄  สร้างโจทย์ด้วยพรอมต์อิสระ",
])

# TAB 1: CHAT & SOLVER
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p class="example-caption">💡 ลองกดถามโจทย์ตัวอย่าง</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""

    if col1.button("📐 แก้สมการ: 4x + 12 = 36", use_container_width=True):
        st.session_state.chat_input = "ช่วยแก้สมการ 4x + 12 = 36 แสดงวิธีทำอย่างละเอียด"
    if col2.button("📊 หาอนุพันธ์: f(x) = 3x² + 5x - 2", use_container_width=True):
        st.session_state.chat_input = "ช่วยหาอนุพันธ์ของ f(x) = 3x² + 5x - 2 พร้อมอธิบายสเต็ป"
    if col3.button("🍕 โจทย์ปัญหาเศษส่วน ป.5", use_container_width=True):
        st.session_state.chat_input = "แม่มีเงิน 2,500 บาท ซื้อของไป 3/5 ของเงินทั้งหมด แม่เหลือเงินกี่บาท?"

    st.markdown("<br>", unsafe_allow_html=True)
    user_query = st.text_input("✏️ พิมพ์โจทย์คณิตศาสตร์ตรงนี้...", key="chat_input")
    send_clicked = st.button("🚀 ส่งคำถาม", type="primary", key="btn_chat")
    st.markdown('</div>', unsafe_allow_html=True)

    if send_clicked:
        if user_query.strip():
            with st.spinner("Gemini กำลังประมวลผลคำตอบ..."):
                output = generate_response(user_query)
                if output:
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown('<div class="answer-label">📝 คำตอบและวิธีทำ</div>', unsafe_allow_html=True)
                    st.write(output)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("กรุณากรอกโจทย์คณิตศาสตร์ก่อนส่งคำถามครับ")

# TAB 2: STRUCTURED GENERATOR
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🎯 เครื่องมือออกข้อสอบและแบบฝึกหัด")
    col_g, col_d = st.columns(2)
    with col_g:
        grade = st.selectbox("🎓 เลือกระดับชั้น:", [f"ป.{i}" for i in range(1, 7)] + [f"ม.{i}" for i in range(1, 7)])
        num_q = st.slider("🔢 จำนวนโจทย์ (ข้อ):", 1, 10, 3)
    with col_d:
        topic = st.text_input("📚 บทเรียน/เรื่องที่ต้องการ:", placeholder="เช่น สมการ, เวกเตอร์, เศษส่วน")
        show_sol = st.checkbox("✅ รวมเฉลยละเอียด", value=True)

    gen_clicked = st.button("🚀 สร้างโจทย์เลย!", use_container_width=True, type="primary", key="btn_tab2")
    st.markdown('</div>', unsafe_allow_html=True)

    if gen_clicked:
        if not topic.strip():
            st.warning("กรุณากรอกเรื่องที่ต้องการสร้างโจทย์ก่อนครับ")
        else:
            prompt_t2 = f"สร้างโจทย์คณิตศาสตร์ ระดับ {grade} เรื่อง {topic} จำนวน {num_q} ข้อ {'พร้อมเฉลยละเอียด' if show_sol else 'ไม่ต้องมีเฉลย'}"
            with st.spinner("Gemini กำลังสร้างชุดโจทย์..."):
                output = generate_response(prompt_t2)
                if output:
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown('<div class="answer-label">📝 ชุดโจทย์ที่สร้างขึ้น</div>', unsafe_allow_html=True)
                    st.write(output)
                    st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: CUSTOM PROMPT GENERATOR
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 🪄 สั่งสร้างโจทย์ด้วยคำสั่งอิสระ")
    custom_p = st.text_area("✍️ พิมพ์คำสั่งสร้างโจทย์ที่ต้องการ:", height=120, placeholder="เช่น ออกโจทย์คณิตตลกร้าย 1 ข้อ เรื่องการคำนวณภาษี พร้อมวิธีคิด")
    custom_clicked = st.button("✨ สร้างโจทย์ตามสั่ง", use_container_width=True, type="primary", key="btn_tab3")
    st.markdown('</div>', unsafe_allow_html=True)

    if custom_clicked:
        if not custom_p.strip():
            st.warning("กรุณากรอกคำสั่งก่อนครับ")
        else:
            with st.spinner("Gemini กำลังสร้างโจทย์ตามสั่ง..."):
                output = generate_response(custom_p)
                if output:
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown('<div class="answer-label">📝 ผลลัพธ์</div>', unsafe_allow_html=True)
                    st.write(output)
                    st.markdown('</div>', unsafe_allow_html=True)
