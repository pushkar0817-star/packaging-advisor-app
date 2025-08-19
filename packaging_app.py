import streamlit as st
import json
import os
import time
from datetime import datetime
import pandas as pd

DB_FILE = "packaging_db.json"
LOG_FILE = "training_log.csv"   # interactions for future ML
MODEL_FILE = "model.pkl"        # reserved for later

# ------------------ Persistence ------------------
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    # ensure schema keys
    data.setdefault("materials", {})
    data.setdefault("category_requirements", {})
    return data

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def log_interaction(row: dict):
    # append (or create) a CSV for ML later
    cols = [
        "timestamp","product_name","product_desc","auto_category","packaging_type",
        "suggested_material","accepted"  # accepted=1 if user clicks accept
    ]
    df = pd.DataFrame([row], columns=cols)
    if os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, mode="a", header=False, index=False, encoding="utf-8")
    else:
        df.to_csv(LOG_FILE, index=False, encoding="utf-8")

# ------------------ App State ------------------
if "db" not in st.session_state:
    st.session_state.db = load_db()

# ------------------ UI Title ------------------
st.markdown("<h1 style='text-align:center;color:#FF6F61;'>✨📦 AI Packaging Advisor (with Memory & ML-ready) ✨</h1>", unsafe_allow_html=True)

# ------------------ Helpers ------------------
def categorize_product(description: str) -> str:
    desc = (description or "").lower()
    if any(w in desc for w in ["food","snack","beverage","drink","fruit","vegetable","flour","grain","oil"]):
        return "Food & Beverages"
    if any(w in desc for w in ["mobile","electronics","gadget","laptop","device","pcb","charger"]):
        return "Electronics"
    if any(w in desc for w in ["bottle","liquid","juice","shampoo","detergent","solvent"]):
        return "Liquids"
    if any(w in desc for w in ["glass","ceramic","fragile","delicate"]):
        return "Fragile Items"
    if any(w in desc for w in ["metal","tools","hardware","machine","component"]):
        return "Industrial Goods"
    return "General Products"

def score_material(material: dict, req: dict, packaging_type: str) -> float:
    """Heuristic scoring now; can be replaced by ML later."""
    score = 0.0
    props = material.get("properties", {})
    level = material.get("level","").lower()
    family = material.get("family","")

    # Align level ↔ packaging_type (Transportation/Export favor secondary/tertiary)
    pt = packaging_type.split(" ")[0].lower()  # "transportation", "storage", "retail", "export"
    if pt in ["retail"]:
        score += 1.0 if level == "primary" else 0.2
    elif pt in ["transportation","export"]:
        score += 1.0 if level in ["secondary","tertiary"] else 0.2
    elif pt in ["storage"]:
        score += 0.6  # neutral

    needs = req.get("needs", {}) if req else {}
    # Barrier needs
    if needs.get("oxygen_sensitive") is True and props.get("otr_ccm2_day") is not None:
        score += max(0, 1.0 - min(props["otr_ccm2_day"]/5.0, 1.0))  # lower OTR → higher score
    if needs.get("moisture_sensitive") is True and props.get("wvtr_g_m2_day") is not None:
        score += max(0, 1.0 - min(props["wvtr_g_m2_day"]/5.0, 1.0)) # lower WVTR → higher score
    if needs.get("light_sensitive") is True:
        lb = props.get("light_barrier","none")
        score += {"none":0.0,"partial":0.5,"high":1.0}.get(lb,0.0)
    if needs.get("fragile") is True:
        cush = props.get("cushioning","none")
        score += {"none":0.0,"low":0.3,"medium":0.7,"high":1.0}.get(cush,0.0)

    # Stack strength for transport/export
    min_stack = req.get("min_stack_strength_n", 0) if req else 0
    if min_stack and props.get("stack_strength_n"):
        score += 1.0 if props["stack_strength_n"] >= min_stack else 0.0
    elif min_stack and family in ["corrugated","pulp","foam"]:
        score += 0.5  # heuristic if unknown but likely supportive

    # Food contact if needed
    if req.get("food_contact") and level == "primary":
        # crude assumption: glass/metal/plastic-bottle/laminate are acceptable for food (customize later)
        score += 0.5 if family in ["glass","metal","plastic-bottle","laminate","film"] else 0.0

    # Recyclability bonus (UX preference)
    rec = props.get("recyclability","moderate")
    score += {"poor":0.0,"moderate":0.2,"good":0.4}.get(rec,0.0)

    return score

