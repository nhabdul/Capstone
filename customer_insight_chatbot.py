import streamlit as st
import pandas as pd
import datetime

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df_clusters = load_data()

# Initialize session state
today = datetime.datetime.now().strftime("%d %B %Y")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
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
    avg_age = subset['Age'].mean()
    return (
        f"Cluster {cluster_id} Overview:\n"
        f"- Avg Income: ${avg_income:,.2f}\n"
        f"- Spending Score: {avg_spend:.2f}\n"
        f"- Avg Age: {avg_age:.1f} years"
    )

def product_cluster_response(user_input):
    product_categories = df_clusters['Product_Category'].unique()
    for product in product_categories:
        if product.lower() in user_input.lower():
            matched_product = product
            filtered = df_clusters[df_clusters['Product_Category'] == matched_product]
            top_cluster = filtered['Cluster'].value_counts().idxmax()
            count = filtered['Cluster'].value_counts().max()
            st.session_state.last_cluster = top_cluster
            st.session_state.last_product = matched_product
            return f"Most customers who purchase {matched_product} are in Cluster {top_cluster} ({count} customers)."
    return None

def follow_up_on_cluster(user_input):
    cluster_id = st.session_state.last_cluster
    if cluster_id is None:
        return "Please ask about a specific product or cluster first."
    subset = df_clusters[df_clusters["Cluster"] == cluster_id]
    msg = user_input.lower()
    if "income" in msg:
        return f"Average income in Cluster {cluster_id} is ${subset['Annual_Income'].mean():,.2f}."
    elif "spending" in msg:
        return f"Spending score in Cluster {cluster_id} is {subset['Spending_Score'].mean():.2f}."
    elif "age" in msg:
        return f"Average age in Cluster {cluster_id} is {subset['Age'].mean():.1f} years."
    return "I'm not sure how to answer that. Try asking about income, age, or spending."

def chatbot_response(user_input):
    # Direct cluster query
    if "cluster" in user_input.lower():
        for i in range(10):
            if str(i) in user_input:
                return get_cluster_info(i)

    # Product to cluster query
    response = product_cluster_response(user_input)
    if response:
        return response

    # Follow up
    return follow_up_on_cluster(user_input)

# --- Streamlit UI ---
st.set_page_config(layout="centered")
st.title("🛍️ Simple Customer Chatbot")

for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Bot:** {message}")

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask me something about the customer data:", key="user_input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input:
        bot_reply = chatbot_response(user_input)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", bot_reply))
