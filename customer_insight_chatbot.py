import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- Load Data ---
@st.cache_data

def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df_clusters = load_data()

# --- Initialize session state ---
if "topics" not in st.session_state:
    st.session_state.topics = {}
    today = datetime.today().strftime("%d %B %Y")
    st.session_state.topics[today] = []
    st.session_state.active_topic = today
if "last_cluster" not in st.session_state:
    st.session_state.last_cluster = None
if "last_product" not in st.session_state:
    st.session_state.last_product = None

# --- Helper Functions ---
def get_cluster_info(cluster_id):
    subset = df_clusters[df_clusters['Cluster'] == cluster_id]
    if subset.empty:
        return "❌ That cluster doesn't exist."
    st.session_state.last_cluster = cluster_id
    avg_income = subset['Annual_Income'].mean()
    avg_spend = subset['Spending_Score'].mean()
    avg_order_value = subset['Average_Order_Value'].mean()
    avg_orders = subset['Number_of_Orders'].mean()
    avg_review = subset['Review_Score'].mean()
    avg_age = subset['Age'].mean()
    top_device = subset['Device_Used'].mode()[0]
    top_payment = subset['Preferred_Payment_Method'].mode()[0]
    top_product = subset['Product_Category'].mode()[0]
    return (
        f"### 🧠 Cluster {cluster_id} Overview\n"
        f"- Average Income: ${avg_income:,.2f}\n"
        f"- Spending Score: {avg_spend:.1f}\n"
        f"- Avg Order Value: ${avg_order_value:.2f}\n"
        f"- Orders per Customer: {avg_orders:.2f}\n"
        f"- Average Review Score: {avg_review:.2f}\n"
        f"- Age: {avg_age:.1f} years\n"
        f"- Most used payment method: **{top_payment}**\n"
        f"- Most used device: **{top_device}**\n"
        f"- Common product: **{top_product}**"
    )

def product_cluster_response(user_input):
    user_input_lower = user_input.lower()
    product_categories = df_clusters['Product_Category'].unique()
    matched_product = None
    for product in product_categories:
        if product.lower() in user_input_lower:
            matched_product = product
            break
    if matched_product:
        filtered = df_clusters[df_clusters['Product_Category'] == matched_product]
        cluster_counts = filtered['Cluster'].value_counts().sort_values(ascending=False)
        top_cluster = cluster_counts.idxmax()
        count = cluster_counts.max()
        st.session_state.last_cluster = top_cluster
        st.session_state.last_product = matched_product
        return (
            f"💡 Customers who purchase **{matched_product}** the most are in **Cluster {top_cluster}** "
            f"with **{count} customers**.\n\n"
            f"You can ask: 'Tell me more about Cluster {top_cluster}' to learn about them."
        )
    return None

def follow_up_on_last_cluster(user_input):
    msg = user_input.lower()
    cluster_id = st.session_state.last_cluster
    if cluster_id is None:
        return None
    subset = df_clusters[df_clusters["Cluster"] == cluster_id]

    if "income" in msg or "salary" in msg:
        return f"Average income in Cluster {cluster_id} is ${subset['Annual_Income'].mean():,.2f}."
    elif "spend" in msg:
        return f"Average spending score in Cluster {cluster_id} is {subset['Spending_Score'].mean():.2f}."
    elif "order" in msg:
        return f"Average number of orders in Cluster {cluster_id} is {subset['Number_of_Orders'].mean():.2f}."
    elif "review" in msg:
        return f"Average review score in Cluster {cluster_id} is {subset['Review_Score'].mean():.2f}."
    elif "device" in msg:
        return f"Most common device in Cluster {cluster_id} is **{subset['Device_Used'].mode().iloc[0]}**."
    elif "region" in msg:
        return f"Most customers in Cluster {cluster_id} are from **{subset['Customer_Region'].mode().iloc[0]}**."
    elif "gender" in msg:
        return f"Most customers in Cluster {cluster_id} are **{subset['Gender'].mode().iloc[0]}**."
    return None

def cluster_aware_response(user_input):
    input_lower = user_input.lower()

    # Ask for cluster info
    if "cluster" in input_lower:
        for i in range(10):
            if f"{i}" in input_lower:
                return get_cluster_info(i)

    # Ask for available product categories
    if ("product" in input_lower and "categor" in input_lower) or "available categories" in input_lower:
        categories = df_clusters['Product_Category'].unique()
        return "**Available Product Categories:**\n" + "\n".join(f"- {c}" for c in sorted(categories))

    # Other general questions
    if "payment" in input_lower:
        return "**Top Payment Methods:**\n- Credit Card\n- Debit Card\n- PayPal"
    if "device" in input_lower:
        return "**Common Devices Used:**\n- Mobile\n- Desktop\n- Tablet"
    if "delivery" in input_lower:
        return "**Preferred Delivery Options:**\n- Express\n- Standard\n- Scheduled"
    if "region" in input_lower:
        return "**Customer Regions:**\n- North\n- South\n- East\n- West"

    product_response = product_cluster_response(user_input)
    if product_response:
        return product_response

    follow_up = follow_up_on_last_cluster(user_input)
    if follow_up:
        return follow_up

    return "🤖 Sorry, I didn't understand that. Try asking about a product, a cluster, or spending habits."

# --- Sidebar Chat History ---
st.sidebar.title("📂 Chat History")
topic_choice = st.sidebar.radio("Choose a topic:", list(st.session_state.topics.keys()))
if topic_choice != st.session_state.active_topic:
    st.session_state.active_topic = topic_choice

new_topic = st.sidebar.text_input("Start new topic")
if st.sidebar.button("➕ Add Topic") and new_topic:
    st.session_state.topics[new_topic] = []
    st.session_state.active_topic = new_topic

chat_history = st.session_state.topics[st.session_state.active_topic]

# --- Custom CSS ---
st.markdown("""
    <style>
    .chat-container {
        max-height: calc(100vh - 160px);
        overflow-y: auto;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .message-box {
        margin: 0.25rem 0;
        padding: 0.75rem;
        border-radius: 10px;
    }
    .user-msg {
        background-color: #1a1a1a;
        border: 1px solid white;
    }
    .bot-msg {
        background-color: #262626;
        border: 1px solid white;
    }
    .input-container {
        display: flex;
        align-items: center;
        gap: 10px;
        position: fixed;
        bottom: 1rem;
        left: 260px;
        right: 1rem;
        z-index: 100;
    }
    .stTextInput > div > div > input {
        padding: 0.75rem;
        font-size: 1rem;
        border: 1px solid white;
        border-radius: 10px;
        width: 100%;
    }
    .send-button {
        padding: 0.75rem 1.5rem;
        background-color: #22c55e;
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# --- Main Chat Area ---
st.title("🛍️ Customer Insight Chatbot")
st.markdown("Ask me about product segments, clusters, and spending trends.")

with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for sender, msg in chat_history:
        role_class = "user-msg" if sender == "user" else "bot-msg"
        st.markdown(f'<div class="message-box {role_class}"><strong>{"🧑 You" if sender == "user" else "🤖 Bot"}:</strong> {msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Input Box ---
with st.container():
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_input = st.text_input("Type your question here...", key="user_input", label_visibility="collapsed")
    if st.button("Send", key="send_button"):
        if user_input:
            reply = cluster_aware_response(user_input)
            chat_history.append(("user", user_input))
            chat_history.append(("bot", reply))
            st.session_state.user_input = ""
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)
