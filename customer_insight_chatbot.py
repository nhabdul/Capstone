import streamlit as st
import pandas as pd
import re

# Load cluster summary from uploaded CSV or preprocessed DataFrame
df = pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

# Compute summary only once
cluster_summary = df.groupby("Cluster").agg({
    "Annual_Income": "mean",
    "Spending_Score": "mean",
    "Average_Order_Value": "mean",
    "Number_of_Orders": "mean",
    "Review_Score": "mean",
    "Preferred_Payment_Method": lambda x: x.mode()[0] if not x.mode().empty else "N/A",
    "Device_Used": lambda x: x.mode()[0] if not x.mode().empty else "N/A",
    "Product_Category": lambda x: x.mode()[0] if not x.mode().empty else "N/A",
    "Age": "mean"
}).round(2)

# Category sets for general questions
product_categories = sorted(df["Product_Category"].dropna().unique())
payment_methods = sorted(df["Preferred_Payment_Method"].dropna().unique())
delivery_options = sorted(df["Preferred_Delivery_Option"].dropna().unique())
device_types = sorted(df["Device_Used"].dropna().unique())
customer_regions = sorted(df["Customer_Region"].dropna().unique())
age_groups = sorted(df["Age_Group"].dropna().unique())
clusters = sorted(df["Cluster"].dropna().unique())

# Free-text response function
def chatbot_response(user_input):
    user_input = user_input.lower()
    cluster_match = re.search(r'cluster\s*(\d+)', user_input)
    cluster_number = int(cluster_match.group(1)) if cluster_match else None

    if cluster_number is not None and cluster_number in cluster_summary.index:
        row = cluster_summary.loc[cluster_number]
        return (
            f"🧠 **Cluster {cluster_number} Overview**\n"
            f"- Average Income: ${row['Annual_Income']}\n"
            f"- Spending Score: {row['Spending_Score']}\n"
            f"- Avg Order Value: ${row['Average_Order_Value']}\n"
            f"- Orders per Customer: {row['Number_of_Orders']}\n"
            f"- Average Review Score: {row['Review_Score']}\n"
            f"- Age: {round(row['Age'])} years old\n"
            f"- Most used payment method: {row['Preferred_Payment_Method']}\n"
            f"- Most used device: {row['Device_Used']}\n"
            f"- Common product: {row['Product_Category']}"
        )
    elif "product category" in user_input:
        return "📦 Available Product Categories:\n" + "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(product_categories)])
    elif "payment method" in user_input:
        return "💳 Payment Methods:\n" + "\n".join([f"• {m}" for m in payment_methods])
    elif "delivery" in user_input:
        return "🚚 Delivery Options:\n" + "\n".join([f"• {d}" for d in delivery_options])
    elif "device" in user_input:
        return "📱 Devices Used:\n" + "\n".join([f"• {d}" for d in device_types])
    elif "region" in user_input:
        return "🌍 Customer Regions:\n" + "\n".join([f"• {r}" for r in customer_regions])
    elif "age group" in user_input:
        return "👥 Age Groups:\n" + "\n".join([f"• {a}" for a in age_groups])
    elif "cluster" in user_input:
        return f"There are {len(clusters)} clusters: {', '.join(map(str, clusters))}"
    else:
        return "🤖 I'm not sure how to help with that. Try asking about a specific cluster or customer attributes."

# Streamlit UI with chat history
st.set_page_config(page_title="Customer Insight Chatbot", layout="centered")
st.title("💬 Customer Insight Chatbot")

# Session state for chat history
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask a question about your customers:")

if user_input:
    response = chatbot_response(user_input)
    st.session_state.history.append((user_input, response))

# Display chat history
for q, a in st.session_state.history:
    st.markdown(f"**You:** {q}")
    st.markdown(f"{a}")

st.caption("Ask about clusters, product categories, devices, payment methods, etc.")
