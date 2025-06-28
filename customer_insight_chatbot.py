# chatbot_with_memory.py
import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df_clusters = load_data()

# Initialize session memory
if "topics" not in st.session_state:
    st.session_state.topics = {"Default": []}
if "active_topic" not in st.session_state:
    st.session_state.active_topic = "Default"
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = {}

# Helper: Get cluster info
def get_cluster_info(cluster_id):
    subset = df_clusters[df_clusters['Cluster'] == cluster_id]
    if subset.empty:
        return "❌ That cluster doesn't exist."
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

# Context-aware logic
def cluster_aware_response(user_input):
    input_lower = user_input.lower()
    memory = st.session_state.chat_memory

    # Check direct cluster query
    if "cluster" in input_lower:
        for i in range(5):
            if f"{i}" in input_lower:
                memory["last_cluster"] = i
                return get_cluster_info(i)

    # Product category question
    if "product" in input_lower and "categor" in input_lower:
        categories = df_clusters['Product_Category'].unique()
        return "**Available Product Categories:**\n" + "\n".join(f"- {c}" for c in sorted(categories))

    # Ask about who buys what
    product_categories = df_clusters['Product_Category'].unique()
    for product in product_categories:
        if product.lower() in input_lower:
            subset = df_clusters[df_clusters['Product_Category'] == product]
            top_cluster = subset['Cluster'].value_counts().idxmax()
            memory["last_product"] = product
            memory["last_cluster"] = top_cluster
            return (
                f"💡 Customers who purchase **{product}** the most are in **Cluster {top_cluster}**.\n\n"
                f"You can ask about this cluster or their spending behavior."
            )

    # Follow-up Q: e.g., what's their income?
    if any(word in input_lower for word in ["income", "salary"]):
        cluster_id = memory.get("last_cluster")
        if cluster_id is not None:
            income = df_clusters[df_clusters['Cluster'] == cluster_id]['Annual_Income'].mean()
            return f"🧾 The average income for Cluster {cluster_id} is **${income:,.2f}**."

    if "spending" in input_lower:
        cluster_id = memory.get("last_cluster")
        if cluster_id is not None:
            spend = df_clusters[df_clusters['Cluster'] == cluster_id]['Spending_Score'].mean()
            return f"💸 Cluster {cluster_id} has an average spending score of **{spend:.1f}**."

    return "🤖 I didn't understand that. Try asking about products, clusters, or spending."

# UI Layout
st.sidebar.title("📂 Chat History")
topic_choice = st.sidebar.radio("Choose a topic:", list(st.session_state.topics.keys()))
if topic_choice != st.session_state.active_topic:
    st.session_state.active_topic = topic_choice

new_topic = st.sidebar.text_input("Start new topic")
if st.sidebar.button("➕ Add Topic") and new_topic:
    st.session_state.topics[new_topic] = []
    st.session_state.active_topic = new_topic

st.title("🧠 Customer Insight Chatbot with Memory")
chat_history = st.session_state.topics[st.session_state.active_topic]

for sender, msg in chat_history:
    if sender == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")

# Handle input

def submit():
    user_input = st.session_state.user_input
    if user_input:
        reply = cluster_aware_response(user_input)
        chat_history.append(("user", user_input))
        chat_history.append(("bot", reply))
        st.session_state.user_input = ""

st.text_input("Your question", key="user_input", on_change=submit)