def get_category_req(db, category: str):
    return db.get("category_requirements", {}).get(category)

def emoji_for_material(family: str, level: str):
    fam = (family or "").lower()
    lvl = (level or "").lower()
    if fam == "corrugated": return "📦"
    if fam in ["film","laminate"]: return "🎞️"
    if fam == "glass": return "🫙"
    if fam == "metal": return "🥫"
    if fam in ["pulp","foam"]: return "🧽"
    if fam == "plastic-bottle": return "🧴"
    return "🎁"

# ------------------ Layout ------------------
tab_main, tab_teach_mat, tab_teach_cat, tab_db = st.tabs(["Suggest", "Teach Materials", "Teach Categories", "Database"])

# ---------- Suggest tab ----------
with tab_main:
    st.subheader("📝 Product Input")
    product_name = st.text_input("Product Name")
    product_desc = st.text_area("Product Description")
    packaging_type = st.selectbox("Packaging Type", ["Transportation 🚚","Storage 📦","Retail 🛍️","Export 🌍"])

    auto_category = categorize_product(product_desc) if product_desc else None
    if auto_category:
        st.success(f"🔍 Auto-detected category: **{auto_category}**")

    if st.button("🚀 Suggest Packaging"):
        if not product_name or not product_desc:
            st.error("Please enter both product name and description.")
        else:
            st.balloons()
            with st.spinner("Thinking 🤔..."):
                time.sleep(1.2)

            req = get_category_req(st.session_state.db, auto_category or "General Products")
            mats = st.session_state.db.get("materials", {})
            # score all materials
            ranked = []
            for name, mat in mats.items():
                s = score_material(mat, req, packaging_type)
                ranked.append((s, name, mat))
            ranked.sort(reverse=True, key=lambda x: x[0])

            st.subheader("📌 Suggested Packaging")
            st.write(f"**Category:** {auto_category or 'General Products'} | **Use:** {packaging_type}")

            if not ranked:
                st.info("🤖 No structured materials yet. Teach some in the **Teach Materials** tab.")
            else:
                for score, name, mat in ranked[:6]:
                    fam = mat.get("family","")
                    lvl = mat.get("level","")
                    emj = emoji_for_material(fam,lvl)
                    props = mat.get("properties",{})

                    st.markdown(
                        f"{emj} **{name}**  — *{fam} / {lvl}*  \n"
                        f"• Best for: {mat.get('best_for','—')}  \n"
                        f"• Notes: {mat.get('notes','—')}  \n"
                        f"• Barrier: OTR={props.get('otr_ccm2_day','?')}, WVTR={props.get('wvtr_g_m2_day','?')}, Light={props.get('light_barrier','?')}  \n"
                        f"• Strength/Cushion: Stack={props.get('stack_strength_n','?')} N, Cushion={props.get('cushioning','?')}  \n"
                        f"• Recyclability: {props.get('recyclability','?')}  \n"
                        f"• Score: **{round(score,2)}**"
                    )
                    # accept button to log training data later
                    if st.button(f"✅ Use '{name}'", key=f"accept_{name}"):
                        log_interaction({
                            "timestamp": datetime.utcnow().isoformat(),
                            "product_name": product_name,
                            "product_desc": product_desc,
                            "auto_category": auto_category or "General Products",
                            "packaging_type": packaging_type,
                            "suggested_material": name,
                            "accepted": 1
                        })
                        st.success("Saved your choice for training. 🙌")

