import streamlit as st
import boto3
import pandas as pd

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

# ✅ Define the table correctly
table = dynamodb.Table('DetectedItems')

# Now it's safe to scan
response = table.scan()
items = response['Items']

# Convert to DataFrame
df = pd.DataFrame(items)

# Display
st.title("Detected Items Dashboard")
st.dataframe(df)

# Optional bar chart
if 'ItemName' in df.columns:
    st.bar_chart(df['ItemName'].value_counts())
