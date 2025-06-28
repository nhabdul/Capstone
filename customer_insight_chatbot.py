import streamlit as st
import pandas as pd
from datetime import datetime

# Set page config for better layout
st.set_page_config(
    page_title="Customer Insights Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Chat container styling */
    .chat-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: transparent;
        margin: 10px 0;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* Message styling */
    .user-message {
        background-color: transparent;
        color: #007bff;
        padding: 10px 0;
        margin: 5px 0;
        text-align: right;
        word-wrap: break-word;
        font-weight: 600;
    }
    
    .bot-message {
        background-color: transparent;
        color: #333;
        padding: 10px 0;
        margin: 5px 0;
        word-wrap: break-word;
    }
    
    /* Input area styling */
    .input-container {
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        background-color: white;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        font-size: 18px;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    
    .history-item {
        background-color: #f1f3f4;
        padding: 8px;
        margin: 5px 0;
        border-radius: 5px;
        border-left: 3px solid #007bff;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .history-item:hover {
        background-color: #e3f2fd;
    }
    
    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message, .bot-message {
            margin-left: 5px;
            margin-right: 5px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_cluster' not in st.session_state:
    st.session_state.last_cluster = None
if 'last_product' not in st.session_state:
    st.session_state.last_product = None

# Load your data (replace with your actual data loading)
@st.cache_data
def load_data():
    # This is a placeholder - replace with your actual data loading
    # For demo purposes, creating sample data structure
    return pd.DataFrame({
        'Cluster': [0, 1, 2, 0, 1, 2] * 100,
        'Annual_Income': [50000, 75000, 100000, 55000, 80000, 95000] * 100,
        'Spending_Score': [20, 50, 80, 25, 55, 75] * 100,
        'Average_Order_Value': [100, 200, 300, 150, 250, 280] * 100,
        'Number_of_Orders': [5, 10, 15, 6, 12, 14] * 100,
        'Review_Score': [3.5, 4.0, 4.5, 3.8, 4.2, 4.3] * 100,
        'Age': [25, 35, 45, 28, 38, 42] * 100,
        'Device_Used': ['Mobile', 'Desktop', 'Tablet', 'Mobile', 'Desktop', 'Mobile'] * 100,
        'Preferred_Payment_Method': ['Credit Card', 'PayPal', 'Debit Card', 'Credit Card', 'PayPal', 'Credit Card'] * 100,
        'Product_Category': ['Electronics', 'Clothing', 'Books', 'Electronics', 'Home', 'Sports'] * 100,
        'Customer_Region': ['North', 'South', 'East', 'West', 'North', 'South'] * 100,
        'Gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female'] * 100
    })

# Load data
df_clusters = load_data()

# --- Helper Functions (from your provided code) ---
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
        st.session_state.last_cluster = top_cluster
        st.session_state.last_product = matched_product
        return (
            f"💡 Customers who purchase **{matched_product}** the most are in **Cluster {top_cluster}** "
            f"with **{count} customers**.\n\n"
            f"You can ask: 'Tell me more about Cluster {top_cluster}' to learn about them."
        )
    return None

def follow_up_on_last_cluster(user_input):
    msg = user_input.lower()
    cluster_id = st.session_state.last_cluster
    if cluster_id is None:
        return None
    subset = df_clusters[df_clusters["Cluster"] == cluster_id]

    if "income" in msg or "salary" in msg:
        return f"Average income in Cluster {cluster_id} is ${subset['Annual_Income'].mean():,.2f}."
    elif "spend" in msg:
        return f"Average spending score in Cluster {cluster_id} is {subset['Spending_Score'].mean():.2f}."
    elif "order" in msg:
        return f"Average number of orders in Cluster {cluster_id} is {subset['Number_of_Orders'].mean():.2f}."
    elif "review" in msg:
        return f"Average review score in Cluster {cluster_id} is {subset['Review_Score'].mean():.2f}."
    elif "device" in msg:
        return f"Most common device in Cluster {cluster_id} is **{subset['Device_Used'].mode().iloc[0]}**."
    elif "region" in msg:
        return f"Most customers in Cluster {cluster_id} are from **{subset['Customer_Region'].mode().iloc[0]}**."
    elif "gender" in msg:
        return f"Most customers in Cluster {cluster_id} are **{subset['Gender'].mode().iloc[0]}**."
    return None

def cluster_aware_response(user_input):
    input_lower = user_input.lower()

    if "cluster" in input_lower:
        for i in range(10):
            if f"{i}" in input_lower:
                return get_cluster_info(i)

    if ("product" in input_lower and "categor" in input_lower) or "available categories" in input_lower:
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

    follow_up = follow_up_on_last_cluster(user_input)
    if follow_up:
        return follow_up

    return "🤖 Sorry, I didn't understand that. Try asking about a product, a cluster, or spending habits."

# --- Main App Layout ---
st.title("Customer Insights Chatbot")
st.markdown("Ask me about customer clusters, products, and spending patterns!")

# Create layout with sidebar and main content
col1, col2 = st.columns([1, 3])

# Sidebar for chat history
with col1:
    st.markdown('<div class="sidebar-header">💬 Chat History</div>', unsafe_allow_html=True)
    
    # Add clear history button
    if st.button("🗑️ Clear History", key="clear_history"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        for i, (timestamp, user_msg, bot_msg) in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💬 {timestamp}", expanded=False):
                st.markdown(f"**You:** {user_msg[:50]}...")
                st.markdown(f"**Bot:** {bot_msg[:50]}...")
                if st.button("🔄 Reload", key=f"reload_{i}"):
                    # Add the conversation back to current messages
                    st.session_state.messages.append({"role": "user", "content": user_msg})
                    st.session_state.messages.append({"role": "assistant", "content": bot_msg})
                    st.rerun()

# Main chat area
with col2:
    # Chat container with custom styling
    chat_content = []
    
    # Build chat content
    if not st.session_state.messages:
        chat_content.append("""
        <div class="bot-message">
            Hello! I'm your Customer Insights Assistant. I can help you explore customer data and clusters.
            <br><br>
            Try asking me:
            <br>• "Tell me about cluster 1"
            <br>• "Which customers buy electronics?"
            <br>• "Show me product categories"
            <br>• "What payment methods are popular?"
        </div>
        """)
    
    # Add all messages to chat content
    for message in st.session_state.messages:
        if message["role"] == "user":
            chat_content.append(f'<div class="user-message">{message["content"]}</div>')
        else:
            chat_content.append(f'<div class="bot-message">{message["content"]}</div>')
    
    # Display everything inside the bordered container
    st.markdown(f'''
    <div class="chat-container">
        {"".join(chat_content)}
    </div>
    ''', unsafe_allow_html=True)
    
    # Input area with custom styling
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # Create input form that responds to Enter key
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Type your message here...",
            key="user_input",
            placeholder="Ask me about clusters, products, or customer data...",
            label_visibility="collapsed"
        )
        
        col_send, col_examples = st.columns([1, 4])
        with col_send:
            submit_button = st.form_submit_button("Send 📤", use_container_width=True)
        with col_examples:
            st.markdown("*Press Enter to send*")
    
    # Quick action buttons
    st.markdown("**Quick Actions:**")
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    
    with btn_col1:
        if st.button("Clusters", key="clusters"):
            user_input = "Show me available clusters"
            submit_button = True
    
    with btn_col2:
        if st.button("🛍️ Products", key="products"):
            user_input = "Show me product categories"
            submit_button = True
    
    with btn_col3:
        if st.button("💳 Payments", key="payments"):
            user_input = "What payment methods are available?"
            submit_button = True
    
    with btn_col4:
        if st.button("📱 Devices", key="devices"):
            user_input = "What devices do customers use?"
            submit_button = True
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process user input
if submit_button and user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get bot response using your helper function
    bot_response = cluster_aware_response(user_input)
    
    # Add bot response to chat
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Add to chat history with timestamp
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append((timestamp, user_input, bot_response))
    
    # Keep only last 20 conversations in history
    if len(st.session_state.chat_history) > 20:
        st.session_state.chat_history = st.session_state.chat_history[-20:]
    
    # Rerun to update the display
    st.rerun()

# Footer with instructions
st.markdown("---")
st.markdown("""
**Instructions:**
- Type your question and press Enter or click Send
- Use the sidebar to view and reload previous conversations
- Try the quick action buttons for common queries
- Ask about specific clusters (0-3), products, or customer behavior
""")
