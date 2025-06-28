import streamlit as st
import pandas as pd
import re

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")
    return df

df = load_data()

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

# Sidebar for chat history
with st.sidebar:
    st.header("💬 Chat Topics")
    topic_names = list(st.session_state.chat_topics.keys())
    selected = st.selectbox("Choose a topic", ["New Chat"] + topic_names, key="topic_selector")

    if selected != "New Chat":
        st.session_state.current_topic = selected
        st.session_state.messages = st.session_state.chat_topics[selected].copy()
    else:
        st.session_state.messages = []

# Function to extract category from question
def extract_product_category(text, valid_categories):
    for category in valid_categories:
        if re.search(rf"\\b{category.lower()}\\b", text.lower()):
            return category
    return None

# Cluster-aware chatbot response
def cluster_aware_response(user_input):
    input_lower = user_input.lower()
    valid_categories = df["Product_Category"].unique().tolist()

    # List categories
    if "product category" in input_lower:
        categories = sorted(valid_categories)
        return "Available product categories include:\n" + "\n".join(f"- {cat}" for cat in categories)

    # Who spends most in [category]?
    if "spend" in input_lower and "most" in input_lower:
        category = extract_product_category(user_input, valid_categories)
        if category:
            top_cluster = df[df['Product_Category'] == category].groupby('Cluster')["Spending_Score"].mean().idxmax()
            st.session_state.memory = {'cluster': top_cluster, 'category': category}
            return f"Cluster {top_cluster} spends the most on {category} products."
        else:
            return "Could you specify which product category you're referring to?"

    # Follow-up: what's their average income?
    if "income" in input_lower or "salary" in input_lower:
        if "cluster" in st.session_state.memory:
            cl = st.session_state.memory['cluster']
            avg_income = df[df['Cluster'] == cl]['Annual_Income'].mean()
            return f"The average income of Cluster {cl} is ${avg_income:,.2f}."
        return "Can you clarify which cluster you're referring to?"

    # Catch-all
    return "I'm sorry, I couldn't understand your question. Try asking about spending habits or customer profiles."

# Display chat
st.title("🛍️ Customer Segment Chatbot")

# Render chat history
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask me something about the customer segments...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = cluster_aware_response(user_input)
    st.session_state.messages.append({"role": "bot", "content": response})
    st.session_state.chat_input = ""
    # Save conversation under current topic
    st.session_state.chat_topics[st.session_state.current_topic] = st.session_state.messages.copy()
    st.rerun()
