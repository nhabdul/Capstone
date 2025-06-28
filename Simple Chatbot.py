
import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Load data
df = pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

# Summarize by cluster
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

# Categories
product_categories = sorted(df["Product_Category"].dropna().unique())
payment_methods = sorted(df["Preferred_Payment_Method"].dropna().unique())
delivery_options = sorted(df["Preferred_Delivery_Option"].dropna().unique())
device_types = sorted(df["Device_Used"].dropna().unique())
customer_regions = sorted(df["Customer_Region"].dropna().unique())
age_groups = sorted(df["Age_Group"].dropna().unique())
clusters = sorted(df["Cluster"].dropna().unique())

# Bot response
def chatbot_response(user_input):
    user_input = user_input.lower()
    cluster_match = re.search(r'cluster\s*(\d+)', user_input)
    cluster_number = int(cluster_match.group(1)) if cluster_match else None

    if cluster_number is not None and cluster_number in cluster_summary.index:
        row = cluster_summary.loc[cluster_number]
        return (
            f"🧠 **Cluster {cluster_number} Overview**\n"
            f"- Average Income: ${{row['Annual_Income']}}\n"
            f"- Spending Score: ${{row['Spending_Score']}}\n"
            f"- Avg Order Value: ${{row['Average_Order_Value']}}\n"
            f"- Orders per Customer: ${{row['Number_of_Orders']}}\n"
            f"- Average Review Score: ${{row['Review_Score']}}\n"
            f"- Age: {{round(row['Age'])}} years old\n"
            f"- Most used payment method: ${{row['Preferred_Payment_Method']}}\n"
            f"- Most used device: ${{row['Device_Used']}}\n"
            f"- Common product: ${{row['Product_Category']}}"
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

# Page config
st.set_page_config(page_title="Customer Insight Chatbot", layout="centered")
st.markdown("<h1 style='text-align:center;'>💬 Customer Insight Chatbot</h1>", unsafe_allow_html=True)

# Chat state
if "history" not in st.session_state:
    st.session_state.history = []

# Style block
st.markdown("""
<style>
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 10px;
    background-color: #f9f9f9;
    margin-bottom: 10px;
}
.user-msg {
    color: #000;
    font-weight: bold;
}
.bot-msg {
    color: #333;
    background-color: #e0e0e0;
    padding: 10px;
    border-radius: 10px;
    margin-top: 5px;
    margin-bottom: 15px;
}
.timestamp {
    font-size: 0.75rem;
    color: #777;
    margin-bottom: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# Display messages first
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for sender, msg, time in st.session_state.history:
    if sender == "You":
        st.markdown(f'<div class="timestamp">{time}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-msg">🧑‍💼 <b>You:</b> {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="timestamp">{time}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-msg">🤖 <b>Bot:</b><br>{msg}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input comes after
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your question:")
    submit = st.form_submit_button("Send")

if submit and user_input:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = chatbot_response(user_input)
    st.session_state.history.insert(0, ("Bot", response, now))
    st.session_state.history.insert(0, ("You", user_input, now))

st.caption("Ask about clusters, products, devices, payments, etc.")
