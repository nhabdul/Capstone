import streamlit as st
import pandas as pd
import numpy as np

# Load your preprocessed dataset
df = pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

# Initialize session state for memory
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_cluster" not in st.session_state:
    st.session_state.last_cluster = None
if "last_product" not in st.session_state:
    st.session_state.last_product = None

# Get unique product categories
available_categories = sorted(df["Product_Category"].dropna().unique().tolist())

# Title and sidebar
st.set_page_config(page_title="Customer Insight Chatbot", layout="wide")
st.sidebar.title("🧠 Chat History")
st.sidebar.info("This chatbot remembers your last product or cluster context.")

st.title("📊 Customer Insight Chatbot")

# Display previous messages
for msg in st.session_state.messages:
    role, content = msg["role"], msg["content"]
    align = "💬 You:" if role == "user" else "🤖 Bot:"
    st.markdown(f"**{align}** {content}")

# Chat input
user_input = st.text_input("Type your question here", key="user_input")

# --- Core Logic ---
def cluster_aware_response(user_msg):
    msg = user_msg.lower()
    response = "Sorry, I couldn't understand your request."

    # 1. Ask about available categories
    if ("product" in msg and "categor" in msg) or "available categories" in msg:
        return "The available product categories are:\n- " + "\n- ".join(available_categories)

    # 2. Ask who buys what
    elif "who" in msg and "buy" in msg:
        for category in available_categories:
            if category.lower() in msg:
                cluster_id = df[df["Product_Category"] == category]["Cluster"].mode().iloc[0]
                st.session_state.last_product = category
                st.session_state.last_cluster = cluster_id
                return f"Customers in **Cluster {cluster_id}** most frequently purchase **{category}** products."
        return "Please specify a valid product category like Fashion, Electronics, etc."

    # 3. Ask about follow-up to cluster
    elif any(kw in msg for kw in ["income", "salary", "spend", "score", "order", "review", "device", "region", "gender"]):
        cluster_id = st.session_state.last_cluster
        if cluster_id is None:
            return "Please ask about a product or cluster first so I know who you're referring to."

        subset = df[df["Cluster"] == cluster_id]
        if "income" in msg or "salary" in msg:
            return f"Average income in Cluster {cluster_id} is ${subset['Annual_Income'].mean():,.2f}."
        elif "spend" in msg:
            return f"Average spending score in Cluster {cluster_id} is {subset['Spending_Score'].mean():.2f}."
        elif "order" in msg:
            return f"Average number of orders in Cluster {cluster_id} is {subset['Number_of_Orders'].mean():.2f}."
        elif "review" in msg:
            return f"Average review score in Cluster {cluster_id} is {subset['Review_Score'].mean():.2f}."
        elif "device" in msg:
            mode = subset["Device_Used"].mode().iloc[0]
            return f"The most common device in Cluster {cluster_id} is **{mode}**."
        elif "region" in msg:
            top = subset["Customer_Region"].mode().iloc[0]
            return f"Most customers in Cluster {cluster_id} are from **{top}** region."
        elif "gender" in msg:
            top = subset["Gender"].mode().iloc[0]
            return f"Most customers in Cluster {cluster_id} are **{top}**."

    # 4. Ask about a specific cluster
    elif "cluster" in msg:
        import re
        match = re.search(r"cluster\s*(\d+)", msg)
        if match:
            cluster_id = int(match.group(1))
            if cluster_id in df["Cluster"].unique():
                st.session_state.last_cluster = cluster_id
                return f"You're now viewing insights for **Cluster {cluster_id}**. Ask about their income, spending, or preferences!"
            else:
                return f"Cluster {cluster_id} doesn't exist."
        return "Please specify a cluster number, like 'Cluster 1'."

    return response

# --- Process input ---
if user_input and "input_processed" not in st.session_state:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_response = cluster_aware_response(user_input)
    st.session_state.messages.append({"role": "bot", "content": bot_response})
    st.session_state.input_processed = True
    st.rerun()

# Reset after rerun
if "input_processed" in st.session_state:
    del st.session_state["input_processed"]