# ---------- Teach Materials ----------
with tab_teach_mat:
    st.subheader("🧑‍🏫 Teach: Packaging Materials")
    cols = st.columns(2)
    with cols[0]:
        m_name = st.text_input("Material Name *", placeholder="e.g., PET12/Al7/LDPE60 laminate")
        m_level = st.selectbox("Level *", ["primary","secondary","tertiary"])
        m_family = st.selectbox("Family *", ["laminate","film","corrugated","metal","glass","pulp","foam","plastic-bottle","other"])
        m_layers = st.text_input("Layers (optional)", placeholder="PET12|Al7|LDPE60")
        m_best_for = st.text_input("Best for (free text)", placeholder="snacks, powders")
        m_cost = st.number_input("Unit Cost (₹, optional)", min_value=0.0, step=0.1, value=0.0)
    with cols[1]:
        p_otr = st.number_input("OTR (cc/m²·day, lower=better)", min_value=0.0, step=0.1, value=0.0)
        p_wvtr = st.number_input("WVTR (g/m²·day, lower=better)", min_value=0.0, step=0.1, value=0.0)
        p_light = st.selectbox("Light Barrier", ["none","partial","high"])
        p_seal = st.number_input("Seal Temp (°C, optional)", min_value=0.0, step=1.0, value=0.0)
        p_max = st.number_input("Max Temp (°C, optional)", min_value=0.0, step=1.0, value=0.0)
        p_stack = st.number_input("Stack Strength (N, optional)", min_value=0.0, step=10.0, value=0.0)
        p_cush = st.selectbox("Cushioning", ["none","low","medium","high"])
        p_recy = st.selectbox("Recyclability", ["poor","moderate","good"])
    m_notes = st.text_area("Notes (optional)")

    if st.button("💾 Save Material"):
        if not m_name.strip():
            st.error("Material Name is required.")
        else:
            st.session_state.db["materials"][m_name] = {
                "level": m_level,
                "family": m_family,
                "layers": m_layers or None,
                "properties": {
                    "otr_ccm2_day": p_otr if p_otr>0 else None,
                    "wvtr_g_m2_day": p_wvtr if p_wvtr>0 else None,
                    "light_barrier": p_light,
                    "seal_temp_c": p_seal if p_seal>0 else None,
                    "max_temp_c": p_max if p_max>0 else None,
                    "stack_strength_n": p_stack if p_stack>0 else None,
                    "cushioning": p_cush,
                    "recyclability": p_recy
                },
                "unit_cost_inr": m_cost if m_cost>0 else None,
                "best_for": m_best_for or "",
                "notes": m_notes or ""
            }
            save_db(st.session_state.db)
            st.success(f"Saved material: {m_name}")
            st.snow()

# ---------- Teach Categories ----------
with tab_teach_cat:
    st.subheader("🧑‍🏫 Teach: Category Requirements")
    c_name = st.text_input("Category Name *", placeholder="e.g., Food & Beverages")
    c_oxy = st.checkbox("Oxygen sensitive")
    c_mois = st.checkbox("Moisture sensitive")
    c_light = st.checkbox("Light sensitive")
    c_frag = st.checkbox("Fragile")
    c_shelf = st.number_input("Shelf life (days)", min_value=0, step=1, value=0)
    c_stack = st.number_input("Min stack strength needed (N)", min_value=0, step=10, value=0)
    c_temp_min = st.number_input("Min temp (°C)", step=1.0, value=0.0)
    c_temp_max = st.number_input("Max temp (°C)", step=1.0, value=40.0)
    c_food = st.checkbox("Food-contact required (primary)")
    c_notes = st.text_area("Notes (optional)")

    if st.button("💾 Save Category"):
        if not c_name.strip():
            st.error("Category Name is required.")
        else:
            st.session_state.db["category_requirements"][c_name] = {
                "needs": {
                    "oxygen_sensitive": c_oxy,
                    "moisture_sensitive": c_mois,
                    "light_sensitive": c_light,
                    "fragile": c_frag
                },
                "shelf_life_days": c_shelf or None,
                "min_stack_strength_n": c_stack or None,
                "temp_range_c": [c_temp_min, c_temp_max],
                "food_contact": c_food,
                "notes": c_notes or ""
            }
            save_db(st.session_state.db)
            st.success(f"Saved category: {c_name}")
            st.balloons()

# ---------- Database / Backup ----------
with tab_db:
    st.subheader("🔎 JSON Viewer")
    st.json(st.session_state.db)

    st.download_button(
        "⬇️ Download DB (JSON backup)",
        data=json.dumps(st.session_state.db, indent=4, ensure_ascii=False),
        file_name="packaging_db_backup.json",
        mime="application/json"
    )

    st.markdown("---")
    st.subheader("📈 Training Log (for ML later)")
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        st.dataframe(df.tail(100), use_container_width=True)
        st.download_button(
            "⬇️ Download Training Log (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="training_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No interactions logged yet. When you click ✅ Use '<material>' on a suggestion, it will log data here.")

    st.markdown("> ML training button will appear here once you have enough logged samples (e.g., 100+).")
