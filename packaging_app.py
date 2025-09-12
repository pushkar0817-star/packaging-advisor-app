import streamlit as st

# ============ CLEAN THEME CSS ============
st.markdown(
    """
    <style>
    /* General background */
    .stApp {
        background-color: #f9f9f9;
        color: #333333;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }

    [data-testid="stSidebar"] h2 {
        color: #2c3e50 !important;
    }

    /* Input fields */
    .stTextInput > div > div > input, 
    .stTextArea > div > textarea, 
    .stSelectbox > div > div {
        background: #ffffff;
        border: 1px solid #cccccc;
        color: #333333 !important;
        border-radius: 5px;
    }

    /* Button */
    div.stButton > button {
        background-color: #2c3e50;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 500;
        font-size: 15px;
        padding: 8px 18px;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #1a252f;
        transform: scale(1.02);
    }

    /* Title */
    h1, h2, h3 {
        color: #2c3e50 !important;
        font-weight: bold;
    }

    /* Footer creator tag in center */
    .creator {
        position: fixed;
        bottom: 8px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 12px;
        color: #666666;
        text-align: center;
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
st.markdown("<h1>🛒 Product Advisor</h1>", unsafe_allow_html=True)

# ============ PRODUCT ADVISOR FORM ============
if section == "🛒 Product Advisor":
    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input("✏️ Product Name")
    with col2:
        packaging_type = st.selectbox("📦 Packaging Type", ["Primary", "Secondary", "Tertiary"])

    product_desc = st.text_area("📝 Product Description")

    if st.button("🚀 Suggest Packaging"):
        st.success(f"Suggested packaging for **{product_name}** in **{packaging_type} packaging** ✅")

# Teach Model Section
elif section == "🤖 Teach Model":
    st.subheader("🤖 Train the Model")
    st.text_input("Provide Training Data")
    st.text_area("Add Notes")
    if st.button("📡 Train Model"):
        st.info("Training started...")

# Database Viewer Section
elif section == "📂 Database Viewer":
    st.subheader("📂 View Stored Data")
    st.write("Database content will be displayed here.")

# ============ CREATOR FOOTER ============
st.markdown(
    "<div class='creator'>👨‍💻 Created by Pushkar Singhania | IIP Delhi</div>",
    unsafe_allow_html=True
)
