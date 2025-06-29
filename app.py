from flask import Flask, render_template, request, jsonify, session
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load data once when the app starts
df_clusters = None

def load_data():
    global df_clusters
    try:
        df_clusters = pd.read_csv("ecommerce_customer_clusters_for_tableau.csv")
        print("Data loaded successfully!")
        print(f"Loaded {len(df_clusters)} records with {len(df_clusters.columns)} columns")
        return True
    except FileNotFoundError:
        print("ERROR: CSV file 'ecommerce_customer_clusters_for_tableau.csv' not found.")
        print("Please ensure the CSV file is in the same directory as this script.")
        return False
    except Exception as e:
        print(f"ERROR loading data: {e}")
        return False

# Initialize data on startup
if not load_data():
    print("Application cannot start without the required CSV file.")
    exit(1)

# Helper Functions
def get_cluster_info(cluster_id):
    """Get detailed information about a specific cluster"""
    subset = df_clusters[df_clusters['Cluster'] == cluster_id]
    if subset.empty:
        return f"Cluster {cluster_id} doesn't exist in the data."
    
    session['last_cluster'] = cluster_id
    
    # Calculate statistics
    avg_income = subset['Annual_Income'].mean()
    avg_spend = subset['Spending_Score'].mean()
    avg_order_value = subset['Average_Order_Value'].mean()
    avg_orders = subset['Number_of_Orders'].mean()
    avg_review = subset['Review_Score'].mean()
    avg_age = subset['Age'].mean()
    
    # Get most common values
    top_device = subset['Device_Used'].mode()[0] if not subset['Device_Used'].mode().empty else "N/A"
    top_payment = subset['Preferred_Payment_Method'].mode()[0] if not subset['Preferred_Payment_Method'].mode().empty else "N/A"
    top_product = subset['Product_Category'].mode()[0] if not subset['Product_Category'].mode().empty else "N/A"
    top_region = subset['Customer_Region'].mode()[0] if not subset['Customer_Region'].mode().empty else "N/A"
    
    cluster_size = len(subset)
    
    return (
        f"### Cluster {cluster_id} Overview ({cluster_size} customers)\n"
        f"• **Average Income:** ${avg_income:,.2f}\n"
        f"• **Spending Score:** {avg_spend:.1f}/100\n"
        f"• **Avg Order Value:** ${avg_order_value:.2f}\n"
        f"• **Orders per Customer:** {avg_orders:.1f}\n"
        f"• **Average Review Score:** {avg_review:.2f}/5.0\n"
        f"• **Average Age:** {avg_age:.1f} years\n"
        f"• **Most Common Payment:** {top_payment}\n"
        f"• **Most Used Device:** {top_device}\n"
        f"• **Popular Product Category:** {top_product}\n"
        f"• **Primary Region:** {top_region}\n"
        f"💡 *Ask about specific aspects like 'income', 'spending', or 'devices' for more details*"
    )

def product_cluster_response(user_input):
    """Find which cluster is most associated with a product category"""
    user_input_lower = user_input.lower()
    product_categories = df_clusters['Product_Category'].unique()
    matched_product = None

    # Find matching product category
    for product in product_categories:
        if product.lower() in user_input_lower:
            matched_product = product
            break
    
    # Also check for partial matches
    if not matched_product:
        for product in product_categories:
            product_words = product.lower().split()
            if any(word in user_input_lower for word in product_words):
                matched_product = product
                break

    if matched_product:
        filtered = df_clusters[df_clusters['Product_Category'] == matched_product]
        
        if filtered.empty:
            return f"No data found for product category '{matched_product}'"
        
        cluster_counts = filtered['Cluster'].value_counts().sort_values(ascending=False)
        top_cluster = int(cluster_counts.idxmax())
        count = int(cluster_counts.max())
        total_customers = len(filtered)

        session['last_cluster'] = int(top_cluster)
        session['last_product'] = str(matched_product)

        return (
            f"**{matched_product} Analysis:**\n"
            f"• **Top Cluster:** Cluster {top_cluster} ({count} customers)\n"
            f"• **Total Customers:** {total_customers} purchase this category\n"
            f"💡 Ask: *'Tell me about Cluster {top_cluster}'* to learn more about these customers."
        )
    
    return None

