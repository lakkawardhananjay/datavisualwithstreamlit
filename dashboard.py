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

# Convert 'NoOfManufactured' to integer if not already
if 'NoOfManufactured' in df.columns:
    df['NoOfManufactured'] = pd.to_numeric(df['NoOfManufactured'], errors='coerce').fillna(0).astype(int)

# Display title and raw data
st.title("📊 Detected Items Dashboard")
st.dataframe(df)

# --- Total Items Manufactured (Till Now)
if 'NoOfManufactured' in df.columns:
    total_items_all_time = df['NoOfManufactured'].sum()

# --- Total Items Manufactured (Today Only)
today = datetime.datetime.now().date()
today_data = df[df['Date'].dt.date == today]

if not today_data.empty:
    total_items_today = today_data['NoOfManufactured'].sum()
else:
    total_items_today = 0

# 📢 Show the metrics
st.subheader("📈 Overall Manufacturing Stats")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Items Manufactured Till Now", total_items_all_time)

with col2:
    st.metric("Total Items Manufactured Today", total_items_today)

# --- Item Distribution Bar Chart (Total Manufactured per Item)
if 'ItemName' in df.columns:
    st.subheader("📦 Item Distribution (All Time)")

    item_distribution = df.groupby('ItemName')['NoOfManufactured'].sum().reset_index()
    fig_bar = px.bar(item_distribution, x='ItemName', y='NoOfManufactured', text_auto=True, labels={'NoOfManufactured': 'Quantity'})
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Pie Chart for Today's Manufacturing Distribution
if not today_data.empty:
    st.subheader(f"🛠️ Today's Manufacturing Distribution ({today})")

    today_distribution = today_data.groupby('ItemName')['NoOfManufactured'].sum().reset_index()

    fig_pie = px.pie(
        today_distribution,
        names='ItemName',
        values='NoOfManufactured',
        hole=0.4,
        title="Manufactured Items Distribution Today"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- Bar Graph: Items Manufactured by Day of Week
if 'Date' in df.columns:
    st.subheader("📅 Items Manufactured by Day of Week")

    df['DayOfWeek'] = df['Date'].dt.day_name()

    day_distribution = df.groupby('DayOfWeek')['NoOfManufactured'].sum().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ).fillna(0)

    fig_day = px.bar(day_distribution, x=day_distribution.index, y=day_distribution.values, labels={'x': 'Day', 'y': 'Total Manufactured'})
    st.plotly_chart(fig_day, use_container_width=True)
