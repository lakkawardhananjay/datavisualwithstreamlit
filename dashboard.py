import streamlit as st
import boto3
import pandas as pd
import datetime
import plotly.express as px

# Load AWS credentials from Streamlit secrets
aws_access_key = st.secrets["AWS_ACCESS_KEY_ID"]
aws_secret_key = st.secrets["AWS_SECRET_ACCESS_KEY"]

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
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

# Item distribution bar chart
if 'ItemName' in df.columns:
    st.subheader("Item Distribution")
    st.bar_chart(df['ItemName'].value_counts())

# Pie chart for today's manufactured items
if 'Date' in df.columns and 'ItemName' in df.columns:
    today = datetime.datetime.now().date()
    today_data = df[df['Date'].dt.date == today]

    if not today_data.empty:
        st.subheader(f"Today's Manufacturing Distribution ({today})")

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

        # Calculate total manufactured items
        if 'Quantity' in today_data.columns:
            total_items = today_data['Quantity'].astype(int).sum()
        else:
            total_items = len(today_data)

        total_items = today_data['ItemName'].value_counts().sum()
    else:
        st.info("No items manufactured today.")

# Bar graph for items manufactured by day of week
if 'Date' in df.columns:
    st.subheader("Items Manufactured by Day of Week")

    df['DayOfWeek'] = df['Date'].dt.day_name()

    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['DayOfWeek'].value_counts().reindex(days_order).fillna(0)

    st.bar_chart(day_counts)
