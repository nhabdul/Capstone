import streamlit as st
import pandas as pd
from datetime import datetime
import time
import numpy as np

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
        scroll-behavior: smooth;
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
        --bot-color: #333333;
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
        scroll-behavior: smooth;
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
if 'df_clusters' not in st.session_state:
    st.session_state.df_clusters = None
if 'scroll_trigger' not in st.session_state:
    st.session_state.scroll_trigger = 0

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.dark_theme), unsafe_allow_html=True)

# Load CSV data
@st.cache_data
def load_csv_data(file):
    """Load data from uploaded CSV file"""
    try:
        df = pd.read_csv(file)
        return df, None
    except Exception as e:
        return None, str(e)

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

# Helper Functions for data analysis
def get_cluster_info(cluster_id, df):
    """Get information about a specific cluster"""
    if 'Cluster' not in df.columns:
        return "❌ No 'Cluster' column found in the data."
    
    subset = df[df['Cluster'] == cluster_id]
    if subset.empty:
        return f"❌ Cluster {cluster_id} doesn't exist in the data."
    
    st.session_state.last_cluster = cluster_id
    
    # Build response based on available columns
    response = f"### 🧠 Cluster {cluster_id} Overview\n\n"
    
    # Numeric columns to analyze
    numeric_cols = subset.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != 'Cluster':
            avg_val = subset[col].mean()
            if col.lower() in ['income', 'salary', 'revenue', 'value', 'price']:
                response += f"• Average {col}: ${avg_val:,.2f}\n\n"
            else:
                response += f"• Average {col}: {avg_val:.2f}\n\n"
    
    # Categorical columns to analyze
    categorical_cols = subset.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if len(subset[col].unique()) > 0:
            top_value = subset[col].mode().iloc[0] if len(subset[col].mode()) > 0 else "N/A"
            response += f"• Most common {col}: **{top_value}**\n\n"
    
    return response

def product_cluster_response(user_input, df):
    """Find which cluster buys a specific product most"""
    if 'Product_Category' not in df.columns:
        return None
    
    user_input_lower = user_input.lower()
    product_categories = df['Product_Category'].unique()
    matched_product = None
    
    for product in product_categories:
        if product.lower() in user_input_lower:
            matched_product = product
            break
    
    if matched_product and 'Cluster' in df.columns:
        filtered = df[df['Product_Category'] == matched_product]
        if not filtered.empty:
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

def follow_up_on_last_cluster(user_input, df):
    """Handle follow-up questions about the last mentioned cluster"""
    msg = user_input.lower()
    cluster_id = st.session_state.last_cluster
    if cluster_id is None or 'Cluster' not in df.columns:
        return None
    
    subset = df[df["Cluster"] == cluster_id]
    if subset.empty:
        return None
    
    # Check for specific column mentions
    for col in df.columns:
        if col.lower() in msg and col != 'Cluster':
            if df[col].dtype in ['int64', 'float64']:
                avg_val = subset[col].mean()
                if col.lower() in ['income', 'salary', 'revenue', 'value', 'price']:
                    return f"• Average {col} in Cluster {cluster_id} is ${avg_val:,.2f}."
                else:
                    return f"• Average {col} in Cluster {cluster_id} is {avg_val:.2f}."
            else:
                if len(subset[col].mode()) > 0:
                    top_value = subset[col].mode().iloc[0]
                    return f"• Most common {col} in Cluster {cluster_id} is **{top_value}**."
    
    return None

def cluster_aware_response(user_input, df):
    """Main response function that handles various user queries"""
    if df is None:
        return "❌ Please upload a CSV file first to analyze customer data."
    
    input_lower = user_input.lower()

    # Handle cluster queries
    if "cluster" in input_lower:
        if 'Cluster' not in df.columns:
            return "❌ No 'Cluster' column found in your data."
        
        # Check for specific cluster numbers
        unique_clusters = sorted(df['Cluster'].unique())
        for cluster_id in unique_clusters:
            if str(cluster_id) in input_lower:
                return get_cluster_info(cluster_id, df)
        
        # If just "cluster" or "clusters" is mentioned, show all available clusters
        if input_lower.strip() in ["cluster", "clusters", "show me available clusters", "available clusters"]:
            cluster_info = "**Available Clusters:**\n\n"
            for cluster_id in unique_clusters:
                cluster_info += f"• Cluster {cluster_id}\n\n"
            return cluster_info

    # Handle column-specific queries
    if "columns" in input_lower or "what data" in input_lower or "available data" in input_lower:
        cols_info = "**Available Data Columns:**\n\n"
        for col in df.columns:
            cols_info += f"• {col}\n\n"
        return cols_info

    # Handle product queries
    product_response = product_cluster_response(user_input, df)
    if product_response:
        return product_response

    # Handle follow-up questions
    follow_up = follow_up_on_last_cluster(user_input, df)
    if follow_up:
        return follow_up

    # Generic data exploration
    if any(word in input_lower for word in ["summary", "overview", "describe", "info"]):
        summary_info = f"**Data Summary:**\n\n"
        summary_info += f"• Total records: {len(df)}\n\n"
        summary_info += f"• Columns: {len(df.columns)}\n\n"
        
        if 'Cluster' in df.columns:
            summary_info += f"• Unique clusters: {df['Cluster'].nunique()}\n\n"
        
        return summary_info

    return "🤖 I can help you analyze your customer data. Try asking about clusters, specific columns, or data summaries. Upload your CSV file if you haven't already!"

