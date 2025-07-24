import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

# Load and preprocess data 
inbound_df = pd.read_csv("./data/phx_inbound.csv")
inbound_df['calendar_date'] = pd.to_datetime(inbound_df['calendar_date'])
inbound_df['year_month'] = inbound_df['calendar_date'].dt.to_period('M').astype(str)

# Sidebar menu 
chart_type = st.selectbox(
    "Select a chart to view:",
    ("Monthly Received Cases", "Daily Received Cases", "Vendor Performance")
)

# Chart: Monthly Received Cases 
if chart_type == "Monthly Received Cases":
    monthly_cases = (
        inbound_df.groupby('year_month')['hdr_received_cases_qty']
        .sum()
        .reset_index()
        .sort_values('year_month')
    )
    fig = px.bar(
        monthly_cases,
        x='year_month',
        y='hdr_received_cases_qty',
        text='hdr_received_cases_qty',
        title='Inbound Received Cases Per Month',
        labels={'year_month': 'Month', 'hdr_received_cases_qty': 'Cases Received'}
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis_title='Month', yaxis_title='Cases Received', title_x=0.5)
    fig.update_xaxes(type='category')
    st.plotly_chart(fig)

# Chart: Daily Received Cases 
elif chart_type == "Daily Received Cases":
    daily_cases = (
        inbound_df.groupby('calendar_date')['hdr_received_cases_qty']
        .sum()
        .reset_index()
        .sort_values('calendar_date')
    )
    fig = px.line(
        daily_cases,
        x='calendar_date',
        y='hdr_received_cases_qty',
        title='Inbound Received Cases Over Time',
        labels={'calendar_date': 'Date', 'hdr_received_cases_qty': 'Cases Received'},
        markers=True
    )
    fig.update_layout(xaxis_title='Date', yaxis_title='Cases Received', title_x=0.5)
    st.plotly_chart(fig)

# Chart: Vendor Performance 
elif chart_type == "Vendor Performance":
    vendor_perf = (
        inbound_df.groupby('received_from_vendor_name')
        .agg({
            'hdr_shipped_cases_qty': 'sum',
            'hdr_received_cases_qty': 'sum'
        })
        .reset_index()
    )
    vendor_perf['discrepancy'] = vendor_perf['hdr_shipped_cases_qty'] - vendor_perf['hdr_received_cases_qty']
    top_vendors = vendor_perf.sort_values('hdr_received_cases_qty', ascending=False).head(10)

    fig = px.bar(
        top_vendors,
        x='received_from_vendor_name',
        y='discrepancy',
        text='discrepancy',
        title='Top 10 Vendors: Shipped vs. Received Discrepancy',
        labels={'received_from_vendor_name': 'Vendor', 'discrepancy': 'Discrepancy (Shipped - Received)'}
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis_title='Vendor', yaxis_title='Discrepancy', title_x=0.5)
    st.plotly_chart(fig)
