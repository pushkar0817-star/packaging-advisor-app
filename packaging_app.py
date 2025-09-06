import streamlit as st

# ============ FUTURISTIC THEME CSS ============
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #e0e0e0;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141E30, #243B55);
        color: #f8f8f8;
    }
    [data-testid="stSidebar"] h2 {
        color: #00f5ff !important;
        text-shadow: 0px 0px 8px #00f5ff;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label {
        color: #ddd !important;
    }

    /* Labels */
    label, .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #ffffff !important;
        font-weight: bold;
        text-shadow: 0px 0px 6px #00f5ff;
    }

    /* Input boxes */
    .stTextInput > div > div > input, 
    .stTextArea > div > textarea, 
    .stSelectbox > div > div {
        background: rgba(20, 30, 48, 0.9);
        border: 1px solid #00f5ff;
        color: #ffffff !important;
        border-radius: 10px;
    }

    /* Button */
    div.stButton > button {
        background: linear-gradient(90deg, #00f5ff, #ff00ff);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        font-size: 16px;
        padding: 8px 18px;
        box-shadow: 0px 0px 12px #00f5ff;
        transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #ff00ff, #00f5ff);
        box-shadow: 0px 0px 20px #ff00ff;
        transform: scale(1.05);
    }

    /* Title */
    h1, h2, h3 {
        color: #00f5ff !important;
        text-shadow: 0px 0px 12px #00f5ff;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============ SIDEBAR ============
st.sidebar.title("⚡ Navigation")
st.sidebar.write("Choose a section:")
section = st.sidebar.radio(
    "",
    ["🛒 Product Advisor", "🤖 Teach Model", "📂 Database Viewer"]
)

# ============ MAIN TITLE ============
st.markdown("<h1>🛒 Futuristic Product Advisor</h1>", unsafe_allow_html=True)

# ============ PRODUCT ADVISOR FORM ============
if section == "🛒 Product Advisor":
    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input("✏️ Product Name")
    with col2:
        packaging_type = st.selectbox("📦 Packaging Type", ["Primary", "Secondary", "Tertiary"])

    product_desc = st.text_area("📝 Product Description")

    if st.button("🚀 Suggest Packaging"):
        st.success(f"✨ Suggested futuristic packaging for **{product_name}** in **{packaging_type} packaging** 🚀")

# Teach Model Section
elif section == "🤖 Teach Model":
    st.subheader("🤖 Train the AI Model")
    st.text_input("Provide Training Data")
    st.text_area("Add Notes")
    if st.button("📡 Train Model"):
        st.info("⚡ Training started...")

# Database Viewer Section
elif section == "📂 Database Viewer":
    st.subheader("📂 View Stored Data")
    st.write("🔍 Database content will be displayed here.")