def follow_up_on_last_cluster(user_input):
    """Handle follow-up questions about the last discussed cluster"""
    msg = user_input.lower()
    cluster_id = session.get('last_cluster')
    
    if cluster_id is None:
        return None
    
    subset = df_clusters[df_clusters["Cluster"] == cluster_id]
    
    if subset.empty:
        return None

    # Handle different types of follow-up questions
    if any(word in msg for word in ["income", "salary", "earn", "money"]):
        avg_income = subset['Annual_Income'].mean()
        return (f"💰 **Cluster {cluster_id} Income Details:**\n"
                f"• Average: ${avg_income:,.2f}")
    
    elif any(word in msg for word in ["spend", "spending", "score"]):
        avg_spend = subset['Spending_Score'].mean()
        return (f"📊 **Cluster {cluster_id} Spending Details:**\n"
                f"• Average: {avg_spend:.1f}/100")
    
    elif any(word in msg for word in ["order", "orders", "purchase"]):
        avg_orders = subset['Number_of_Orders'].mean()
        avg_value = subset['Average_Order_Value'].mean()
        return (f"🛒 **Cluster {cluster_id} Order Patterns:**\n"
                f"• Average orders per customer: **{avg_orders:.1f}**\n"
                f"• Average order value: **${avg_value:.2f}**")
    
    elif any(word in msg for word in ["review", "rating", "satisfaction"]):
        avg_review = subset['Review_Score'].mean()
        return (f"⭐ **Cluster {cluster_id} Review Details:**\n"
                f"• Average: {avg_review:.2f}/5.0")
    
    elif any(word in msg for word in ["device", "mobile", "desktop", "tablet"]):
        device_counts = subset['Device_Used'].value_counts()
        device_info = "📱 **Cluster " + str(cluster_id) + " Device Usage:**\n"
        for device, count in device_counts.items():
            percentage = (count / len(subset)) * 100
            device_info += f"• {device}: {count} customers ({percentage:.1f}%)\n"
        return device_info
    
    elif any(word in msg for word in ["region", "location", "where"]):
        region_counts = subset['Customer_Region'].value_counts()
        region_info = "🌍 **Cluster " + str(cluster_id) + " Regional Distribution:**\n"
        for region, count in region_counts.items():
            percentage = (count / len(subset)) * 100
            region_info += f"• {region}: {count} customers ({percentage:.1f}%)\n"
        return region_info
    
    elif any(word in msg for word in ["gender", "male", "female"]):
        gender_counts = subset['Gender'].value_counts()
        gender_info = "👥 **Cluster " + str(cluster_id) + " Gender Distribution:**\n"
        for gender, count in gender_counts.items():
            percentage = (count / len(subset)) * 100
            # Convert numeric gender codes to readable labels
            gender_label = "Male" if gender == 1 else "Female" if gender == 0 else str(gender)
            gender_info += f"• {gender_label}: {count} customers ({percentage:.1f}%)\n"
        return gender_info
    
    elif any(word in msg for word in ["age", "old", "young"]):
        avg_age = subset['Age'].mean()
        return (f"👨‍👩‍👧‍👦 **Cluster {cluster_id} Age Details:**\n"
                f"• Average age: **{avg_age:.1f} years**")
    
    return None

