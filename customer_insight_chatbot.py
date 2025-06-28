import streamlit as st
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Customer Insights Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Simplified CSS with auto-scroll
def get_css():
    return """
<style>
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .chat-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
        background-color: #fafafa;
        scroll-behavior: smooth;
    }
    
    .user-message {
        color: #007bff;
        padding: 10px 0;
        text-align: right;
        font-weight: 600;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 10px;
    }
    
    .bot-message {
        color: #333;
        padding: 10px 0;
        line-height: 1.6;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 10px;
    }
    
    .input-area {
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
        background-color: white;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>

<script>
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Auto-scroll when new messages are added
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
            setTimeout(scrollToBottom, 100);
        }
    });
});

// Start observing when the chat container is available
function startObserving() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        observer.observe(chatContainer, { childList: true, subtree: true });
        scrollToBottom(); // Initial scroll
    } else {
        setTimeout(startObserving, 100);
    }
}

// Start observing after DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserving);
} else {
    startObserving();
}
</script>
"""

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'last_cluster' not in st.session_state:
    st.session_state.last_cluster = None

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")

df_clusters = load_data()

# Helper Functions
def get_cluster_info(cluster_id):
    subset = df_clusters[df_clusters['Cluster'] == cluster_id]
    if subset.empty:
        return "❌ That cluster doesn't exist."
    
    st.session_state.last_cluster = cluster_id
    avg_income = subset['Annual_Income'].mean()
    avg_spend = subset['Spending_Score'].mean()
    avg_order_value = subset['Average_Order_Value'].mean()
    avg_orders = subset['Number_of_Orders'].mean()
    avg_review = subset['Review_Score'].mean()
    avg_age = subset['Age'].mean()
    top_device = subset['Device_Used'].mode()[0]
    top_payment = subset['Preferred_Payment_Method'].mode()[0]
    top_product = subset['Product_Category'].mode()[0]
    
    return f"""### 🧠 Cluster {cluster_id} Overview

• **Average Income:** ${avg_income:,.2f}
• **Spending Score:** {avg_spend:.1f}
• **Avg Order Value:** ${avg_order_value:.2f}
• **Orders per Customer:** {avg_orders:.2f}
• **Average Review Score:** {avg_review:.2f}
• **Age:** {avg_age:.1f} years
• **Top Payment Method:** {top_payment}
• **Top Device:** {top_device}
• **Popular Product:** {top_product}"""

def product_cluster_response(user_input):
    user_input_lower = user_input.lower()
    product_categories = df_clusters['Product_Category'].unique()
    
    for product in product_categories:
        if product.lower() in user_input_lower:
            filtered = df_clusters[df_clusters['Product_Category'] == product]
            cluster_counts = filtered['Cluster'].value_counts()
            top_cluster = cluster_counts.idxmax()
            count = cluster_counts.max()
            st.session_state.last_cluster = top_cluster
            
            return f"💡 **{product}** customers are mostly in **Cluster {top_cluster}** ({count} customers). Ask about this cluster for more details!"
    return None

