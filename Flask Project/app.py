from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# Load your dataset once
DATA_PATH = os.path.join(os.path.dirname(__file__), 'ecommerce_customer_clusters_for_tableau.csv')
df = pd.read_csv(DATA_PATH)

def get_cluster_info(cluster_id):
    subset = df[df['Cluster'] == cluster_id]
    if subset.empty:
        return "❌ That cluster doesn't exist."

    avg_income = subset['Annual_Income'].mean()
    avg_spend = subset['Spending_Score'].mean()
    avg_order_value = subset['Average_Order_Value'].mean()
    avg_orders = subset['Number_of_Orders'].mean()
    avg_review = subset['Review_Score'].mean()
    common_payment = subset['Preferred_Payment_Method'].mode()[0]
    common_device = subset['Device_Used'].mode()[0]
    common_category = subset['Product_Category'].mode()[0]
    avg_age = subset['Age'].mean()

    return (
        f"📊 **Cluster {cluster_id} Insights**:\n"
        f"- Avg Income: ${avg_income:,.2f}\n"
        f"- Avg Spending Score: {avg_spend:.2f}\n"
        f"- Avg Order Value: ${avg_order_value:,.2f}\n"
        f"- Avg Orders: {avg_orders:.1f}\n"
        f"- Avg Review Score: {avg_review:.2f}\n"
        f"- Common Payment: {common_payment}\n"
        f"- Common Device: {common_device}\n"
        f"- Common Category: {common_category}\n"
        f"- Avg Age: {avg_age:.1f} years"
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []

    bot_response = None
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        session['chat_history'].append({'user': user_input, 'time': timestamp})

        # Bot logic (extend with NLP if needed)
        if 'cluster' in user_input.lower():
            cluster_id = ''.join(filter(str.isdigit, user_input))
            if cluster_id.isdigit():
                bot_response = get_cluster_info(int(cluster_id))
            else:
                bot_response = "❓ Please specify a valid cluster number."
        else:
            bot_response = "🤖 I'm here to provide cluster insights. Try asking: 'Tell me about cluster 2'."

        session['chat_history'].append({'bot': bot_response, 'time': timestamp})

    return render_template('index.html', chat=session['chat_history'])

@app.route('/reset')
def reset():
    session.pop('chat_history', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