def gender_product_analysis(user_input):
    """Analyze product preferences by gender, optionally within a specific cluster"""
    input_lower = user_input.lower()
    
    # Check if a specific cluster is mentioned
    import re
    cluster_matches = re.findall(r'cluster\s+(\d+)', input_lower)
    cluster_id = None
    if cluster_matches:
        try:
            cluster_id = int(cluster_matches[0])
        except ValueError:
            pass
    
    # Start with all data or filter by cluster
    data_subset = df_clusters
    cluster_text = ""
    if cluster_id is not None:
        available_clusters = [int(x) for x in df_clusters['Cluster'].unique()]
        if cluster_id not in available_clusters:
            available_clusters_str = ', '.join(map(str, sorted(available_clusters)))
            return f"Cluster {cluster_id} doesn't exist. Available clusters: {available_clusters_str}"
        
        data_subset = df_clusters[df_clusters['Cluster'] == cluster_id]
        cluster_text = f" in Cluster {cluster_id}"
    
    # Check if asking about female preferences FIRST to avoid "female" being caught by "male"
    if any(word in input_lower for word in ["female", "women", "woman"]):
        # Filter for females
        female_customers = data_subset[data_subset['Gender'] == 0]  # Adjust based on your data encoding
        
        if female_customers.empty:
            # Try alternative encoding
            female_customers = data_subset[data_subset['Gender'].str.lower() == 'female'] if data_subset['Gender'].dtype == 'object' else data_subset[data_subset['Gender'] == 'Female']
        
        if not female_customers.empty:
            product_counts = female_customers['Product_Category'].value_counts()
            total_females = len(female_customers)
            
            response = f"👩 **Female Customer Product Preferences{cluster_text}** ({total_females} customers):\n"
            for product, count in product_counts.head(5).items():  # Top 5 products
                percentage = (count / total_females) * 100
                response += f"• **{product}**: {count} customers ({percentage:.1f}%)\n"
            return response
        else:
            if cluster_id is not None:
                return f"No female customers found in Cluster {cluster_id}"
            else:
                return f"No female customers found in the data"
    
    # Check if asking about male preferences
    elif any(word in input_lower for word in ["male", "men", "man"]) and not any(word in input_lower for word in ["female", "women", "woman"]):
        # Filter for males (assuming 1 = Male, 0 = Female, or check actual values)
        male_customers = data_subset[data_subset['Gender'] == 1]  # Adjust based on your data encoding
        
        if male_customers.empty:
            # Try alternative encoding
            male_customers = data_subset[data_subset['Gender'].str.lower() == 'male'] if data_subset['Gender'].dtype == 'object' else data_subset[data_subset['Gender'] == 'Male']
        
        if not male_customers.empty:
            product_counts = male_customers['Product_Category'].value_counts()
            total_males = len(male_customers)
            
            response = f"👨 **Male Customer Product Preferences{cluster_text}** ({total_males} customers):\n"
            for product, count in product_counts.head(5).items():  # Top 5 products
                percentage = (count / total_males) * 100
                response += f"• **{product}**: {count} customers ({percentage:.1f}%)\n"
            return response
        else:
            if cluster_id is not None:
                return f"No male customers found in Cluster {cluster_id}"
            else:
                return f"No male customers found in the data"
    
    return None

