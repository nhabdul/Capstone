import streamlit as st
import pandas as pd

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df_clusters = load_data()

# Helper: Get cluster details
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
        return (
            f"💡 Customers who purchase **{matched_product}** the most are in **Cluster {top_cluster}** "
            f"with **{count} customers**.\n\n"
            f"You can ask: 'Tell me more about Cluster {top_cluster}' to learn about them."
        )
    return None

def cluster_aware_response(user_input):
    input_lower = user_input.lower()
    if "cluster" in input_lower:
        for i in range(5):
            if f"{i}" in input_lower:
                return get_cluster_info(i)

    if ("product" in input_lower and "categor" in input_lower):
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

    return "🤖 Sorry, I didn't understand that. You can ask about clusters, products, payments, or devices."

# Sidebar: chat history by topic
st.sidebar.title("📂 Chat History")
if "topics" not in st.session_state:
    st.session_state.topics = {"Default": []}
if "active_topic" not in st.session_state:
    st.session_state.active_topic = "Default"

topic_choice = st.sidebar.radio("Choose a topic:", list(st.session_state.topics.keys()))
if topic_choice != st.session_state.active_topic:
    st.session_state.active_topic = topic_choice

new_topic = st.sidebar.text_input("Start new topic")
if st.sidebar.button("➕ Add Topic") and new_topic:
    st.session_state.topics[new_topic] = []
    st.session_state.active_topic = new_topic

# Main UI
st.title("🛍️ Customer Insight Chatbot")
st.markdown("Ask anything about clusters, products, income, or devices.")

chat_history = st.session_state.topics[st.session_state.active_topic]

# Display conversation above input
for sender, msg in chat_history:
    if sender == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")

# Input field with auto-clear
def submit():
    user_input = st.session_state.user_input
    if user_input:
        reply = cluster_aware_response(user_input)
        chat_history.append(("user", user_input))
        chat_history.append(("bot", reply))
        st.session_state.topics[st.session_state.active_topic] = chat_history
        st.session_state.user_input = ""  # Clear input after use

st.text_input("Your question", key="user_input", on_change=submit)