def cluster_aware_response(user_input):
    input_lower = user_input.lower()

    # Handle cluster queries
    if "cluster" in input_lower:
        for i in range(4):
            if f"{i}" in input_lower:
                return get_cluster_info(i)
        
        if input_lower.strip() in ["cluster", "clusters"]:
            return "**Available Clusters:** 0, 1, 2, 3\n\nAsk about any specific cluster!"

    # Handle product categories
    if "product" in input_lower or "categories" in input_lower:
        categories = sorted(df_clusters['Product_Category'].unique())
        return "**Product Categories:**\n" + "\n".join([f"• {cat}" for cat in categories])

    # Handle payment methods
    if "payment" in input_lower:
        payments = sorted(df_clusters['Preferred_Payment_Method'].unique())
        return "**Payment Methods:**\n" + "\n".join([f"• {pay}" for pay in payments])
    
    # Handle devices
    if "device" in input_lower:
        devices = sorted(df_clusters['Device_Used'].unique())
        return "**Customer Devices:**\n" + "\n".join([f"• {dev}" for dev in devices])
    
    # Handle regions
    if "region" in input_lower:
        regions = sorted(df_clusters['Customer_Region'].unique())
        return "**Customer Regions:**\n" + "\n".join([f"• {reg}" for reg in regions])

    # Check for product-specific queries
    product_response = product_cluster_response(user_input)
    if product_response:
        return product_response

    # Follow-up questions about last cluster
    if st.session_state.last_cluster is not None:
        cluster_id = st.session_state.last_cluster
        subset = df_clusters[df_clusters["Cluster"] == cluster_id]
        
        if "income" in input_lower:
            return f"💰 Average income in Cluster {cluster_id}: ${subset['Annual_Income'].mean():,.2f}"
        elif "spend" in input_lower:
            return f"🛒 Average spending score in Cluster {cluster_id}: {subset['Spending_Score'].mean():.2f}"
        elif "order" in input_lower:
            return f"📦 Average orders in Cluster {cluster_id}: {subset['Number_of_Orders'].mean():.2f}"

    return "🤖 I can help with clusters (0-3), products, payments, devices, or regions. What would you like to know?"

# Apply CSS
st.markdown(get_css(), unsafe_allow_html=True)

# Main Layout
st.title("🤖 Customer Insights Chatbot")
st.markdown("Ask me about customer clusters, products, and spending patterns!")

# Create two columns
col1, col2 = st.columns([2, 1])

with col1:
    # Chat display area
    chat_content = []
    
    if not st.session_state.messages:
        chat_content.append('''
            <div class="bot-message">
                👋 Hello! I'm your Customer Insights Assistant.<br><br>
                <strong>Try asking:</strong><br>
                • "Tell me about cluster 1"<br>
                • "Show me product categories"<br>
                • "What payment methods are available?"<br>
                • "Electronics customers"
            </div>
        ''')
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            chat_content.append(f'<div class="user-message">You: {message["content"]}</div>')
        else:
            # Convert markdown to HTML for better display
            content = message["content"].replace('\n', '<br>').replace('**', '<strong>').replace('**', '</strong>')
            chat_content.append(f'<div class="bot-message">{content}</div>')
    
    st.markdown(f'<div class="chat-container" id="chat-container">{"".join(chat_content)}</div>', 
                unsafe_allow_html=True)
    
    # Input area
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Message",
            placeholder="Type your question here...",
            label_visibility="collapsed"
        )
        
        col_send, col_clear = st.columns([3, 1])
        with col_send:
            submit_button = st.form_submit_button("Send 📤", use_container_width=True)
        with col_clear:
            if st.form_submit_button("Clear 🗑️", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar with quick actions
with col2:
    st.markdown("### Quick Actions")
    
    if st.button("🧠 Show Clusters", use_container_width=True):
        user_input = "Show me available clusters"
        submit_button = True
    
    if st.button("🛍️ Product Categories", use_container_width=True):
        user_input = "Show me product categories"
        submit_button = True
    
    if st.button("💳 Payment Methods", use_container_width=True):
        user_input = "What payment methods are available?"
        submit_button = True
    
    if st.button("📱 Customer Devices", use_container_width=True):
        user_input = "What devices do customers use?"
        submit_button = True
    
    if st.button("🌍 Customer Regions", use_container_width=True):
        user_input = "Show me customer regions"
        submit_button = True
    
    # Recent conversations count
    if st.session_state.messages:
        st.markdown(f"**Conversation:** {len(st.session_state.messages)//2} exchanges")

# Process user input
if submit_button and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get bot response
    bot_response = cluster_aware_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Rerun to update display and trigger auto-scroll
    st.rerun()

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Ask about specific clusters (0-3), product categories, or customer behavior patterns!")
