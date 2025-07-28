import pandas as pd
import plotly.express as px
import altair as alt
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

st.set_page_config(
    page_title="Ankaa Global Logistics Dashboard",
    page_icon=":a:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Reduce page padding
st.markdown(
    """
    <style>
        .main .block-container {
            padding-left: 0rem;
            padding-right: 0rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)
#alt.theme.background("light")

# Load and preprocess data 
inbound_df = pd.read_csv("./data/phx_inbound.csv")
inbound_df['calendar_date'] = pd.to_datetime(inbound_df['calendar_date'])
inbound_df['year_month'] = inbound_df['calendar_date'].dt.to_period('M').astype(str)
outbound_df = pd.read_csv("./data/phx_outbound.csv")
items_df = pd.read_csv("./data/phx_items.csv")

# Get current date and week boundaries
today = pd.Timestamp.now()
start_of_week = today - pd.to_timedelta(today.weekday(), unit='d')
current_month = today.month
current_year = today.year
current_month_str = today.to_period('M').strftime('%Y-%m')

# Weekly Data Filtering
weekly_inbound = inbound_df[inbound_df['calendar_date'] >= start_of_week]
monthly_inbound = inbound_df.loc[inbound_df['year_month'] == current_month_str]

# Weekly Metrics
# Total SKUs received (Week to Date)
weekly_sku_count = weekly_inbound['item_no'].nunique()

# Weekly Received Cases
weekly_received_cases = weekly_inbound['hdr_received_cases_qty'].sum()

# Monthly Metrics
# Total Received Cases This Month 
monthly_received_cases = monthly_inbound['hdr_received_cases_qty'].sum()

# Top 3 Customers by Volume (Monthly) - for Customers tab
monthly_customer_summary = (
    monthly_inbound.groupby("received_from_vendor_name")["hdr_received_cases_qty"]
    .sum()
    .reset_index()
    .sort_values(by="hdr_received_cases_qty", ascending=False)
    .head(3)
)

if len(monthly_customer_summary) > 0:
    top_customers = []
    for i, row in monthly_customer_summary.iterrows():
        customer_name = row['received_from_vendor_name']
        cases = int(row['hdr_received_cases_qty'])
        top_customers.append((customer_name, cases))
else:
    top_customers = [("No data", 0), ("No data", 0), ("No data", 0)]

# Ensure we have exactly 3 entries for display
while len(top_customers) < 3:
    top_customers.append(("No data", 0))

# Total number of customers
total_customers = inbound_df['received_from_vendor_name'].nunique()

# SKU Active/Inactive/Discontinued Donut Chart
def create_sku_donut_chart():
    # Process SKU status data
    sku_status_counts = items_df['scm_item_status_desc'].value_counts()
    
    # Map the statuses and get counts
    active_skus = sku_status_counts.get('Sku Active', 0)
    inactive_skus = sku_status_counts.get('Blank As Valid', 0)
    discontinued_skus = sku_status_counts.get('Discontinued', 0)     
    total_skus = active_skus + inactive_skus + discontinued_skus
    
    # Create the donut chart
    fig = go.Figure(data=[go.Pie(
        labels=['Active', 'Inactive', 'Discontinued'],
        values=[active_skus, inactive_skus, discontinued_skus],
        hole=0.4,
        marker_colors=['#2ca02c', '#ffa500', '#ff4b4b'],  # Green for active, orange for inactive, red for discontinued
        textinfo='label+percent',
        textfont_size=14,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    # Update layout with center annotation
    fig.update_layout(
        title={
            'text': 'SKU Status',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        annotations=[
            dict(
                text=f'<b>{total_skus}</b><br>Total<br>SKUs',
                x=0.5, y=0.5,
                font_size=12,
                showarrow=False,
                xanchor="center",
                yanchor="middle"
            )
        ],
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50),
        height=300
    )
    
    return fig

# Customer Active/Inactive Donut Chart
def create_customer_donut_chart():
    # Sample data - replace with your actual logic
    total_customers_count = total_customers  # Using your existing variable
    
    # Sample active/inactive logic - you'll need to replace this with your actual data
    # For example, you might determine active customers based on recent orders
    active_customers = int(total_customers_count * 0.75)  # 75% active (sample)
    inactive_customers = total_customers_count - active_customers
    
    # Create the donut chart
    fig = go.Figure(data=[go.Pie(
        labels=['Active', 'Inactive'],
        values=[active_customers, inactive_customers],
        hole=0.4,
        marker_colors=['#2ca02c', '#ff4b4b'],  # Green for active, red for inactive
        textinfo='label+percent',
        textfont_size=14,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    # Update layout with center annotation
    fig.update_layout(
        title={
            'text': 'Customer Status',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        annotations=[
            dict(
                text=f'<b>{total_customers_count}</b><br>Total<br>Customers',
                x=0.5, y=0.5,
                font_size=12,
                showarrow=False,
                xanchor="center",
                yanchor="middle"
            )
        ],
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50),
        height=300
    )
    
    return fig

# Monthly inbound and outbound data for chart (filtered and cleaned)
# Convert date fields to datetime first, then filter
inbound_df_copy = inbound_df.copy()
inbound_df_copy['last_receipt_dt'] = pd.to_datetime(inbound_df_copy['last_receipt_dt'], errors='coerce')

outbound_df_copy = outbound_df.copy()
outbound_df_copy['ship_dt'] = pd.to_datetime(outbound_df_copy['ship_dt'], errors='coerce')

# Remove Jan 1970 data (unclassified data) using converted datetime fields
filtered_inbound_df = inbound_df_copy[inbound_df_copy['last_receipt_dt'] >= pd.Timestamp('1971-01-01')]
filtered_outbound_df = outbound_df_copy[outbound_df_copy['ship_dt'] >= pd.Timestamp('1971-01-01')]

# Create year_month for both datasets
filtered_inbound_df = filtered_inbound_df.copy()
filtered_inbound_df['year_month'] = filtered_inbound_df['last_receipt_dt'].dt.to_period('M').astype(str)

filtered_outbound_df = filtered_outbound_df.copy()
filtered_outbound_df['year_month'] = filtered_outbound_df['ship_dt'].dt.to_period('M').astype(str)

# Get vendor list for dropdown
vendor_list = inbound_df.groupby("received_from_vendor_name").groups.keys()
vendor_list = list(vendor_list)  # Convert to list
vendor_list.sort()  # Sort alphabetically

def get_chart_data(selected_vendor=None):
    # Create dummy data for demonstration
    import numpy as np
    
    # Define months
    months = ['2024-01', '2024-02', '2024-03', '2024-04']
    
    if selected_vendor is None:  # "All Customers" selected
        # Dummy data for all customers combined
        inbound_volumes = [480, 780, 270, 470]  # Matches your chart pattern
        outbound_volumes = [660, 950, 380, 710]  # Matches your chart pattern
        
        # Create DataFrame
        inbound_data = pd.DataFrame({
            'year_month': months,
            'volume': inbound_volumes,
            'type': 'Inbound'
        })
        
        outbound_data = pd.DataFrame({
            'year_month': months,
            'volume': outbound_volumes,
            'type': 'Outbound'
        })
        
        combined_chart = pd.concat([inbound_data, outbound_data], ignore_index=True)
        return combined_chart
    
    else:
        # Dummy data for specific customer (smaller volumes)
        np.random.seed(42)  # For consistent results
        inbound_volumes = np.random.randint(50, 200, 4)
        outbound_volumes = np.random.randint(80, 250, 4)
        
        inbound_data = pd.DataFrame({
            'year_month': months,
            'volume': inbound_volumes,
            'type': 'Inbound'
        })
        
        outbound_data = pd.DataFrame({
            'year_month': months,
            'volume': outbound_volumes,
            'type': 'Outbound'
        })
        
        combined_chart = pd.concat([inbound_data, outbound_data], ignore_index=True)
        return combined_chart
    
    # Combine inbound and outbound for chart
    combined_chart = pd.concat([monthly_inbound_chart, monthly_outbound_chart], ignore_index=True)
    return combined_chart

# Monthly KPIs calculations (same logic as weekly but with monthly data)
# Monthly SKU count
monthly_sku_count = monthly_inbound['item_no'].nunique()

# Monthly received cases (already calculated above)
# monthly_received_cases = monthly_inbound['hdr_received_cases_qty'].sum()

# Monthly Inbound Delivery Expectations (same logic as weekly)
monthly_putaway_df = monthly_inbound.dropna(subset=['first_receipt_dt', 'scheduled_start_receive_dt'])
monthly_putaway_df = monthly_putaway_df.copy()
monthly_putaway_df['first_receipt_dt'] = pd.to_datetime(monthly_putaway_df['first_receipt_dt'], errors='coerce')
monthly_putaway_df['scheduled_start_receive_dt'] = pd.to_datetime(monthly_putaway_df['scheduled_start_receive_dt'], errors='coerce')
monthly_putaway_df = monthly_putaway_df.dropna(subset=['first_receipt_dt', 'scheduled_start_receive_dt'])

if len(monthly_putaway_df) > 0:
    try:
        monthly_on_time_receipts = (monthly_putaway_df['first_receipt_dt'] <= monthly_putaway_df['scheduled_start_receive_dt']).sum()
        monthly_on_time_rate = round((monthly_on_time_receipts / len(monthly_putaway_df)) * 100, 2)
        if pd.isna(monthly_on_time_rate):
            monthly_on_time_rate = 0.0
    except:
        monthly_on_time_rate = 0.0
else:
    monthly_on_time_rate = 0.0

# Monthly Outbound Delivery Expectations (same logic as weekly)
# Filter outbound data for current month using date range
monthly_outbound_data = outbound_df_copy[outbound_df_copy['ship_dt'] >= pd.Timestamp(f'{current_year}-{current_month:02d}-01')]
monthly_outbound_data = monthly_outbound_data[monthly_outbound_data['ship_dt'] < pd.Timestamp(f'{current_year}-{current_month:02d}-01') + pd.DateOffset(months=1)]

monthly_shipment_df = monthly_outbound_data.dropna(subset=['ship_dt', 'appointment_dt'])
monthly_shipment_df = monthly_shipment_df.copy()
monthly_shipment_df['ship_dt'] = pd.to_datetime(monthly_shipment_df['ship_dt'], errors='coerce')
monthly_shipment_df['appointment_dt'] = pd.to_datetime(monthly_shipment_df['appointment_dt'], errors='coerce')
monthly_shipment_df = monthly_shipment_df.dropna(subset=['ship_dt', 'appointment_dt'])

if len(monthly_shipment_df) > 0:
    try:
        monthly_on_time_shipments = (monthly_shipment_df['ship_dt'] <= monthly_shipment_df['appointment_dt']).sum()
        monthly_shipment_rate = round((monthly_on_time_shipments / len(monthly_shipment_df)) * 100, 2)
        if pd.isna(monthly_shipment_rate):
            monthly_shipment_rate = 0.0
    except:
        monthly_shipment_rate = 0.0
else:
    monthly_shipment_rate = 0.0

# Convert date columns
inbound_df['first_receipt_dt'] = pd.to_datetime(inbound_df['first_receipt_dt'], errors='coerce')
inbound_df['scheduled_start_receive_dt'] = pd.to_datetime(inbound_df['scheduled_start_receive_dt'], errors='coerce')

# Weekly KPIs calculations
# Weekly Average Putaway Time (hrs)
weekly_putaway_df = weekly_inbound.dropna(subset=['first_receipt_dt', 'scheduled_start_receive_dt'])

# Ensure datetime conversion for weekly data
weekly_putaway_df = weekly_putaway_df.copy()
weekly_putaway_df['first_receipt_dt'] = pd.to_datetime(weekly_putaway_df['first_receipt_dt'], errors='coerce')
weekly_putaway_df['scheduled_start_receive_dt'] = pd.to_datetime(weekly_putaway_df['scheduled_start_receive_dt'], errors='coerce')

# Remove any rows where conversion failed
weekly_putaway_df = weekly_putaway_df.dropna(subset=['first_receipt_dt', 'scheduled_start_receive_dt'])

if len(weekly_putaway_df) > 0:
    try:
        weekly_on_time_receipts = (weekly_putaway_df['first_receipt_dt'] <= weekly_putaway_df['scheduled_start_receive_dt']).sum()
        weekly_on_time_rate = round((weekly_on_time_receipts / len(weekly_putaway_df)) * 100, 2)
        if pd.isna(weekly_on_time_rate):
            weekly_on_time_rate = 0.0
    except:
        weekly_on_time_rate = 0.0
else:
    weekly_on_time_rate = 0.0

# Weekly Outbound On-Time Shipment Rate
weekly_outbound = outbound_df_copy[outbound_df_copy['ship_dt'] >= start_of_week]
weekly_shipment_df = weekly_outbound.dropna(subset=['ship_dt', 'appointment_dt'])

# Ensure datetime conversion for weekly outbound data
weekly_shipment_df = weekly_shipment_df.copy()
weekly_shipment_df['ship_dt'] = pd.to_datetime(weekly_shipment_df['ship_dt'], errors='coerce')
weekly_shipment_df['appointment_dt'] = pd.to_datetime(weekly_shipment_df['appointment_dt'], errors='coerce')

# Remove any rows where conversion failed
weekly_shipment_df = weekly_shipment_df.dropna(subset=['ship_dt', 'appointment_dt'])

if len(weekly_shipment_df) > 0:
    try:
        weekly_on_time_shipments = (weekly_shipment_df['ship_dt'] <= weekly_shipment_df['appointment_dt']).sum()
        weekly_shipment_rate = round((weekly_on_time_shipments / len(weekly_shipment_df)) * 100, 2)
        if pd.isna(weekly_shipment_rate):
            weekly_shipment_rate = 0.0
    except:
        weekly_shipment_rate = 0.0
else:
    weekly_shipment_rate = 0.0

# Outbound KPI - wave_desc distribution
wave_counts = outbound_df['wave_desc'].fillna('Unknown').value_counts()

# --- SIDEBAR ---
with st.sidebar:
    st.image("Ankaa_logo.jpg", use_container_width= True)
    st.markdown("<h2 style='text-align: center;'>Ankaa Global Logistics</h2>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=["Admin Dashboard", "Customers", "New Customer", "Value Added Services"],
        icons=["house-fill", "people-fill", "person-plus-fill", "box-seam-fill"],
        menu_icon="cast",
        default_index=0
    )

# --- MAIN CONTENT ---
# Single column layout when Customers is selected, otherwise two columns
if selected == "Customers":
    # Full width single column for Customers tab
    st.subheader("👥 Customer Overview")
    st.divider()
    
    # Top 3 customers section
    st.markdown(f"<h4>Top 3 Customers by Volume</h4>", unsafe_allow_html=True)

    st.markdown("""
       <style>
        [data-testid="stMetricValue"] {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
        }
        </style>
    """, unsafe_allow_html=True)

    cust_col1, cust_col2, cust_col3 = st.columns([1,2,2])
            
    with cust_col1:
        st.metric(
            label="🥇 #1 Customer",
            value=top_customers[0][0],
            delta=f"{top_customers[0][1]:,} Cases"
        )
        st.metric(
            label="🥈 #2 Customer", 
            value=top_customers[1][0],
            delta=f"{top_customers[1][1]:,} Cases"
        )
        st.metric(
            label="🥉 #3 Customer",
            value=top_customers[2][0], 
            delta=f"{top_customers[2][1]:,} Cases"
        )

    with cust_col2:
        customer_donut_fig = create_customer_donut_chart()
        st.plotly_chart(customer_donut_fig, use_container_width=True)
            
    with cust_col3:
        sku_donut_fig = create_sku_donut_chart()
        st.plotly_chart(sku_donut_fig, use_container_width=True)
            
    st.markdown("---")
    # Monthly inbound vs outbound chart with customer filter
    st.subheader("📊 Monthly Inbound vs Outbound Volume")
    
    # Customer dropdown filter
    customer_options = ["All Customers"] + vendor_list
    selected_customer = st.selectbox(
        'Select a Customer:',
        customer_options,
        key='customer_filter'
    )
    
    # Get filtered chart data
    chart_data = get_chart_data(selected_customer if selected_customer != "All Customers" else None)
    
    # Create grouped bar chart
    if not chart_data.empty:
        fig_combined = px.bar(
            chart_data,
            x='year_month',
            y='volume',
            color='type',
            barmode='group',
            title=f'Monthly Inbound vs Outbound Volume - {selected_customer}',
            labels={'year_month': 'Month', 'volume': 'Volume (Cases/Cartons)', 'type': 'Type'},
            color_discrete_map={'Inbound': '#1f77b4', 'Outbound': '#ff7f0e'}
        )
        fig_combined.update_layout(
            xaxis_title='Month', 
            yaxis_title='Volume (Cases/Cartons)', 
            title_x=0.5,
            showlegend=True
        )
        fig_combined.update_xaxes(type='category')
        st.plotly_chart(fig_combined, use_container_width=True)
    else:
        st.warning(f"No data available for {selected_customer}")


elif selected == "Admin Dashboard":
    # Two columns: main (wide) and side (narrow) for other tabs
    col_main, col_side = st.columns([2, 1], gap='small')

    with col_main:
        st.subheader("📊 Weekly Summary")
        st.divider()
        kpi1, kpi2, kpi3 = st.columns(3, gap='small')
        with kpi1:
            st.markdown("**Total SKUs Received (WTD)**")
            st.markdown(f"<h2 style='color:#1f77b4'>{weekly_sku_count}</h2>", unsafe_allow_html=True)

        with kpi2:
            st.markdown("**Weekly Received Cases**")
            st.markdown(f"<h2 style='color:#ff7f0e'>{int(weekly_received_cases):,}</h2>", unsafe_allow_html=True)

        with kpi3:
            st.markdown("**Inbound On-Time Rate**")
            st.markdown(f"<h2 style='color:#2ca02c'>{weekly_on_time_rate}%</h2>", unsafe_allow_html=True)
        chart_type = st.selectbox(
            "Select a chart to view:",
            ("Monthly Received Cases", "Daily Received Cases")
        )
        # Chart rendering
        if chart_type == "Monthly Received Cases":
            monthly_cases = (
                inbound_df.groupby('year_month')['hdr_received_cases_qty']
                .sum()
                .reset_index()
                .sort_values('year_month')
            )
            
            # Convert year_month to alpha-numeric format (Jan 2025)
            monthly_cases['month_formatted'] = pd.to_datetime(monthly_cases['year_month']).dt.strftime('%b %Y')
            
            # Show only last 6 months
            monthly_cases_recent = monthly_cases.tail(6)
            
            fig = px.bar(
                monthly_cases_recent,
                x='month_formatted',
                y='hdr_received_cases_qty',
                text='hdr_received_cases_qty',
                title='Inbound Received Cases Per Month (YTD)',
                labels={'month_formatted': 'Date', 'hdr_received_cases_qty': 'Cases Received'}
            )
            fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig.update_layout(xaxis_title='Date', yaxis_title='Cases Received', title_x=0.5)
            fig.update_xaxes(type='category')
            st.plotly_chart(fig)

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

    with col_side:
        st.subheader("📅 Monthly Summary")
        st.markdown("---")
        m_kpi1, m_kpi2 = st.columns(2, gap='small')
        with m_kpi1:
            st.markdown("**Inbound On-Time Rate**")
            st.markdown(f"<h2 style='color:#2ca02c'>{monthly_on_time_rate:.1f}%</h2>", unsafe_allow_html=True)
        with m_kpi2:
            st.markdown("**Total Received Cases**")
            st.markdown(f"<h2 style='color:yellow'>{monthly_received_cases} Cases</h2>", unsafe_allow_html=True)
        
        # Get top 5 customers data
        top_5_customers = (
            monthly_inbound.groupby("received_from_vendor_name")["hdr_received_cases_qty"]
            .sum()
            .reset_index()
            .sort_values(by="hdr_received_cases_qty", ascending=False)
            .head(5)
        )

        # Add bottles on hand (sample data - replace with your actual logic)
        top_5_customers['bottles_on_hand'] = top_5_customers['hdr_received_cases_qty'] * 12  # Sample: 12 bottles per case

        # Rename columns for display
        top_5_customers_display = top_5_customers.rename(columns={
            'Rank': 'Rank',
            'received_from_vendor_name': 'Customer Name',
            'bottles_on_hand': 'Bottles on Hand'
        })

        # Display as dataframe with custom column configuration
        st.dataframe(
            top_5_customers_display[['Customer Name', 'Bottles on Hand']],
            column_config={
                "Rank": st.column_config.TextColumn(
                    "Rank",
                    width="small"
                ),
                "Customer Name": st.column_config.TextColumn(
                    "Top Customers",
                    width="medium",
                ),
                "Bottles on Hand": st.column_config.NumberColumn(
                    "Bottles on Hand",
                    format="%d",
                    width="small"
                )
            },
            hide_index=True,
            use_container_width=True
        )

elif selected == "New Customer":
    # New Customer Form
    st.subheader("New Customer Registration")
    st.markdown("---")
    st.markdown("""
        <style>
        .stFileUploader > div > div > div > div {
            width: 100% !important;
            max-width: 300px !important;
        }
        .stFileUploader > div > div > div > div > button {
            width: 100% !important;
            padding: 8px 15px !important;
            font-size: 14px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
    uploaded_file = st.file_uploader("",type=['csv', 'xlsx', 'pdf'])
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    with st.form("new_customer_form"):
        # Company Information
        st.markdown("### Company Information")
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", placeholder="Enter company name")
            contact_person = st.text_input("Contact Person *", placeholder="Primary contact name")
            email = st.text_input("Email Address *", placeholder="contact@company.com")
            
        with col2:
            phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
        
        # Address Information
        st.markdown("### Address Information")
        col3, col4 = st.columns(2)
        
        with col3:
            address_line1 = st.text_input("Address Line 1 *", placeholder="Street address")
            city = st.text_input("City *", placeholder="City")
            state = st.text_input("State/Province *", placeholder="State")
            
        with col4:
            address_line2 = st.text_input("Address Line 2", placeholder="Suite, unit, etc.")
            zip_code = st.text_input("ZIP/Postal Code *", placeholder="12345")
            country = st.text_input("Country *", placeholder="United States")
        
        # Service Requirements
        st.markdown("### Service Requirements")
        services = st.multiselect(
            "Required Services",
            ["Warehousing", "Distribution", "Inventory Management","Custom Packaging"]
        )
        
        special_requirements = st.text_area("Special Requirements", placeholder="Any specific needs or requirements...")
        
        # Form submission
        col_submit_left, col_submit_center, col_submit_right = st.columns([2, 1, 2])
        with col_submit_center:
            submitted = st.form_submit_button("Submit Customer", use_container_width=True)
        
        if submitted:
            # Basic validation
            required_fields = [company_name, contact_person, email, address_line1, city, state, zip_code, country]
            if all(required_fields):
                st.success("✅ Customer registration submitted successfully!")
                st.balloons()
            else:
                st.error("❌ Please fill in all required fields marked with *")


elif selected == "Value Added Services":
    # Value Added Services Information
    st.header("Value Added Services")
    st.markdown("---")
    
    # Service overview metrics
    st.subheader("📊 Service Overview")
    
    service_col1, service_col2, service_col3, service_col4 = st.columns(4)
    
    with service_col1:
        st.metric("Active Repack Orders", "142", delta="12 this week")
    
    with service_col2:
        st.metric("VAP Projects", "28", delta="-3 from last month")
    
    with service_col3:
        st.metric("Labeling Jobs", "89", delta="15 pending")
    
    with service_col4:
        st.metric("Lot-Tracking Items", "1,247", delta="98 new lots")
    
    st.markdown("---")
    
    # Service utilization chart
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Service revenue/volume chart
        service_data = pd.DataFrame({
            'Service': ['Repacks', 'VAP', 'Labeling', 'Lot-Tracking'],
            'Monthly_Volume': [450, 180, 320, 890],
            'Revenue': [15000, 25000, 8000, 12000]
        })
        
        fig_services = px.bar(
            service_data, 
            x='Service', 
            y='Monthly_Volume',
            title='Service Volume This Month',
            color='Service'
        )
        st.plotly_chart(fig_services, use_container_width=True)
    
    with col_chart2:
       # Service turnaround times
        turnaround_data = pd.DataFrame({
            'Service': ['Repacks', 'VAP', 'Labeling', 'Lot-Tracking'],
            'Target_Days': [3, 7, 2, 0.5],
            'Actual_Days': [2.5, 5.2, 3.8, 0.2]
        })
        
        fig_turnaround = px.bar(
            turnaround_data,
            x='Service',
            y=['Target_Days', 'Actual_Days'],
            title='Average Turnaround Time: Target vs Actual',
            barmode='group'
        )
        st.plotly_chart(fig_turnaround, use_container_width=True)


# Initialize session state for chat
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False

# Floating chat button and overlay
st.markdown(f"""
<style>
.floating-chat-btn {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1001;
    background: #ff4b4b;
    color: white;
    border: none;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}}

.floating-chat-btn:hover {{
    background: #ff6b6b;
    transform: scale(1.1);
}}

.chat-overlay {{
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 350px;
    height: 500px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    z-index: 1000;
    border: 1px solid #ddd;
    display: {'block' if st.session_state.chat_open else 'none'};
}}

.chat-header {{
    background: #ff4b4b;
    color: white;
    padding: 15px;
    border-radius: 10px 10px 0 0;
    font-weight: bold;
    position: relative;
}}

.chat-close {{
    position: absolute;
    right: 15px;
    top: 15px;
    background: none;
    border: none;
    color: white;
    font-size: 18px;
    cursor: pointer;
}}
</style>

<div class="chat-overlay">
    <div class="chat-header">
        Ankaa Assistant
        <button class="chat-close" onclick="toggleChat()">×</button>
    </div>
    <iframe src="YOUR_DATABRICKS_CHATBOT_URL" 
            width="100%" 
            height="440" 
            frameborder="0"
            style="border-radius: 0 0 10px 10px;">
    </iframe>
</div>

<button class="floating-chat-btn" onclick="toggleChat()">💬</button>

<script>
function toggleChat() {{
    // Send message to Streamlit to toggle chat state
    window.parent.postMessage({{
        type: 'streamlit:setComponentValue',
        value: !{str(st.session_state.chat_open).lower()}
    }}, '*');
    
    // Also toggle display immediately for responsiveness
    var chatOverlay = document.querySelector('.chat-overlay');
    if (chatOverlay.style.display === 'none') {{
        chatOverlay.style.display = 'block';
    }} else {{
        chatOverlay.style.display = 'none';
    }}
}}
</script>
""", unsafe_allow_html=True)

# Alternative: Use a hidden button to handle state changes
col1, col2 = st.columns([10, 1])
with col2:
    # This invisible button will handle the actual state change
    if st.button("", key="chat_toggle", help="Toggle chat", 
                 label_visibility="collapsed"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()