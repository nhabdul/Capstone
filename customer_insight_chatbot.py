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
def get_theme_css(dark_mode=False):
    if dark_mode:
        return """
<style>
    /* Dark theme variables */
    :root {
        --bg-color: #1e1e1e;
        --text-color: #ffffff;
        --border-color: #444444;
        --user-color: #4a9eff;
        --bot-color: #ffffff;
        --container-bg: #2d2d2d;
        --input-bg: #333333;
    }
    
    /* Main app background */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Chat container styling */
    .chat-container {
        border: 2px solid var(--border-color);
        border-radius: 10px 10px 0 0;
        padding: 20px;
        background-color: transparent;
        margin: 0;
        margin-bottom: 0;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* Message styling */
    .user-message {
        background-color: transparent;
        color: var(--user-color);
        padding: 10px 0;
        margin: 5px 0;
        text-align: right;
        word-wrap: break-word;
        font-weight: 600;
        font-size: 16px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .bot-message {
        background-color: transparent;
        color: var(--bot-color);
        padding: 10px 0;
        margin: 5px 0;
        word-wrap: break-word;
        font-size: 16px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }
    
    /* Input area styling */
    .input-container {
        border: 2px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 10px;
        margin: 0;
        margin-top: 0;
        background-color: var(--input-bg);
    }
    
    /* Remove spacing between containers */
    .element-container:has(.chat-container) + .element-container:has(.input-container) {
        margin-top: 0 !important;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        font-size: 18px;
        font-weight: bold;
        color: var(--text-color);
        margin-bottom: 10px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .history-item {
        background-color: var(--container-bg);
        padding: 8px;
        margin: 5px 0;
        border-radius: 5px;
        border-left: 3px solid var(--user-color);
        cursor: pointer;
        transition: background-color 0.3s;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .history-item:hover {
        background-color: #404040;
    }
    
    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove default streamlit spacing */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message, .bot-message {
            margin-left: 5px;
            margin-right: 5px;
        }
    }
</style>
"""
    else:
        return """
<style>
    /* Light theme variables */
    :root {
        --bg-color: #ffffff;
        --text-color: #333333;
        --border-color: #e0e0e0;
        --user-color: #007bff;
        --bot-color: #ffffff;
        --container-bg: #f1f3f4;
        --input-bg: #ffffff;
    }
    
    /* Main app styling */
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Chat container styling */
    .chat-container {
        border: 2px solid var(--border-color);
        border-radius: 10px 10px 0 0;
        padding: 20px;
        background-color: transparent;
        margin: 0;
        margin-bottom: 0;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* Message styling */
    .user-message {
        background-color: transparent;
        color: var(--user-color);
        padding: 10px 0;
        margin: 5px 0;
        text-align: right;
        word-wrap: break-word;
        font-weight: 600;
        font-size: 16px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .bot-message {
        background-color: transparent;
        color: var(--bot-color);
        padding: 10px 0;
        margin: 5px 0;
        word-wrap: break-word;
        font-size: 16px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }
    
    /* Input area styling */
    .input-container {
        border: 2px solid var(--user-color);
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 10px;
        margin: 0;
        margin-top: 0;
        background-color: var(--input-bg);
    }
    
    /* Remove spacing between containers */
    .element-container:has(.chat-container) + .element-container:has(.input-container) {
        margin-top: 0 !important;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        font-size: 18px;
        font-weight: bold;
        color: var(--text-color);
        margin-bottom: 10px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .history-item {
        background-color: var(--container-bg);
        padding: 8px;
        margin: 5px 0;
        border-radius: 5px;
        border-left: 3px solid var(--user-color);
        cursor: pointer;
        transition: background-color 0.3s;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .history-item:hover {
        background-color: #e3f2fd;
    }
    
    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove default streamlit spacing */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message, .bot-message {
            margin-left: 5px;
            margin-right: 5px;
        }
    }
</style>
"""

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_cluster' not in st.session_state:
    st.session_state.last_cluster = None
if 'last_product' not in st.session_state:
    st.session_state.last_product = None
if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = False

# Helper function to group chat history by time
def group_chat_history(chat_history):
    if not chat_history:
        return []
    
    grouped = []
    current_group = []
    current_time = None
    
    for timestamp, user_msg, bot_msg in chat_history:
        # Parse timestamp to datetime for comparison
        chat_time = datetime.strptime(timestamp, "%H:%M")
        
        if current_time is None:
            current_time = chat_time
            current_group = [(timestamp, user_msg, bot_msg)]
        else:
            # Check if the chat is within 10 minutes of the current group
            time_diff = abs((chat_time - current_time).total_seconds())
            if time_diff <= 600:  # 10 minutes = 600 seconds
                current_group.append((timestamp, user_msg, bot_msg))
            else:
                # Start a new group
                grouped.append(current_group)
                current_group = [(timestamp, user_msg, bot_msg)]
                current_time = chat_time
    
    # Add the last group
    if current_group:
        grouped.append(current_group)
    
    return grouped