def cluster_aware_response(user_input):
    """Main function to handle user queries and return appropriate responses"""
    input_lower = user_input.lower().strip()

    # Handle greetings
    if any(greeting in input_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return ("👋 **Hello!** I'm your customer cluster analysis assistant.\n"
                "I can help you explore customer segments. Try asking:\n"
                "• *'Tell me about Cluster 0'*\n"
                "• *'Which cluster buys electronics?'*\n"
                "• *'Show me available clusters'*")

    # Handle gender-based product queries
    gender_response = gender_product_analysis(user_input)
    if gender_response:
        return gender_response

    # Handle help requests
    if any(word in input_lower for word in ["help", "what can you do", "commands", "options"]):
        available_clusters = [int(x) for x in sorted(df_clusters['Cluster'].unique())]
        available_products = sorted(df_clusters['Product_Category'].unique())
        
        return ("🤖 **I can help you with:**\n"
                "**Cluster Analysis:**\n"
                f"• Available clusters: {', '.join(map(str, available_clusters))}\n"
                "• Ask: *'Tell me about Cluster X'*\n"
                "**Product Analysis:**\n"
                f"• Categories: {', '.join(available_products)}\n"
                "• Ask: *'Which cluster buys electronics?'*\n"
                "**Follow-up Questions:**\n"
                "• Income, spending, age, devices, regions, etc.")

    # Handle cluster queries
    if "cluster" in input_lower:
        # Extract cluster number if mentioned
        import re
        cluster_matches = re.findall(r'\b(\d+)\b', user_input)
        
        if cluster_matches:
            try:
                cluster_id = int(cluster_matches[0])
                available_clusters = [int(x) for x in df_clusters['Cluster'].unique()]
                if cluster_id in available_clusters:
                    return get_cluster_info(cluster_id)
                else:
                    available_clusters_str = ', '.join(map(str, sorted(available_clusters)))
                    return f"Cluster {cluster_id} doesn't exist. Available clusters: {available_clusters_str}"
            except ValueError:
                pass
        
        # Show available clusters if no specific number mentioned
        if any(phrase in input_lower for phrase in ["available", "show", "list", "what clusters"]):
            available_clusters = [int(x) for x in sorted(df_clusters['Cluster'].unique())]
            cluster_info = "**Available Customer Clusters:**\n"
            for cluster_id in available_clusters:
                cluster_size = len(df_clusters[df_clusters['Cluster'] == cluster_id])
                cluster_info += f"• **Cluster {cluster_id}** ({cluster_size} customers)\n"
            cluster_info += "💡 *Ask about any specific cluster for detailed analysis*"
            return cluster_info

    # Handle product category queries
    if any(phrase in input_lower for phrase in ["product", "category", "categories", "available product", "what product"]):
        if any(phrase in input_lower for phrase in ["available", "show", "list", "what are"]):
            categories = sorted(df_clusters['Product_Category'].unique())
            category_info = "**Available Product Categories:**\n"
            for category in categories:
                count = len(df_clusters[df_clusters['Product_Category'] == category])
                category_info += f"• **{category}** ({count} customers)\n"
            return category_info

    # Handle payment method queries
    if any(word in input_lower for word in ["payment", "pay"]):
        payments = sorted(df_clusters['Preferred_Payment_Method'].unique())
        payment_info = "**Customer Payment Methods:**\n"
        for payment in payments:
            count = len(df_clusters[df_clusters['Preferred_Payment_Method'] == payment])
            payment_info += f"• **{payment}** ({count} customers)\n"
        return payment_info
    
    # Handle device queries
    if any(word in input_lower for word in ["device", "mobile", "desktop", "tablet"]):
        devices = sorted(df_clusters['Device_Used'].unique())
        device_info = "📱 **Customer Device Usage:**\n"
        for device in devices:
            count = len(df_clusters[df_clusters['Device_Used'] == device])
            device_info += f"• **{device}** ({count} customers)\n"
        return device_info

    # Handle region queries
    if any(word in input_lower for word in ["region", "location", "where"]):
        regions = sorted(df_clusters['Customer_Region'].unique())
        region_info = "**Customer Regions:**\n"
        for region in regions:
            count = len(df_clusters[df_clusters['Customer_Region'] == region])
            region_info += f"• **{region}** ({count} customers)\n"
        return region_info

    # Try product-based analysis
    product_response = product_cluster_response(user_input)
    if product_response:
        return product_response

    # Try follow-up questions about last cluster
    follow_up = follow_up_on_last_cluster(user_input)
    if follow_up:
        return follow_up

    # Default response with suggestions
    return ("🤖 I didn't understand that query. Here are some things you can try:\n"
            "• *'Tell me about Cluster 0'*\n"
            "• *'Which cluster buys electronics?'*\n"
            "• *'Show available clusters'*\n"
            "• Type *'help'* for more options")

# Routes
@app.route('/')
def index():
    """Main page route"""
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
    """Handle chat messages"""
    try:
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
    
    except Exception as e:
        print(f"Error in send_message: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    """Toggle between light and dark theme"""
    session['dark_theme'] = not session.get('dark_theme', False)
    session.modified = True
    return jsonify({'dark_theme': session['dark_theme']})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear chat history"""
    session['messages'] = []
    session['chat_history'] = []
    session.pop('last_cluster', None)
    session.pop('last_product', None)
    session.modified = True
    return jsonify({'status': 'success'})

@app.route('/get_chat_history')
def get_chat_history():
    """Get chat history for display"""
    return jsonify(session.get('chat_history', []))

@app.route('/load_conversation', methods=['POST'])
def load_conversation():
    """Load a previous conversation"""
    try:
        data = request.json
        user_msg = data.get('user_message')
        bot_msg = data.get('bot_message')
        
        if not user_msg or not bot_msg:
            return jsonify({'error': 'Invalid conversation data'}), 400
        
        if 'messages' not in session:
            session['messages'] = []
        
        session['messages'].append({'role': 'user', 'content': user_msg})
        session['messages'].append({'role': 'assistant', 'content': bot_msg})
        session.modified = True
        
        return jsonify({'status': 'success'})
    
    except Exception as e:
        print(f"Error in load_conversation: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)