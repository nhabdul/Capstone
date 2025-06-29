from flask import Flask, render_template, request, jsonify, session
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Load data once when the app starts
df_clusters = None

def load_data():
    global df_clusters
    try:
        df_clusters = pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")
        print("Data loaded successfully!")
    except FileNotFoundError:
        print("CSV file not found. Please ensure 'ecommerce_customer_clusters_for_tableau.csv' is in the same directory.")
        # Create dummy data for demonstration
        df_clusters = pd.DataFrame({
            'Cluster': [0, 1, 2, 3] * 25,
            'Annual_Income': [50000, 75000, 100000, 125000] * 25,
            'Spending_Score': [30, 50, 70, 90] * 25,
            'Average_Order_Value': [100, 150, 200, 250] * 25,
            'Number_of_Orders': [5, 8, 12, 15] * 25,
            'Review_Score': [3.5, 4.0, 4.5, 4.8] * 25,
            'Age': [25, 35, 45, 55] * 25,
            'Device_Used': ['Mobile', 'Desktop', 'Tablet', 'Mobile'] * 25,
            'Preferred_Payment_Method': ['Credit Card', 'PayPal', 'Debit Card', 'Bank Transfer'] * 25,
            'Product_Category': ['Electronics', 'Clothing', 'Home & Garden', 'Sports'] * 25,
            'Customer_Region': ['North', 'South', 'East', 'West'] * 25,
            'Gender': ['Male', 'Female', 'Male', 'Female'] * 25
        })

# Initialize data on startup
load_data()

# Helper Functions
def get_cluster_info(cluster_id):
    subset = df_clusters[df_clusters['Cluster'] == cluster_id]
    if subset.empty:
        return "❌ That cluster doesn't exist."
    
    session['last_cluster'] = cluster_id
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
        session['last_cluster'] = top_cluster
        session['last_product'] = matched_product
        
        return (
            f"💡 Customers who purchase **{matched_product}** the most are in **Cluster {top_cluster}** "
            f"with **{count} customers**.\n\n"
            f"You can ask: 'Tell me more about Cluster {top_cluster}' to learn about them."
        )
    return None

def follow_up_on_last_cluster(user_input):
    msg = user_input.lower()
    cluster_id = session.get('last_cluster')
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
        for i in range(4):  # Support clusters 0-3
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

# Routes
@app.route('/')
def index():
    # Initialize session variables
    if 'messages' not in session:
        session['messages'] = []
    if 'chat_history' not in session:
        session['chat_history'] = []
    if 'dark_theme' not in session:
        session['dark_theme'] = False
    
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.json.get('message', '').strip()
    
    if not user_input:
        return jsonify({'error': 'Empty message'}), 400
    
    # Get bot response
    bot_response = cluster_aware_response(user_input)
    
    # Add to session messages
    if 'messages' not in session:
        session['messages'] = []
    
    session['messages'].append({'role': 'user', 'content': user_input})
    session['messages'].append({'role': 'assistant', 'content': bot_response})
    
    # Add to chat history with timestamp
    timestamp = datetime.now().strftime("%H:%M")
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    session['chat_history'].append({
        'timestamp': timestamp,
        'user_message': user_input,
        'bot_message': bot_response
    })
    
    # Keep only last 20 conversations in history
    if len(session['chat_history']) > 20:
        session['chat_history'] = session['chat_history'][-20:]
    
    session.modified = True
    
    return jsonify({
        'bot_response': bot_response,
        'timestamp': timestamp
    })

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    session['dark_theme'] = not session.get('dark_theme', False)
    session.modified = True
    return jsonify({'dark_theme': session['dark_theme']})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['messages'] = []
    session['chat_history'] = []
    session.modified = True
    return jsonify({'status': 'success'})

@app.route('/get_chat_history')
def get_chat_history():
    return jsonify(session.get('chat_history', []))

@app.route('/load_conversation', methods=['POST'])
def load_conversation():
    data = request.json
    user_msg = data.get('user_message')
    bot_msg = data.get('bot_message')
    
    if 'messages' not in session:
        session['messages'] = []
    
    session['messages'].append({'role': 'user', 'content': user_msg})
    session['messages'].append({'role': 'assistant', 'content': bot_msg})
    session.modified = True
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)