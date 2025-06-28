import streamlit as st
import pandas as pd
import datetime

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df = load_data()

# Session state setup
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_cluster" not in st.session_state:
    st.session_state.last_cluster = None
if "last_product" not in st.session_state:
    st.session_state.last_product = None

# Question handling

def handle_question(question):
    q = question.lower()
    
    if "available categories" in q or ("product" in q and "category" in q):
        categories = sorted(df['Product_Category'].unique())
        return "\n".join(["Available Product Categories:"] + [f"- {c}" for c in categories])

    elif "cluster" in q:
        for i in range(10):
            if f"cluster {i}" in q:
                return describe_cluster(i)

    elif any(p in q for p in ["income", "spend", "order", "review", "device", "region", "gender"]):
        return follow_up_info(q)

    elif any(p.lower() in q for p in df['Product_Category'].unique()):
        return product_cluster_insight(q)

    return "🤖 Sorry, I didn’t understand that. Try asking about a cluster, product category, or spending habits."


def describe_cluster(cluster_id):
    subset = df[df['Cluster'] == cluster_id]
    if subset.empty:
        return "❌ Cluster not found."
    st.session_state.last_cluster = cluster_id
    return f"🧠 Cluster {cluster_id} — Avg Income: ${subset['Annual_Income'].mean():,.2f}, Top Product: {subset['Product_Category'].mode()[0]}"


def product_cluster_insight(question):
    for product in df['Product_Category'].unique():
        if product.lower() in question:
            filtered = df[df['Product_Category'] == product]
            top_cluster = filtered['Cluster'].value_counts().idxmax()
            st.session_state.last_cluster = top_cluster
            st.session_state.last_product = product
            return f"💡 Customers who buy {product} are mostly in Cluster {top_cluster}."
    return None


def follow_up_info(question):
    cluster = st.session_state.last_cluster
    if cluster is None:
        return "Please ask about a cluster first."
    subset = df[df['Cluster'] == cluster]
    q = question.lower()
    if "income" in q:
        return f"Avg Income in Cluster {cluster}: ${subset['Annual_Income'].mean():,.2f}"
    if "spend" in q:
        return f"Avg Spending Score: {subset['Spending_Score'].mean():.1f}"
    if "order" in q:
        return f"Avg Orders: {subset['Number_of_Orders'].mean():.2f}"
    if "review" in q:
        return f"Avg Review Score: {subset['Review_Score'].mean():.2f}"
    if "device" in q:
        return f"Most common device: {subset['Device_Used'].mode()[0]}"
    if "region" in q:
        return f"Top Region: {subset['Customer_Region'].mode()[0]}"
    if "gender" in q:
        return f"Most customers are: {subset['Gender'].mode()[0]}"
    return "Couldn’t fetch detail."

# Streamlit Layout
st.set_page_config(layout="centered")
st.title("🛍️ Customer Chatbot")

# Chat display
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")

# Input form
with st.form(key="chat_form"):
    user_input = st.text_input("Type your question here...")
    submit = st.form_submit_button("Send")

    if submit and user_input:
        response = handle_question(user_input)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", response))
