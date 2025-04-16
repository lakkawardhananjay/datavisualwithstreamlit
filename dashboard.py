import streamlit as st
import boto3
import pandas as pd
import datetime

# Use Streamlit Secrets
aws_access_key = st.secrets["AWS_ACCESS_KEY_ID"]
aws_secret_key = st.secrets["AWS_SECRET_ACCESS_KEY"]

# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

# Define the table correctly
table = dynamodb.Table('DetectedItems')

# Now it's safe to scan
response = table.scan()
items = response['Items']

# Convert to DataFrame
df = pd.DataFrame(items)

# Display
st.title("Detected Items Dashboard")
st.dataframe(df)

# Optional bar chart for item counts
if 'ItemName' in df.columns:
    st.subheader("Item Distribution")
    st.bar_chart(df['ItemName'].value_counts())

# Adding pie chart for today's manufactured items
if 'Timestamp' in df.columns and 'ItemName' in df.columns:
    # Convert timestamp to datetime (assuming it's stored as string)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Get today's date
    today = datetime.datetime.now().date()
    
    # Filter for today's data
    today_data = df[df['Timestamp'].dt.date == today]
    
    if not today_data.empty:
        st.subheader(f"Today's Manufacturing Distribution ({today})")
        
        # Create pie chart for today's items
        today_counts = today_data['ItemName'].value_counts()
        fig = {
            'data': [{
                'type': 'pie',
                'labels': today_counts.index.tolist(),
                'values': today_counts.values.tolist(),
                'hole': 0.4,
            }]
        }
        st.plotly_chart(fig)
        
        # Display the count
        st.metric("Total Items Manufactured Today", len(today_data))
    else:
        st.info("No items manufactured today")

# Adding bar graph for items manufactured by day of the week
if 'Timestamp' in df.columns:
    st.subheader("Items Manufactured by Day of Week")
    
    # Add day of week column
    df['DayOfWeek'] = df['Timestamp'].dt.day_name()
    
    # Order days correctly
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Count items by day of week
    day_counts = df['DayOfWeek'].value_counts().reindex(days_order).fillna(0)
    
    # Create bar chart
    st.bar_chart(day_counts)
    
    # Also show as a table for precise numbers
    st.subheader("Items Manufactured by Day (Table View)")
    day_counts_df = pd.DataFrame({
        'Day': day_counts.index,
        'Items Manufactured': day_counts.values
    })
    st.table(day_counts_df)
