with st.sidebar:
    st.header("🧮 เครื่องคิดเลข")
    
    # อนุญาตให้พิมพ์จากคีย์บอร์ดได้โดยเอา disabled=True ออก
    calc_input = st.text_input(
        "หน้าจอคำนวณ (พิมพ์หรือกดปุ่มได้)", 
        value=st.session_state.calc_expr, 
        key="calc_display"
    )
    # อัปเดตค่าใน session_state ถ้ามีการพิมพ์ผ่านคีย์บอร์ด
    st.session_state.calc_expr = calc_input

    # ปุ่มกดเครื่องคิดเลข
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("C", use_container_width=True): calc_clear()
    if c2.button("⌫", use_container_width=True): calc_backspace()
    if c3.button("(", use_container_width=True): calc_append("(")
    if c4.button(")", use_container_width=True): calc_append(")")

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("|x|", use_container_width=True): calc_append("|")
    if c2.button("n!", use_container_width=True): calc_append("!")
    if c3.button("√", use_container_width=True): calc_append("math.sqrt(")
    if c4.button("÷", use_container_width=True): calc_append("÷")

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("7", use_container_width=True): calc_append("7")
    if c2.button("8", use_container_width=True): calc_append("8")
    if c3.button("9", use_container_width=True): calc_append("9")
    if c4.button("×", use_container_width=True): calc_append("×")

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("4", use_container_width=True): calc_append("4")
    if c2.button("5", use_container_width=True): calc_append("5")
    if c3.button("6", use_container_width=True): calc_append("6")
    if c4.button("-", use_container_width=True): calc_append("-")

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("1", use_container_width=True): calc_append("1")
    if c2.button("2", use_container_width=True): calc_append("2")
    if c3.button("3", use_container_width=True): calc_append("3")
    if c4.button("+", use_container_width=True): calc_append("+")

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("0", use_container_width=True): calc_append("0")
    if c2.button(".", use_container_width=True): calc_append(".")
    if c3.button("%", use_container_width=True): calc_append("%")
    if c4.button("^", use_container_width=True): calc_append("**")

    if st.button("=", type="primary", use_container_width=True):
        calc_eval()

    st.markdown("---")
    st.caption("💡 ข้อแนะนำการใช้ปุ่มพิเศษ:")
    st.caption("• **|x|** : กดเพื่อเปิด/ปิด เช่น `|-5|` -> 5")
    st.caption("• **√** : พิมพ์ `sqrt(9)` หรือกดปุ่ม `√` แล้วตามด้วยตัวเลขกับวงเล็บปิด")
    st.caption("• **^** : คือการยกกำลัง เช่น `2**3` หรือกดปุ่ม `^` -> 8")
