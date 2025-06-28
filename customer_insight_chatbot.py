import streamlit as st
import pandas as pd

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df_clusters = load_data()

# --- Session state ---
if "topics" not in st.session_state:
    st.session_state.topics = {"Default": []}
if "active_topic" not in st.session_state:
    st.session_state.active_topic = "Default"
if "last_cluster" not in st.session_state:
    st.session_state.last_cluster = None
if "last_product" not in st.session_state:
    st.session_state.last_product = None

# Sidebar: topic history
st.sidebar.title("📂 Chat History")
topic_choice = st.sidebar.radio("Choose a topic:", list(st.session_state.topics.keys()))
if topic_choice != st.session_state.active_topic:
    st.session_state.active_topic = topic_choice

new_topic = st.sidebar.text_input("Start new topic")
if st.sidebar.button("➕ Add Topic") and new_topic:
    st.session_state.topics[new_topic] = []
    st.session_state.active_topic = new_topic

# Helper: Get cluster overview
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

# Helper: Match product to cluster
def product_cluster_response(user_input):
    product_categories = df_clusters['Product_Category'].dropna().unique()
    for product in product_categories:
        if product.lower() in user_input.lower():
            st.session_state.last_product = product
            filtered = df_clusters[df_clusters['Product_Category'] == product]
            cluster_counts = filtered['Cluster'].value_counts().sort_values(ascending=False)
            top_cluster = cluster_counts.idxmax()
            st.session_state.last_cluster = top_cluster
            return (
                f"💡 Customers who purchase **{product}** the most are in **Cluster {top_cluster}** "
                f"with **{cluster_counts.max()} customers**.\n\n"
                f"You can ask: 'Tell me more about Cluster {top_cluster}' to learn about them."
            )
    return None

# Handle user message
def cluster_aware_response(user_input):
    msg = user_input.lower()

    # Ask for product categories
    if "product" in msg and "categor" in msg:
        cats = df_clusters['Product_Category'].dropna().unique()
        return "**Available Product Categories:**\n" + "\n".join(f"- {c}" for c in sorted(cats))

    # Product-based question
    product_response = product_cluster_response(user_input)
    if product_response:
        return product_response

    # Specific cluster request
    if "cluster" in msg:
        import re
        match = re.search(r"cluster\s*(\d+)", msg)
        if match:
            return get_cluster_info(int(match.group(1)))

    # Follow-up questions with memory
    if any(key in msg for key in ["income", "spend", "order", "review", "device", "region", "gender", "age", "value"]):
        cluster_id = st.session_state.last_cluster
        if cluster_id is None:
            return "Please ask about a product or cluster first so I know which group to analyze."
        subset = df_clusters[df_clusters['Cluster'] == cluster_id]
        if "income" in msg or "salary" in msg:
            return f"Average income in Cluster {cluster_id} is ${subset['Annual_Income'].mean():,.2f}."
        if "spend" in msg:
            return f"Average spending score in Cluster {cluster_id} is {subset['Spending_Score'].mean():.2f}."
        if "order" in msg and "value" in msg:
            return f"Average order value in Cluster {cluster_id} is ${subset['Average_Order_Value'].mean():.2f}."
        if "order" in msg:
            return f"Average number of orders in Cluster {cluster_id} is {subset['Number_of_Orders'].mean():.2f}."
        if "review" in msg:
            return f"Average review score in Cluster {cluster_id} is {subset['Review_Score'].mean():.2f}."
        if "device" in msg:
            return f"Most used device in Cluster {cluster_id} is **{subset['Device_Used'].mode()[0]}**."
        if "region" in msg:
            return f"Most customers in Cluster {cluster_id} are from **{subset['Customer_Region'].mode()[0]}**."
        if "gender" in msg:
            return f"Majority gender in Cluster {cluster_id} is **{subset['Gender'].mode()[0]}**."
        if "age" in msg:
            return f"Average age in Cluster {cluster_id} is {subset['Age'].mean():.1f} years."

    return "🤖 Sorry, I didn't understand that. Try asking about a product or cluster."

# Main Chat UI
st.title("🛍️ Customer Insight Chatbot")
st.markdown("Ask about clusters, products, spending, or income.")

chat_history = st.session_state.topics[st.session_state.active_topic]
for sender, msg in chat_history:
    if sender == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")

def submit():
    user_input = st.session_state.user_input
    if user_input:
        reply = cluster_aware_response(user_input)
        chat_history.append(("user", user_input))
        chat_history.append(("bot", reply))
        st.session_state.user_input = ""

st.text_input("Your question", key="user_input", on_change=submit)