# Apply theme CSS after session state is initialized
st.markdown(get_theme_css(st.session_state.dark_theme), unsafe_allow_html=True)

# Load your data (replace with your actual data loading)
@st.cache_data
def load_data():
    # This is a placeholder - replace with your actual data loading
    # For demo purposes, creating sample data structure with 4 clusters
    return pd.DataFrame({
        'Cluster': [0, 1, 2, 3, 0, 1, 2, 3] * 60,
        'Annual_Income': [45000, 65000, 85000, 105000, 125000, 50000, 70000, 90000, 110000, 130000] * 60,
        'Spending_Score': [15, 35, 55, 75, 95, 20, 40, 60, 80, 90] * 60,
        'Average_Order_Value': [80, 150, 220, 290, 360, 100, 180, 250, 320, 380] * 60,
        'Number_of_Orders': [3, 7, 11, 15, 19, 5, 9, 13, 17, 21] * 60,
        'Review_Score': [3.2, 3.7, 4.1, 4.4, 4.7, 3.5, 3.9, 4.2, 4.5, 4.8] * 60,
        'Age': [22, 32, 42, 52, 62, 25, 35, 45, 55, 65] * 60,
        'Device_Used': ['Mobile', 'Desktop', 'Tablet', 'Mobile', 'Desktop', 'Mobile', 'Tablet', 'Desktop', 'Mobile', 'Tablet'] * 60,
        'Preferred_Payment_Method': ['Credit Card', 'PayPal', 'Debit Card', 'Apple Pay', 'Google Pay', 'Credit Card', 'PayPal', 'Debit Card', 'Apple Pay', 'Google Pay'] * 60,
        'Product_Category': ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty', 'Electronics', 'Clothing', 'Books', 'Home'] * 60,
        'Customer_Region': ['North', 'South', 'East', 'West', 'Central', 'North', 'South', 'East', 'West', 'Central'] * 60,
        'Gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'] * 60
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
        f"### 🧠 Cluster {cluster_id} Overview\n\n"
        f"• Average Income: ${avg_income:,.2f}\n\n"
        f"• Spending Score: {avg_spend:.1f}\n\n"
        f"• Avg Order Value: ${avg_order_value:.2f}\n\n"
        f"• Orders per Customer: {avg_orders:.2f}\n\n"
        f"• Average Review Score: {avg_review:.2f}\n\n"
        f"• Age: {avg_age:.1f} years\n\n"
        f"• Most used payment method: **{top_payment}**\n\n"
        f"• Most used device: **{top_device}**\n\n"
        f"• Common product: **{top_product}**"
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
        return f"• Average income in Cluster {cluster_id} is ${subset['Annual_Income'].mean():,.2f}."
    elif "spend" in msg:
        return f"• Average spending score in Cluster {cluster_id} is {subset['Spending_Score'].mean():.2f}."
    elif "order" in msg:
        return f"• Average number of orders in Cluster {cluster_id} is {subset['Number_of_Orders'].mean():.2f}."
    elif "review" in msg:
        return f"• Average review score in Cluster {cluster_id} is {subset['Review_Score'].mean():.2f}."
    elif "device" in msg:
        return f"• Most common device in Cluster {cluster_id} is **{subset['Device_Used'].mode().iloc[0]}**."
    elif "region" in msg:
        return f"• Most customers in Cluster {cluster_id} are from **{subset['Customer_Region'].mode().iloc[0]}**."
    elif "gender" in msg:
        return f"• Most customers in Cluster {cluster_id} are **{subset['Gender'].mode().iloc[0]}**."
    return None

def cluster_aware_response(user_input):
    input_lower = user_input.lower()

    # Handle cluster queries
    if "cluster" in input_lower:
        # Check for specific cluster numbers
        for i in range(5):  # Support clusters 0-4
            if f"{i}" in input_lower:
                return get_cluster_info(i)
        
        # If just "cluster" or "clusters" is mentioned, show all available clusters
        if input_lower.strip() in ["cluster", "clusters", "show me available clusters", "available clusters"]:
            cluster_info = "**Available Clusters:**\n\n"
            for i in range(4):
                cluster_info += f"• Cluster {i}\n\n"
            
            return cluster_info

    if ("product" in input_lower and "categor" in input_lower) or "available categories" in input_lower or "show me product categories" in input_lower:
        categories = sorted(df_clusters['Product_Category'].unique())
        category_info = "**Available Product Categories:**\n\n"
        
        for category in categories:
            category_info += f"• {category}\n\n"
        
        return category_info

    if "payment" in input_lower or "what payment methods are available" in input_lower:
        payments = sorted(df_clusters['Preferred_Payment_Method'].unique())
        payment_info = "**Available Payment Methods:**\n\n"
        
        for payment in payments:
            payment_info += f"• {payment}\n\n"
        
        return payment_info
    
    if "device" in input_lower or "what devices do customers use" in input_lower:
        devices = sorted(df_clusters['Device_Used'].unique())
        device_info = "**Customer Devices:**\n\n"
        
        for device in devices:
            device_info += f"• {device}\n\n"
        
        return device_info
    
    if "delivery" in input_lower:
        return "**Preferred Delivery Options:**\n\n• **Express** - Fast delivery (1-2 days)\n\n• **Standard** - Regular delivery (3-5 days)\n\n• **Scheduled** - Choose your delivery time"
    
    if "region" in input_lower:
        regions = sorted(df_clusters['Customer_Region'].unique())
        region_info = "**Customer Regions:**\n\n"
        
        for region in regions:
            region_info += f"• {region}\n\n"
        
        return region_info

    product_response = product_cluster_response(user_input)
    if product_response:
        return product_response

    follow_up = follow_up_on_last_cluster(user_input)
    if follow_up:
        return follow_up

    return "🤖 Sorry, I didn't understand that. Try asking about a product, a cluster, or spending habits."

# --- Main App Layout ---
# Add theme toggle
col_title, col_theme = st.columns([4, 1])
with col_title:
    st.title("Customer Insights Chatbot")
    st.markdown("Ask me about customer clusters, products, and spending patterns!")
with col_theme:
    st.write("")  # Add some spacing
    if st.button("🌓 Toggle Theme", key="theme_toggle"):
        st.session_state.dark_theme = not st.session_state.dark_theme
        st.rerun()

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
    
    # Display grouped chat history
    if st.session_state.chat_history:
        grouped_history = group_chat_history(st.session_state.chat_history)
        
        for group_idx, chat_group in enumerate(reversed(grouped_history)):
            # Get time range for the group
            start_time = chat_group[0][0]
            end_time = chat_group[-1][0]
            
            if len(chat_group) == 1:
                group_label = f"💬 {start_time}"
            else:
                group_label = f"💬 {start_time} - {end_time} ({len(chat_group)} chats)"
            
            with st.expander(group_label, expanded=False):
                for i, (timestamp, user_msg, bot_msg) in enumerate(chat_group):
                    st.markdown(f"**[{timestamp}] You:** {user_msg[:40]}...")
                    st.markdown(f"**Bot:** {bot_msg[:40]}...")
                    
                    col_reload, col_continue = st.columns(2)
                    with col_reload:
                        if st.button("🔄", key=f"reload_{group_idx}_{i}", help="Reload this conversation"):
                            st.session_state.messages.append({"role": "user", "content": user_msg})
                            st.session_state.messages.append({"role": "assistant", "content": bot_msg})
                            st.rerun()
                    with col_continue:
                        if st.button("➕", key=f"continue_{group_idx}_{i}", help="Continue from here"):
                            # Load all conversations up to this point
                            for ts, u_msg, b_msg in chat_group[:i+1]:
                                st.session_state.messages.append({"role": "user", "content": u_msg})
                                st.session_state.messages.append({"role": "assistant", "content": b_msg})
                            st.rerun()
                    
                    if i < len(chat_group) - 1:
                        st.markdown("---")

# Main chat area
with col2:
    # Chat container with custom styling
    chat_content = []
    
    # Build chat content
    if not st.session_state.messages:
        chat_content.append("""
            Hello! I'm your Customer Insights Assistant. I can help you explore customer data and clusters.
            
            Try asking me about:
            • Specific clusters (e.g., "Tell me about cluster 1")
            • Product categories and customer preferences
            • Payment methods and device usage
            • Customer demographics and behavior
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
    
    # Input area with custom styling - seamlessly connected to chat container
    st.markdown('''
    <div class="input-container">
    </div>
    ''', unsafe_allow_html=True)
    
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
        if st.button("🧠 Clusters", key="clusters"):
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
