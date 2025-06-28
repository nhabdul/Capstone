import streamlit as st
import pandas as pd

# --- Load data ---
@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df_clusters = load_data()

# --- Helpers ---
def get_cluster_info(cluster_id):
    subset = df_clusters[df_clusters['Cluster'] == cluster_id]
    if subset.empty:
        return "❌ That cluster doesn't exist."
    return (
        f"### 🧠 Cluster {cluster_id} Overview\n"
        f"- Avg Income: ${subset['Annual_Income'].mean():,.2f}\n"
        f"- Spending Score: {subset['Spending_Score'].mean():.1f}\n"
        f"- Avg Order Value: ${subset['Average_Order_Value'].mean():.2f}\n"
        f"- Orders per Customer: {subset['Number_of_Orders'].mean():.2f}\n"
        f"- Avg Review Score: {subset['Review_Score'].mean():.2f}\n"
        f"- Avg Age: {subset['Age'].mean():.1f} years\n"
        f"- Common Product: **{subset['Product_Category'].mode()[0]}**\n"
        f"- Common Device: **{subset['Device_Used'].mode()[0]}**\n"
        f"- Common Payment: **{subset['Preferred_Payment_Method'].mode()[0]}**"
    )

def product_cluster_response(user_input):
    user_input_lower = user_input.lower()
    for product in df_clusters['Product_Category'].dropna().unique():
        if product.lower() in user_input_lower:
            subset = df_clusters[df_clusters["Product_Category"] == product]
            cluster = subset["Cluster"].mode().iloc[0]
            st.session_state.last_cluster = cluster
            return f"💡 Customers who purchase **{product}** most are in **Cluster {cluster}**."
    return None

def followup_response(user_input):
    cluster = st.session_state.get("last_cluster", None)
    if cluster is None:
        return "🤖 Please ask about a product or cluster first."
    subset = df_clusters[df_clusters["Cluster"] == cluster]
    msg = user_input.lower()
    if "income" in msg or "salary" in msg:
        return f"💰 Avg income in Cluster {cluster}: ${subset['Annual_Income'].mean():,.2f}"
    elif "spending" in msg or "spend" in msg:
        return f"💸 Avg spending score in Cluster {cluster}: {subset['Spending_Score'].mean():.1f}"
    elif "order" in msg:
        return f"📦 Avg number of orders in Cluster {cluster}: {subset['Number_of_Orders'].mean():.1f}"
    elif "device" in msg:
        return f"📱 Most used device in Cluster {cluster}: {subset['Device_Used'].mode().iloc[0]}"
    elif "gender" in msg:
        return f"🚻 Most common gender in Cluster {cluster}: {subset['Gender'].mode().iloc[0]}"
    elif "region" in msg:
        return f"🌍 Most customers from: {subset['Customer_Region'].mode().iloc[0]}"
    return "🤖 Sorry, I couldn't understand your follow-up."

def get_bot_response(user_input):
    msg = user_input.lower()
    if "available" in msg and "category" in msg:
        categories = df_clusters["Product_Category"].dropna().unique()
        return "**Available Product Categories:**\n- " + "\n- ".join(sorted(categories))
    if "cluster" in msg:
        import re
        match = re.search(r"cluster\s*(\d+)", msg)
        if match:
            return get_cluster_info(int(match.group(1)))
    resp = product_cluster_response(user_input)
    if resp:
        return resp
    return followup_response(user_input)

# --- UI config ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .chat-container {
        height: 75vh;
        overflow-y: auto;
        padding: 10px;
        background: transparent;
        border: 1px solid #ccc;
        border-radius: 10px;
        margin-bottom: 60px;
    }
    .input-container {
        position: fixed;
        bottom: 20px;
        width: 85%;
        background: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Chat state ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_cluster" not in st.session_state:
    st.session_state.last_cluster = None

# --- Header ---
st.title("🛍️ Customer Insight Chatbot")

# --- Chat display ---
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for sender, text in st.session_state.chat:
        if sender == "user":
            st.markdown(f"**🧑 You:** {text}")
        else:
            st.markdown(f"**🤖 Bot:** {text}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Input at bottom ---
with st.container():
    user_msg = st.text_input("Ask a question about clusters, products, or spending…", key="chat_input")
    if user_msg:
        bot_reply = get_bot_response(user_msg)
        st.session_state.chat.append(("user", user_msg))
        st.session_state.chat.append(("bot", bot_reply))
        st.experimental_rerun()
