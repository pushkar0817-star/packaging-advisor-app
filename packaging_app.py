import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = "packaging_db.json"

# Optional: advanced autocomplete
try:
    from streamlit_searchbox import st_searchbox  # pip install streamlit-searchbox
    HAS_SEARCHBOX = True
except Exception:
    HAS_SEARCHBOX = False

# Load database
@st.cache_data
def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        return {"products": {}, "packaging_materials": {}, "recommendation_rules": {}, "scoring_parameters": {}}

def save_database(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def get_all_food_products():
    return [
        # Database products
        "Milk", "Orange Juice", "Cooking Oil", "Bread", "Potato Chips",
        "Yogurt", "Honey", "Rice", "Frozen Pizza", "Coffee Beans",
        "Chocolate", "Baby Food", "Pasta", "Cereal", "Canned Soup",
        # Additional common products
        "Apple Juice", "Banana", "Butter", "Cheese", "Chicken", "Cookies",
        "Crackers", "Eggs", "Fish", "Flour", "Jam", "Ketchup", "Lemon",
        "Meat", "Noodles", "Onion", "Pepper", "Salt", "Sugar", "Tea",
        "Tomato", "Vinegar", "Wine", "Biscuits", "Cake", "Candy",
        "Ice Cream", "Nuts", "Pickles", "Sauce", "Spices", "Vegetables",
        "Fruit Juice", "Energy Drink", "Soda", "Water Bottle", "Sports Drink",
        "Protein Powder", "Granola Bars", "Trail Mix", "Dried Fruits",
        "Coconut Oil", "Olive Oil", "Sunflower Oil", "Peanut Butter",
        "Greek Yogurt", "Cottage Cheese", "Cream Cheese", "Mozzarella",
        "Cheddar Cheese", "Parmesan", "Whole Wheat Bread", "White Bread",
        "Bagels", "Croissants", "Muffins", "Donuts", "Pizza Dough",
        "Tomato Sauce", "BBQ Sauce", "Hot Sauce", "Soy Sauce", "Mustard",
        "Mayonnaise", "Ranch Dressing", "Italian Dressing", "Balsamic Vinegar",
        "Coconut Water", "Almond Milk", "Soy Milk", "Oat Milk", "Protein Shake",
        "Green Tea", "Black Tea", "Herbal Tea", "Matcha", "Coffee Powder",
        "Instant Coffee", "Espresso", "Cappuccino Mix", "Hot Chocolate"
    ]

# Ranked suggestions helper
def ranked_suggestions(query: str, db, max_out: int = 8):
    all_products = get_all_food_products()
    db_products = set(db.get("products", {}).keys())
    if not query:
        # Default: show DB items first
        base = sorted(all_products, key=lambda x: (0 if x in db_products else 1, x))
        return base[:max_out]
    q = query.lower()
    scored = []
    for opt in all_products:
        ol = opt.lower()
        if q in ol:
            # Lower score = higher rank
            if ol == q:
                score = 0
            elif opt in db_products:
                score = 1
            elif ol.startswith(q):
                score = 2
            else:
                score = 3
            scored.append((score, opt))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [s[1] for s in scored[:max_out]]

# Fallback search for legacy UI
def search_products(query, db):
    return ranked_suggestions(query, db, max_out=10)

# ====== Recommendation engine (same as before) ======

def get_auto_parameters(product_name, purpose, cost, shelf_life, db):
    auto_params = {
        "product_state": "Liquid",
        "viscosity": "Medium",
        "ph_level": "Neutral",
        "oxygen_sensitivity": "Medium",
        "moisture_sensitivity": "Medium",
        "light_sensitivity": "Medium",
        "storage_temperature": "Ambient",
        "target_market": "Consumer retail",
        "industry_category": "Food",
        "budget_range": cost,
        "sustainability_priority": "Balanced",
        "safety_requirements": [],
        "brand_positioning": "Mainstream",
        "fragility_level": "Moderate",
        "shelf_life_requirement": shelf_life
    }
    products = db.get("products", {})
    if product_name in products:
        stored = products[product_name].get("auto_parameters", {})
        auto_params.update(stored)
        auto_params["budget_range"] = cost
        auto_params["shelf_life_requirement"] = shelf_life
        return auto_params
    pl = product_name.lower()
    if any(w in pl for w in ["juice","drink","beverage","soda","water","tea","coffee","milk"]):
        auto_params["product_state"] = "Liquid"
        auto_params["viscosity"] = "Low"
        if any(w in pl for w in ["orange","apple","fruit"]):
            auto_params["oxygen_sensitivity"] = "High"
            auto_params["light_sensitivity"] = "High"
            auto_params["ph_level"] = "Acidic"
        if "milk" in pl:
            auto_params["storage_temperature"] = "Cold"
            auto_params["light_sensitivity"] = "High"
    elif any(w in pl for w in ["cheese","butter","yogurt","cream"]):
        auto_params["product_state"] = "Semi-solid"
        auto_params["storage_temperature"] = "Cold"
        auto_params["oxygen_sensitivity"] = "Medium"
        auto_params["light_sensitivity"] = "High"
        auto_params["shelf_life_requirement"] = "Weeks"
    elif any(w in pl for w in ["oil","vinegar","sauce","honey","syrup","dressing"]):
        auto_params["product_state"] = "Liquid"
        auto_params["viscosity"] = "High" if any(w in pl for w in ["honey","syrup"]) else "Medium"
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["light_sensitivity"] = "High"
    elif any(w in pl for w in ["rice","pasta","flour","cereal","grain","oats","bread"]):
        auto_params["product_state"] = "Solid"
        auto_params["viscosity"] = "N/A"
        auto_params["moisture_sensitivity"] = "High"
        auto_params["oxygen_sensitivity"] = "Low"
        auto_params["storage_temperature"] = "Ambient"
        if "bread" in pl:
            auto_params["fragility_level"] = "Fragile"
            auto_params["shelf_life_requirement"] = "Days"
    elif any(w in pl for w in ["chips","crackers","cookies","biscuits","nuts","candy"]):
        auto_params["product_state"] = "Solid"
        auto_params["viscosity"] = "N/A"
        auto_params["fragility_level"] = "Very Fragile" if "chips" in pl else "Fragile"
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["moisture_sensitivity"] = "High"
    elif any(w in pl for w in ["meat","chicken","fish","beef","pork","protein"]):
        auto_params["product_state"] = "Solid"
        auto_params["storage_temperature"] = "Cold"
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["shelf_life_requirement"] = "Days"
        auto_params["safety_requirements"] = ["Sterile"]
    elif any(w in pl for w in ["frozen","ice cream"]):
        auto_params["storage_temperature"] = "Frozen"
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["moisture_sensitivity"] = "High"
    elif any(w in pl for w in ["canned","soup"]):
        auto_params["product_state"] = "Liquid" if "soup" in pl else "Semi-solid"
        auto_params["oxygen_sensitivity"] = "None"
        auto_params["moisture_sensitivity"] = "None"
        auto_params["shelf_life_requirement"] = "Years"
    elif any(w in pl for w in ["chocolate","cake","jam"]):
        auto_params["product_state"] = "Solid"
        auto_params["moisture_sensitivity"] = "High"
        auto_params["light_sensitivity"] = "High"
        auto_params["brand_positioning"] = "Premium"
    if cost == "Premium":
        auto_params["brand_positioning"] = "Premium"
        auto_params["sustainability_priority"] = "Balanced"
    elif cost == "Economy":
        auto_params["brand_positioning"] = "Value"
        auto_params["sustainability_priority"] = "Cost focused"
    if shelf_life in ["Months","Years"]:
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["moisture_sensitivity"] = "High"
    return auto_params

def calculate_packaging_score(user_inputs, material_name, material_data, db):
    total_score = 0
    max_possible_score = 0
    scoring_details = []
    scoring_params = db.get("scoring_parameters", {})
    weights = scoring_params.get("compatibility_weights", {})
    if user_inputs.get('product_state') in material_data['characteristics']['product_state_compatibility']:
        score = weights.get('product_state', 25)
        total_score += score
        scoring_details.append(f"✅ Product state compatibility: +{score}")
    else:
        scoring_details.append("❌ Product state incompatible: +0")
    max_possible_score += weights.get('product_state', 25)
    barrier_score = 0
    barrier_scoring = scoring_params.get("barrier_scoring", {})
    for barrier_type in ['oxygen','moisture','light']:
        user_need = user_inputs.get(f'{barrier_type}_sensitivity', 'None')
        material_barrier = material_data['characteristics'][f'{barrier_type}_barrier'].lower()
        if user_need in barrier_scoring.get(barrier_type, {}):
            need_mapping = barrier_scoring[barrier_type][user_need]
            barrier_points = need_mapping.get(material_barrier.title(), 0)
            barrier_score += barrier_points
            if barrier_points > 0:
                scoring_details.append(f"✅ {barrier_type.title()} barrier: +{barrier_points}")
            else:
                scoring_details.append(f"⚠️ {barrier_type.title()} barrier: {barrier_points}")
    total_score += barrier_score
    max_possible_score += weights.get('barrier_requirements', 20)
    user_ph = user_inputs.get('ph_level', 'Neutral')
    if user_ph in material_data['characteristics']['ph_tolerance']:
        chem_score = weights.get('chemical_compatibility', 15)
        total_score += chem_score
        scoring_details.append(f"✅ Chemical compatibility: +{chem_score}")
    else:
        scoring_details.append("❌ Chemical incompatibility: +0")
    max_possible_score += weights.get('chemical_compatibility', 15)
    cost_scoring = scoring_params.get("cost_scoring", {})
    user_budget = user_inputs.get('budget_range', 'Standard')
    material_cost = material_data['characteristics']['cost_category']
    if user_budget in cost_scoring and material_cost in cost_scoring[user_budget]:
        cost_score = cost_scoring[user_budget][material_cost]
        total_score += cost_score
        if cost_score > 0:
            scoring_details.append(f"✅ Cost alignment: +{cost_score}")
        else:
            scoring_details.append(f"⚠️ Cost mismatch: {cost_score}")
    max_possible_score += weights.get('cost_alignment', 12)
    user_temp = user_inputs.get('storage_temperature', 'Ambient')
    if user_temp in material_data['characteristics']['temperature_range']:
        temp_score = weights.get('temperature_requirements', 10)
        total_score += temp_score
        scoring_details.append(f"✅ Temperature compatibility: +{temp_score}")
    else:
        scoring_details.append("❌ Temperature incompatibility: +0")
    max_possible_score += weights.get('temperature_requirements', 10)
    sustain_score = 0
    if user_inputs.get('sustainability_priority') == 'Eco-focused':
        if material_data['sustainability']['recyclable']:
            sustain_score += 4
        if material_data['sustainability']['pcr_available']:
            sustain_score += 2
        if material_data['sustainability']['biodegradable']:
            sustain_score += 2
    else:
        sustain_score = 4
    total_score += sustain_score
    max_possible_score += weights.get('sustainability_match', 8)
    scoring_details.append(f"♻️ Sustainability match: +{sustain_score}")
    rule_bonuses = apply_recommendation_rules(user_inputs, material_name, db)
    total_score += rule_bonuses
    if rule_bonuses > 0:
        scoring_details.append(f"🎯 Rule bonuses: +{rule_bonuses:.1f}")
    final_score = min(100, (total_score / max_possible_score) * 100) if max_possible_score > 0 else 0
    return final_score, scoring_details

def apply_recommendation_rules(user_inputs, material_name, db):
    bonus_points = 0
    rules = db.get("recommendation_rules", {})
    for _, rule_data in rules.items():
        rule_triggered = False
        for trigger in rule_data.get("triggers", []):
            for key, value in trigger.items():
                if user_inputs.get(key) == value:
                    rule_triggered = True
                    break
        if rule_triggered:
            if material_name in rule_data.get("recommended_materials", []):
                bonus_points += rule_data.get("priority_score", 0) * 0.3
            elif material_name in rule_data.get("avoid_materials", []):
                bonus_points -= rule_data.get("priority_score", 0) * 0.2
    return bonus_points

def get_packaging_recommendations(auto_params, db):
    recs = []
    materials = db.get("packaging_materials", {})
    for material_name, material_data in materials.items():
        score, details = calculate_packaging_score(auto_params, material_name, material_data, db)
        recs.append({
            'name': material_name.replace('_', ' '),
            'material_name': material_name,
            'score': score,
            'data': material_data,
            'scoring_details': details,
            'reasons': generate_recommendation_reasons(auto_params, material_data, score)
        })
    recs.sort(key=lambda x: x['score'], reverse=True)
    return recs

def generate_recommendation_reasons(auto_params, material_data, score):
    reasons = []
    if auto_params.get('product_state') in material_data['characteristics']['product_state_compatibility']:
        reasons.append(f"✅ Perfect for {auto_params.get('product_state').lower()} products")
    barrier_reasons = []
    for barrier_type in ['oxygen','moisture','light']:
        need = auto_params.get(f'{barrier_type}_sensitivity', 'None')
        barrier = material_data['characteristics'][f'{barrier_type}_barrier']
        if need == 'High' and barrier in ['Excellent','High']:
            barrier_reasons.append(barrier_type)
    if barrier_reasons:
        reasons.append(f"🛡️ Excellent {', '.join(barrier_reasons)} protection")
    if auto_params.get('budget_range') == material_data['characteristics']['cost_category']:
        reasons.append(f"💰 Matches {auto_params.get('budget_range').lower()} budget perfectly")
    if auto_params.get('sustainability_priority') == 'Eco-focused':
        feats = []
        sust = material_data['sustainability']
        if sust['recyclable']:
            feats.append('recyclable')
        if sust['pcr_available']:
            feats.append('PCR available')
        if sust['biodegradable']:
            feats.append('biodegradable')
        if feats:
            reasons.append(f"♻️ Eco-friendly: {', '.join(feats)}")
    if score >= 90:
        reasons.append("⭐ Exceptional compatibility match")
    elif score >= 75:
        reasons.append("✨ Excellent compatibility")
    elif score >= 60:
        reasons.append("👍 Good compatibility")
    for pro in material_data.get('pros', [])[:2]:
        reasons.append(f"💪 {pro}")
    return reasons

def main():
    st.set_page_config(page_title="🎯 Smart Packaging Advisor Pro", page_icon="📦", layout="wide", initial_sidebar_state="expanded")
    db = load_database()
    st.title("🎯 Smart Packaging Advisor Pro")
    st.markdown('<p style="font-size: 16px; color: #666; margin-top: -10px;">Made by Pushkar Singhania, IIP Delhi, MS Student</p>', unsafe_allow_html=True)
    st.markdown("*AI-Powered Packaging Recommendations - Just 4 Simple Questions!*")
    st.markdown("---")
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        page = st.radio("Select Function:", ["🎯 Get Smart Recommendations","📋 Browse Products Database","💾 Save New Product","📊 Material Database","⚙️ System Info"])
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("Products", len(db.get("products", {})))
        st.metric("Materials", len(db.get("packaging_materials", {})))
        st.metric("Rules", len(db.get("recommendation_rules", {})))
    if page == "🎯 Get Smart Recommendations":
        recommendation_page(db)
    elif page == "📋 Browse Products Database":
        browse_products_page(db)
    elif page == "💾 Save New Product":
        save_product_page(db)
    elif page == "📊 Material Database":
        material_database_page(db)
    else:
        system_info_page(db)

def recommendation_page(db):
    st.header("🎯 Get Smart Packaging Recommendations")
    st.markdown("*Answer just 4 simple questions to get AI-powered packaging suggestions*")

    # =====================
    # Product name input
    # =====================
    st.markdown("### 📝 Tell us about your product")
    st.markdown("🏷️ **1. What is your product name?**")

    db_products = list(db.get("products", {}).keys())

    product_name = None

    if HAS_SEARCHBOX:
        # True Google-like behavior with dropdown that autofills the same field
        def _search_fn(searchterm: str):
            return ranked_suggestions(searchterm, db, max_out=8)
        default_val = st.session_state.get("product_name", "")
        product_name = st_searchbox(
            search_function=_search_fn,
            placeholder="Start typing... e.g., Orange Juice, Chocolate, Rice",
            default=default_val,
            key="product_searchbox",
        )
        if product_name is None:
            # st_searchbox returns None until user selects or enters
            product_name = default_val
        else:
            st.session_state.product_name = product_name
    else:
        # Fallback: text_input + live suggestions below; click to autofill
        typed = st.text_input(
            "Product Name",
            value=st.session_state.get("product_name", ""),
            placeholder="Start typing... e.g., Orange Juice, Chocolate, Rice",
        )
        suggestions = ranked_suggestions(typed, db, max_out=8)
        if suggestions:
            st.caption("Suggestions (click to autofill):")
            cols = st.columns(2)
            for i, sug in enumerate(suggestions):
                with cols[i % 2]:
                    if st.button(f"🔍 {sug}", key=f"sug_{i}", use_container_width=True):
                        st.session_state.product_name = sug
                        st.experimental_rerun()
        product_name = st.session_state.get("product_name", typed)
        if not HAS_SEARCHBOX:
            st.info("Tip: For Google-like dropdown in the same field, install 'streamlit-searchbox' and restart: pip install streamlit-searchbox")

    if product_name:
        if product_name in db_products:
            st.success(f"✅ Found '{product_name}' in our database!")
        else:
            st.info(f"📦 Will analyze '{product_name}' using AI detection")

    st.markdown("---")

    # Remaining 3 inputs
    purpose = st.selectbox(
        "🎯 **2. What is the main purpose of packaging?**",
        ["Protection & Storage","Retail Display","Transportation","Medical Safety","Food Safety","Industrial Use"]
    )
    cost = st.selectbox("💰 **3. What is your budget preference?**", ["Economy","Standard","Premium"])
    shelf_life = st.selectbox("⏰ **4. How long should the product last?**", ["Days","Weeks","Months","Years"])

    st.markdown("---")

    if st.button("🎯 Get My Packaging Recommendations", type="primary", use_container_width=True):
        if not product_name:
            st.error("❌ Please enter or select a product name first!")
            return
        with st.spinner("🤖 AI is analyzing your product and generating recommendations..."):
            db = load_database()
            auto_params = get_auto_parameters(product_name, purpose, cost, shelf_life, db)
            recommendations = get_packaging_recommendations(auto_params, db)
        if not recommendations:
            st.error("❌ No packaging materials found in database.")
            return
        st.success(f"🎉 Here are the packaging recommendations for **{product_name}**!")
        with st.expander("🔍 What our AI detected about your product", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Product Analysis:**")
                st.write(f"• Industry: {auto_params['industry_category']}")
                st.write(f"• State: {auto_params['product_state']}")
                st.write(f"• Target Market: {auto_params['target_market']}")
            with col2:
                st.write("**Protection Needs:**")
                st.write(f"• Oxygen: {auto_params['oxygen_sensitivity']}")
                st.write(f"• Moisture: {auto_params['moisture_sensitivity']}")
                st.write(f"• Light: {auto_params['light_sensitivity']}")
            with col3:
                st.write("**Requirements:**")
                st.write(f"• Storage: {auto_params['storage_temperature']}")
                st.write(f"• Positioning: {auto_params['brand_positioning']}")
                st.write(f"• Sustainability: {auto_params['sustainability_priority']}")
        for i, rec in enumerate(recommendations[:5], 1):
            score_color = "green" if rec['score'] >= 75 else "orange" if rec['score'] >= 50 else "red"
            with st.expander(f"#{i} {rec['name']} - {rec['score']:.1f}% Match", expanded=i<=3):
                col_info, col_details, col_reasons = st.columns([1,1,1])
                with col_info:
                    st.markdown(f"**Score: :{score_color}[{rec['score']:.1f}%]**")
                    st.write(f"**Type:** {rec['data']['material_type']}")
                    st.write(f"**Cost:** {rec['data']['characteristics']['cost_category']}")
                    barriers = []
                    for b in ['oxygen','moisture','light']:
                        level = rec['data']['characteristics'][f'{b}_barrier']
                        barriers.append(f"{b.title()}: {level}")
                    st.write(f"**Barriers:** {', '.join(barriers)}")
                with col_details:
                    st.write("**Detailed Scoring:**")
                    for detail in rec['scoring_details'][:4]:
                        st.write(f"• {detail}")
                with col_reasons:
                    st.write("**Why This Packaging:**")
                    for reason in rec['reasons']:
                        st.write(f"• {reason}")
                col_pros, col_cons = st.columns(2)
                with col_pros:
                    st.write("**✅ Advantages:**")
                    for pro in rec['data'].get('pros', []):
                        st.write(f"• {pro}")
                with col_cons:
                    st.write("**⚠️ Considerations:**")
                    for con in rec['data'].get('cons', []):
                        st.write(f"• {con}")
        st.markdown("---")
        st.markdown(f"## 📦 **Final Packaging Recommendations for {product_name}**")
        if recommendations:
            top_3 = recommendations[:3]
            col1, col2, col3 = st.columns(3)
            for i, rec in enumerate(top_3):
                with [col1, col2, col3][i]:
                    if rec['score'] >= 75:
                        emoji, color = "🏆", "28a745"
                    elif rec['score'] >= 50:
                        emoji, color = "🥈", "ffc107"
                    else:
                        emoji, color = "🥉", "17a2b8"
                    st.markdown(f"""
                    <div style="border: 2px solid #{color}; border-radius: 10px; padding: 15px; text-align: center; margin: 5px;">
                        <h4>{emoji} #{i+1} CHOICE</h4>
                        <h3>{rec['name']}</h3>
                        <h2 style="color: #{color}">{rec['score']:.0f}% Match</h2>
                        <p><strong>Type:</strong> {rec['data']['material_type']}</p>
                        <p><strong>Cost:</strong> {rec['data']['characteristics']['cost_category']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("**🔑 Key Benefits:**")
                    for reason in rec['reasons'][:3]:
                        st.markdown(f"• {reason}")
                    if i == 0:
                        st.markdown("**🎯 RECOMMENDED CHOICE**")
            st.markdown("---")
            best = recommendations[0]
            st.info(f"""
            **💡 Summary:** Based on your product '{product_name}' with {purpose.lower()} purpose, 
            {cost.lower()} budget, and {shelf_life.lower()} shelf life, we recommend **{best['name']}** 
            as your best packaging solution with a {best['score']:.0f}% compatibility match.
            """)
        else:
            st.warning("⚠️ No recommendations could be generated.")

def browse_products_page(db):
    st.header("📋 Browse Products Database")
    products = db.get("products", {})
    if not products:
        st.warning("No products found in database.")
        return
    col1, col2 = st.columns([2,1])
    with col1:
        search_term = st.text_input("🔍 Search Products:", placeholder="Type product name...")
    with col2:
        categories = sorted({p.get("basic_info", {}).get("category","") for p in products.values() if p.get("basic_info", {}).get("category")})
        category_filter = st.selectbox("📂 Filter by Category:", ["All Categories"] + categories)
    filtered = []
    for name, pdata in products.items():
        cat = pdata.get("basic_info", {}).get("category", "")
        if search_term and search_term.lower() not in name.lower():
            continue
        if category_filter != "All Categories" and cat != category_filter:
            continue
        filtered.append((name, pdata))
    st.info(f"📊 Found {len(filtered)} products")
    for name, pdata in filtered:
        with st.expander(f"📦 {name}"):
            col1, col2 = st.columns(2)
            with col1:
                bi = pdata.get("basic_info", {})
                st.write(f"**Category:** {bi.get('category','N/A')}")
                st.write(f"**Subcategory:** {bi.get('subcategory','N/A')}")
                st.write(f"**Market:** {bi.get('intended_market','N/A')}")
                pr = pdata.get("properties", {})
                st.write(f"**Volume/Weight:** {pr.get('weight_volume','N/A')}")
                st.write(f"**Shelf Life:** {pr.get('shelf_life','N/A')}")
            with col2:
                pk = pdata.get("packaging", {})
                st.write("**Packaging Solutions:**")
                st.write(f"• Primary: {', '.join(pk.get('primary', []))}")
                st.write(f"• Secondary: {', '.join(pk.get('secondary', []))}")
                st.write(f"• Tertiary: {', '.join(pk.get('tertiary', []))}")

def save_product_page(db):
    st.header("💾 Save New Product")
    st.markdown("*Add a new product to the database*")
    name = st.text_input("Product Name:", placeholder="e.g., Premium Face Serum")
    if name:
        if name in db.get("products", {}):
            st.error(f"Product '{name}' already exists!")
            return
        purpose = st.selectbox("Purpose:", ["Protection & Storage","Retail Display","Transportation","Medical Safety","Food Safety","Industrial Use"])
        cost = st.selectbox("Budget:", ["Economy","Standard","Premium"])
        shelf_life = st.selectbox("Shelf Life:", ["Days","Weeks","Months","Years"])
        if st.button("💾 Save Product", type="primary"):
            auto_params = get_auto_parameters(name, purpose, cost, shelf_life, db)
            new_product = {
                "basic_info": {"category": auto_params["industry_category"], "subcategory": "Auto-detected", "intended_market": auto_params["target_market"]},
                "properties": {"weight_volume": "Auto-detected", "shape_form": auto_params["product_state"], "shelf_life": shelf_life, "fragility": auto_params["fragility_level"], "moisture_sensitivity": "Yes" if auto_params["moisture_sensitivity"] in ["Medium","High"] else "No", "light_sensitivity": "Yes" if auto_params["light_sensitivity"] in ["Medium","High"] else "No"},
                "packaging": {"primary": [], "secondary": [], "tertiary": []},
                "auto_parameters": auto_params,
                "created_date": datetime.now().isoformat()
            }
            db["products"][name] = new_product
            save_database(db)
            st.success(f"✅ Product '{name}' saved successfully!")
            st.rerun()

def material_database_page(db):
    st.header("📊 Packaging Materials Database")
    materials = db.get("packaging_materials", {})
    if not materials:
        st.warning("No materials found in database.")
        return
    st.subheader("📈 Database Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Materials", len(materials))
    with col2:
        recyclable_count = sum(1 for m in materials.values() if m['sustainability']['recyclable'])
        st.metric("Recyclable Materials", recyclable_count)
    with col3:
        cost_categories = [m['characteristics']['cost_category'] for m in materials.values()]
        st.metric("Premium Materials", cost_categories.count('Premium'))
    for material_name, material_data in materials.items():
        with st.expander(f"📦 {material_name.replace('_',' ')}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Basic Properties:**")
                chars = material_data['characteristics']
                st.write(f"• Type: {material_data['material_type']}")
                st.write(f"• Cost Category: {chars['cost_category']}")
                st.write(f"• Product States: {', '.join(chars['product_state_compatibility'])}")
            with col2:
                st.write("**Barrier Properties:**")
                st.write(f"• Oxygen: {chars['oxygen_barrier']}")
                st.write(f"• Moisture: {chars['moisture_barrier']}")
                st.write(f"• Light: {chars['light_barrier']}")
                st.write(f"• Chemical Resistance: {chars['chemical_resistance']}")
            with col3:
                st.write("**Sustainability:**")
                sust = material_data['sustainability']
                st.write(f"• Recyclable: {'✅' if sust['recyclable'] else '❌'}")
                st.write(f"• PCR Available: {'✅' if sust['pcr_available'] else '❌'}")
                st.write(f"• Biodegradable: {'✅' if sust['biodegradable'] else '❌'}")

def system_info_page(db):
    st.header("⚙️ System Information")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Database Statistics")
        st.write(f"**Products:** {len(db.get('products', {}))}")
        st.write(f"**Packaging Materials:** {len(db.get('packaging_materials', {}))}")
        st.write(f"**Recommendation Rules:** {len(db.get('recommendation_rules', {}))}")
        import sys
        db_size = sys.getsizeof(str(db)) / 1024
        st.write(f"**Database Size:** {db_size:.1f} KB")
    with col2:
        st.subheader("🎯 System Features")
        st.write("✅ AI-Powered Recommendations")
        st.write("✅ Google-like Autocomplete (uses streamlit-searchbox if installed)")
        st.write("✅ Just 4 Simple Questions")
        st.write("✅ Auto Parameter Detection")
        st.write("✅ Advanced Scoring Algorithm")
        st.write("✅ Technical Material Database")
        st.write("✅ Sustainability Analysis")
        st.write("✅ Cost Optimization")
    st.subheader("🤖 How It Works")
    st.write("""
    • Start typing product name and pick from dropdown (or click a suggestion in fallback mode)
    • AI auto-detects key parameters and scores materials
    • Get top packaging recommendations with reasons
    """)
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    🚀 <b>Smart Packaging Advisor Pro</b> by Pushkar Singhania | IIP Delhi<br>
    Advanced Packaging Engineering & Materials Science
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
