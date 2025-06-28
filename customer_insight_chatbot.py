import streamlit as st
import pandas as pd

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df_clusters = load_data()

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

    if "cluster" in input_lower:
        for i in range(10):
            if f"{i}" in input_lower:
                return get_cluster_info(i)

    if ("product" in input_lower and "categor" in input_lower) or "available categories" in input_lower:
        categories = df_clusters['Product_Category'].unique()
        return "**Available Product Categories:**\n" + "\n".join(f"- {c}" for c in sorted(categories))

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

# --- Session State Initialization ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_cluster' not in st.session_state:
    st.session_state.last_cluster = None
if 'last_product' not in st.session_state:
    st.session_state.last_product = None
if 'chat_input' not in st.session_state:
    st.session_state.chat_input = ""

# --- App UI ---
st.set_page_config(page_title="Customer Insight Chatbot", layout="wide")
st.title("🛍️ Customer Insight Chatbot")
st.markdown("Ask me about product segments, customer clusters, or behavior insights!")

# --- Display Chat History ---
st.markdown("### 💬 Chat History")
for sender, message in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {message}")

# --- Chat Form (Enter works, no bugs) ---
with st.form("chat_form", clear_on_submit=False):
    st.text_input("Type your question here...", key="chat_input")
    submitted = st.form_submit_button("Send")

# --- Handle submission outside the form ---
if submitted and st.session_state.chat_input.strip():
    user_msg = st.session_state.chat_input
    st.session_state.chat_history.append(("You", user_msg))
    bot_reply = cluster_aware_response(user_msg)
    st.session_state.chat_history.append(("Bot", bot_reply))

    # Clear input box properly
    st.session_state.chat_input = ""

# --- Clear Chat Button ---
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.session_state.last_cluster = None
    st.session_state.last_product = None
    st.session_state.chat_input = ""
