import streamlit as st
import pandas as pd
import re

# Load the clustered dataset
df = pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

# Define available product categories
available_categories = ['Beauty', 'Electronics', 'Fashion', 'Home', 'Sports']

# Helper: Get cluster with highest spend per category
def get_top_cluster_by_spend(category):
    filtered = df[df['Product_Category'].str.lower() == category.lower()]
    if filtered.empty:
        return None, None
    cluster_avg = filtered.groupby('Cluster')['Spending_Score'].mean().idxmax()
    avg_income = filtered[df['Cluster'] == cluster_avg]['Annual_Income'].mean()
    return cluster_avg, avg_income

# Helper: Respond to user query
def cluster_aware_response(user_input):
    user_input_lower = user_input.lower()

    if "product category" in user_input_lower or "categories" in user_input_lower:
        return "The available product categories are:\n\n- Beauty\n- Electronics\n- Fashion\n- Home\n- Sports"

    for category in available_categories:
        if category.lower() in user_input_lower:
            cluster, income = get_top_cluster_by_spend(category)
            if cluster is not None:
                st.session_state.memory = {"last_cluster": cluster, "last_category": category}
                return f"Customers in **Cluster {cluster}** spend the most on **{category}**. Their average annual income is **${income:,.2f}**."
            else:
                return f"Sorry, I couldn't find spending data for {category}."

    # Contextual follow-up handling
    mem = st.session_state.memory
    if any(k in user_input_lower for k in ["income", "salary"]):
        if "last_cluster" in mem:
            cluster = mem["last_cluster"]
            income = df[df['Cluster'] == cluster]['Annual_Income'].mean()
            return f"The average annual income for Cluster {cluster} is **${income:,.2f}**."
        else:
            return "Please ask a product-related question first so I can recall the correct cluster."

    return "I'm not sure how to help with that. You can ask me which cluster spends the most on a product category like 'Beauty' or 'Electronics'."

# --- Streamlit App ---
st.set_page_config(page_title="Customer Insights Chatbot", layout="wide")
st.title("🛍️ Customer Insights Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""
if "memory" not in st.session_state:
    st.session_state.memory = {}
if "chat_topics" not in st.session_state:
    st.session_state.chat_topics = {}
if "current_topic" not in st.session_state:
    st.session_state.current_topic = "New Chat"

# Sidebar: Chat topics
with st.sidebar:
    st.header("💬 Chat Topics")
    topic_names = list(st.session_state.chat_topics.keys())
    selected = st.selectbox("Choose a topic", ["New Chat"] + topic_names, key="topic_selector")
    if selected != "New Chat":
        st.session_state.current_topic = selected
        st.session_state.messages = st.session_state.chat_topics[selected].copy()
    else:
        st.session_state.messages = []

# Chat interface
for msg in st.session_state.messages:
    role = "🧑‍💼 You" if msg["role"] == "user" else "🤖 Bot"
    with st.chat_message(role):
        st.markdown(msg["content"])

# Input form
user_input = st.chat_input("Ask a question about customer segments or products...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = cluster_aware_response(user_input)
    st.session_state.messages.append({"role": "bot", "content": response})
    st.session_state.chat_input = ""
    # Save topic
    st.session_state.chat_topics[st.session_state.current_topic] = st.session_state.messages.copy()
    st.rerun()