# --- Main App Layout ---
# Add theme toggle
col_title, col_theme = st.columns([4, 1])
with col_title:
    st.title("Customer Insights Chatbot")
    st.markdown("Upload your CSV file and ask me about customer clusters, products, and patterns!")
with col_theme:
    st.write("")  # Add some spacing
    if st.button("🌓 Toggle Theme", key="theme_toggle"):
        st.session_state.dark_theme = not st.session_state.dark_theme
        st.rerun()

# File upload section
if st.session_state.df_clusters is None:
    st.markdown("### 📁 Upload Your Customer Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload a CSV file containing customer data with columns like 'Cluster', product categories, etc."
    )
    
    if uploaded_file is not None:
        df, error = load_csv_data(uploaded_file)
        if error:
            st.error(f"Error loading CSV: {error}")
        else:
            st.session_state.df_clusters = df
            st.success(f"✅ CSV loaded successfully! {len(df)} rows, {len(df.columns)} columns")
            st.markdown("**Columns found:**")
            st.write(", ".join(df.columns))
            st.rerun()

# Only show chat interface if data is loaded
if st.session_state.df_clusters is not None:
    df = st.session_state.df_clusters
    
    # Create layout with sidebar and main content
    col1, col2 = st.columns([1, 3])

    # Sidebar for chat history
    with col1:
        st.markdown('<div class="sidebar-header">💬 Chat History</div>', unsafe_allow_html=True)
        
        # Add clear history button
        if st.button("🗑️ Clear History", key="clear_history"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.session_state.scroll_trigger += 1
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
                                st.session_state.scroll_trigger += 1
                                st.rerun()
                        with col_continue:
                            if st.button("➕", key=f"continue_{group_idx}_{i}", help="Continue from here"):
                                # Load all conversations up to this point
                                for ts, u_msg, b_msg in chat_group[:i+1]:
                                    st.session_state.messages.append({"role": "user", "content": u_msg})
                                    st.session_state.messages.append({"role": "assistant", "content": b_msg})
                                st.session_state.scroll_trigger += 1
                                st.rerun()
                        
                        if i < len(chat_group) - 1:
                            st.markdown("---")

    # Main chat area
    with col2:
        # Chat container with custom styling
        chat_content = []
        
        # Build chat content
        if not st.session_state.messages:
            chat_content.append(f"""
                Hello! I'm your Customer Insights Assistant. Your data has been loaded with {len(df)} rows and {len(df.columns)} columns.
                
                Try asking me about:
                • Specific clusters (e.g., "Tell me about cluster 1")
                • Available data columns
                • Data summaries and overviews
                • Product categories and customer preferences
            """)
        
        # Add all messages to chat content
        for message in st.session_state.messages:
            if message["role"] == "user":
                chat_content.append(f'<div class="user-message">{message["content"]}</div>')
            else:
                chat_content.append(f'<div class="bot-message">{message["content"]}</div>')
        
        # Display chat container
        chat_html = f'''
        <div class="chat-container" id="chat-container">
            {"".join(chat_content)}
        </div>
        '''
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Auto-scroll script - simplified and more reliable
        st.markdown(f"""
        <script>
        // Auto-scroll function
        function scrollToBottom() {{
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer) {{
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }}
        }}
        
        // Scroll immediately
        scrollToBottom();
        
        // Scroll after short delay for dynamic content
        setTimeout(scrollToBottom, 100);
        setTimeout(scrollToBottom, 300);
        
        // Trigger: {st.session_state.scroll_trigger}
        </script>
        """, unsafe_allow_html=True)
        
        # Input area
        st.markdown('<div class="input-container"></div>', unsafe_allow_html=True)
        
        # Create input form
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Type your message here...",
                key="user_input",
                placeholder="Ask me about your customer data...",
                label_visibility="collapsed"
            )
            
            col_send, col_examples = st.columns([1, 4])
            with col_send:
                submit_button = st.form_submit_button("Send 📤", use_container_width=True)
            with col_examples:
                st.markdown("*Press Enter to send*")
        
        # Quick action buttons based on available data
        st.markdown("**Quick Actions:**")
        btn_cols = st.columns(4)
        
        quick_actions = [
            ("🧠 Clusters", "Show me available clusters"),
            ("📊 Summary", "Give me a data summary"),
            ("📋 Columns", "What data columns are available?"),
            ("🔍 Overview", "Describe the data")
        ]
        
        for idx, (label, query) in enumerate(quick_actions):
            with btn_cols[idx]:
                if st.button(label, key=f"action_{idx}"):
                    user_input = query
                    submit_button = True

        # Process user input
        if submit_button and user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get bot response
            bot_response = cluster_aware_response(user_input, df)
            
            # Add bot response to chat
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            # Update scroll trigger
            st.session_state.scroll_trigger += 1
            
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
- Upload a CSV file with customer data (should include columns like 'Cluster', product categories, etc.)
- Type your question and press Enter or click Send
- Use the sidebar to view and reload previous conversations
- Try the quick action buttons for common queries
- Ask about specific clusters, data summaries, or column information
""")
