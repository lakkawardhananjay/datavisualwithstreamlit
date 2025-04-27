import streamlit as st
import boto3
import pandas as pd
import datetime
import plotly.express as px

# Load AWS credentials from Streamlit secrets
aws_access_key = st.secrets["AWS_ACCESS_KEY_ID"]
aws_secret_access_key = st.secrets["AWS_SECRET_ACCESS_KEY"]

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_access_key
)

# Define your table name
table = dynamodb.Table('DetectedItems')

# Scan the table
try:
    response = table.scan()
    items = response['Items']
    st.success("✅ Data loaded successfully from DynamoDB")
except Exception as e:
    st.error(f"❌ Failed to load data from DynamoDB: {e}")
    items = []

# Convert items to DataFrame
df = pd.DataFrame(items)

# Show warning if DataFrame is empty
if df.empty:
    st.warning("No data found in the table.")
    st.stop()

# Convert 'Date' column to datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])

# Display title and raw data
st.title("📊 Detected Items Dashboard")
st.dataframe(df)

# --- Total Items Manufactured (Till Now)
if 'ItemName' in df.columns:
    total_items_all_time = df['ItemName'].value_counts().sum()

# --- Total Items Manufactured (Today Only)
today = datetime.datetime.now().date()
today_data = df[df['Date'].dt.date == today]

if not today_data.empty:
    total_items_today = today_data['ItemName'].value_counts().sum()
else:
    total_items_today = 0

# 📢 Show the metrics
st.subheader("📈 Overall Manufacturing Stats")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Items Manufactured Till Now", total_items_all_time)

with col2:
    st.metric("Total no. of objects Manufactured Today", total_items_today)

# --- Item Distribution Bar Chart
if 'ItemName' in df.columns:
    st.subheader("📦 Item Distribution")
    st.bar_chart(df['ItemName'].value_counts())

# --- Pie Chart for Today's Manufacturing Distribution
if not today_data.empty:
    st.subheader(f"🛠️ Today's Manufacturing Distribution ({today})")

    today_counts = today_data['ItemName'].value_counts().reset_index()
    today_counts.columns = ['ItemName', 'Count']

    fig = px.pie(
        today_counts,
        names='ItemName',
        values='Count',
        hole=0.4,
        title="Manufactured Items Distribution Today"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Bar Graph: Items Manufactured by Day of Week
if 'Date' in df.columns:
    st.subheader("📅 Items Manufactured by Day of Week")

    df['DayOfWeek'] = df['Date'].dt.day_name()

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['DayOfWeek'].value_counts().reindex(days_order).fillna(0)

    st.bar_chart(day_counts)
