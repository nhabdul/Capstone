import streamlit as st
import pandas as pd
import re

# Load preprocessed data
@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df = load_data()
valid_categories = df['Product_Category'].dropna().unique().tolist()

def extract_product_category(text):
    for category in valid_categories:
        if re.search(rf"\\b{category.lower()}\\b", text.lower()):
            return category
    return None

def cluster_aware_response(user_input):
    input_lower = user_input.lower()

    # Memory logic
    memory = st.session_state.get("memory", {})

    # Product category list
    if ("product" in input_lower and "categor" in input_lower) or "available categories" in input_lower:
        categories = sorted(valid_categories)
        return "The available product categories are:\n- " + "\n- ".join(categories)

    # Who spends the most in a product category
    if "spend" in input_lower and "most" in input_lower:
        category = extract_product_category(user_input)
        if category:
            cluster_spend = df[df['Product_Category'] == category].groupby('Cluster')['Spending_Score'].mean()
            top_cluster = cluster_spend.idxmax()
            st.session_state.memory = {'cluster': top_cluster, 'category': category}
            return f"Cluster {top_cluster} spends the most on {category} products."
        else:
            return "Could you specify which product category you're referring to?"

    # Follow-up: e.g., "What is their average income?"
    if any(word in input_lower for word in ["average", "typical", "mean"]):
        if "income" in input_lower and 'cluster' in memory:
            avg_income = df[df['Cluster'] == memory['cluster']]['Annual_Income'].mean()
            return f"The average income for customers in Cluster {memory['cluster']} is ${avg_income:,.2f}."
        if "age" in input_lower and 'cluster' in memory:
            avg_age = df[df['Cluster'] == memory['cluster']]['Age'].mean()
            return f"The average age for Cluster {memory['cluster']} is {avg_age:.1f} years."

    return "I'm not sure how to answer that yet, but I'm learning more every day!"

# Initialize chat session
st.set_page_config(page_title="Customer Insight Chatbot", layout="wide")
st.title("🛍️ Customer Insight Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# Display messages
for msg in st.session_state.messages:
    role = "🧑‍💼 You" if msg["role"] == "user" else "🤖 Bot"
    with st.chat_message(msg["role"]):
        st.markdown(f"**{role}:** {msg['content']}")

# Chat input field
user_input = st.text_input("Type your question here:", value=st.session_state.chat_input, key="chat_input_input")

# Process new input
if user_input and "input_processed" not in st.session_state:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_response = cluster_aware_response(user_input)
    st.session_state.messages.append({"role": "bot", "content": bot_response})
    st.session_state.input_processed = True
    st.session_state.chat_input = ""
    st.rerun()

# Clear processed flag after rerun
if "input_processed" in st.session_state:
    del st.session_state.input_processed
