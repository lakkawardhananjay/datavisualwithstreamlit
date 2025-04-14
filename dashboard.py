import boto3
import streamlit as st
from datetime import datetime
import pandas as pd
import os


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize 
DynamoDBdynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',  # e.g., ''
    aws_access_key_id=aws_access_key_id ,
    aws_secret_access_key=aws_secret_access_key
)
table = dynamodb.Table('DetectedItems')


# Scan all items
response = table.scan()
items = response['Items']

# Convert to dataframe for Streamlit
import pandas as pd
df = pd.DataFrame(items)

# Sort by date
df = df.sort_values(by='Date', ascending=False)

st.title("Detected Objects Dashboard")
st.dataframe(df)

# Example charts
st.bar_chart(df['ItemName'].value_counts())
