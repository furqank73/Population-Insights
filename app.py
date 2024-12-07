import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# Load the dataset
df = pd.read_csv('df2.csv')

# Title and description
st.title('Population and Demographic Data Visualization THIS (DATA IS FROM 2017)')
st.write("""
    This app allows you to explore and visualize demographic data, including population statistics, sex ratio, population growth, 
    and more across various regions (PROVINCE, DIVISION, DISTRICT, TEHSIL). Use the filters and visualization options below to explore the data interactively.
""")

# Sidebar for filters
st.sidebar.header('Filter Data')

# Add filters for PROVINCE, DIVISION, DISTRICT, TEHSIL
province = st.sidebar.multiselect('Select Province', df['PROVINCE'].unique())
division = st.sidebar.multiselect('Select Division', 
    df[df['PROVINCE'].isin(province)]['DIVISION'].unique() if province else [])
district = st.sidebar.multiselect('Select District', 
    df[(df['PROVINCE'].isin(province)) & (df['DIVISION'].isin(division))]['DISTRICT'].unique() if division else [])
tehsil = st.sidebar.multiselect('Select Tehsil', 
    df[(df['PROVINCE'].isin(province)) & (df['DIVISION'].isin(division)) & (df['DISTRICT'].isin(district))]['TEHSIL'].unique() if district else [])

# Filter data based on selections
filtered_data = df.copy()

if province:
    filtered_data = filtered_data[filtered_data['PROVINCE'].isin(province)]
if division:
    filtered_data = filtered_data[filtered_data['DIVISION'].isin(division)]
if district:
    filtered_data = filtered_data[filtered_data['DISTRICT'].isin(district)]
if tehsil:
    filtered_data = filtered_data[filtered_data['TEHSIL'].isin(tehsil)]

# Display selected filters in breadcrumb format
breadcrumb = []
if province:
    breadcrumb.append(', '.join(province))
if division:
    breadcrumb.append(', '.join(division))
if district:
    breadcrumb.append(', '.join(district))
if tehsil:
    breadcrumb.append(', '.join(tehsil))

breadcrumb_text = ' > '.join(breadcrumb) if breadcrumb else "All Data"
st.write(f"Displaying data for: {breadcrumb_text}")

# Display the filtered data
if not filtered_data.empty:
    st.write(filtered_data)
else:
    st.write("No data available for the selected filters.")

# Column selection for sum display
st.header('Select Columns for Sum Calculation')

# List of columns to calculate the sum
columns_for_sum = [
    'NOW_POPULATION', 'POPULATION 1998', 'FEMALE_POPULATION', 'MALE_POPULATION', 
    'AREA (sq.km)', 'AVG_HOUSEHOLD_SIZE', 'TRANSGENDER_POPULATION', 'SEX_RATIO', 
    'ANNUAL_GROWTH_RATE', 'Population Density', 'POPULATION_INCREASE'
]

# Allow users to select columns to sum
selected_columns = st.multiselect('Select Columns to Show Total', columns_for_sum)

# Show the sum of selected columns for each province
if selected_columns:
    for province_name in province:
        st.subheader(f"Sum for {province_name}")
        province_data = filtered_data[filtered_data['PROVINCE'] == province_name]
        
        summed_data = {col: province_data[col].sum() for col in selected_columns}
        st.write(f"Sum of selected columns for {province_name}: {summed_data}")

        # Optionally, show the summed data in a more readable format (table)
        summed_data_df = pd.DataFrame(summed_data, index=[province_name])
        st.write(summed_data_df)
        
        # If two or more columns are selected, also show the sum of the selected columns together
        if len(selected_columns) > 1:
            combined_sum = province_data[selected_columns].sum().sum()
            st.write(f"Combined Sum of Selected Columns for {province_name}: {combined_sum}")
else:
    st.write("Select columns to see the total sum.")

# Visualization options
st.header('Visualization')

# Allow multiple column selections for visualization
column_choices = st.multiselect('Select Columns for Visualization', columns_for_sum)

# Chart type selection
chart_type = st.selectbox('Select Chart Type', ['Bar Chart', 'Line Chart', 'Pie Chart'])

# Comparison level selection (PROVINCE, DIVISION, DISTRICT, TEHSIL)
comparison_level = st.selectbox('Select Comparison Level', ['PROVINCE', 'DIVISION', 'DISTRICT', 'TEHSIL'])

# Color options
color_palette = px.colors.qualitative.Set1  # Color palette for multiple columns

# Visualization helper functions
def create_bar_chart(x_values, y_values, title, color):
    fig = go.Figure([go.Bar(x=x_values, y=y_values, marker_color=color)])
    fig.update_layout(title=title, xaxis_title='Categories', yaxis_title='Values', template='plotly_dark', barmode='stack')
    return fig

def create_pie_chart(labels, values, title):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3, pull=[0.1]*len(values))])
    fig.update_layout(title=title, template='plotly_dark')
    return fig

def create_line_chart(x_values, y_values, title, color):
    fig = go.Figure([go.Scatter(x=x_values, y=y_values, mode='lines+markers', line=dict(color=color))])
    fig.update_layout(title=title, xaxis_title='Categories', yaxis_title='Values', template='plotly_dark')
    return fig

# Visualization for selected columns and comparison levels
if column_choices and not filtered_data.empty:
    chart_data = []
    chart_titles = []
    for idx, column in enumerate(column_choices):
        color = color_palette[idx % len(color_palette)]  # Cycle through colors
        summed_data = []

        if comparison_level == 'PROVINCE':
            for province_name in province:
                province_data = filtered_data[filtered_data['PROVINCE'] == province_name]
                summed_data.append(province_data[column].sum())
            chart_titles.append(f"Sum of {column} by Province")

        elif comparison_level == 'DIVISION':
            for div in division:
                division_data = filtered_data[filtered_data['DIVISION'] == div]
                summed_data.append(division_data[column].sum())
            chart_titles.append(f"Sum of {column} by Division")

        elif comparison_level == 'DISTRICT':
            for dist in district:
                district_data = filtered_data[filtered_data['DISTRICT'] == dist]
                summed_data.append(district_data[column].sum())
            chart_titles.append(f"Sum of {column} by District")

        elif comparison_level == 'TEHSIL':
            for tehs in tehsil:
                tehsil_data = filtered_data[filtered_data['TEHSIL'] == tehs]
                summed_data.append(tehsil_data[column].sum())
            chart_titles.append(f"Sum of {column} by Tehsil")
        
        chart_data.append(summed_data)
    
    # Create a stacked bar chart with all the selected columns
    if chart_type == 'Bar Chart':
        st.subheader(f"Stacked Bar Chart: {comparison_level} Comparison")
        fig = go.Figure()
        for idx, data in enumerate(chart_data):
            fig.add_trace(go.Bar(x=province if comparison_level == 'PROVINCE' else division if comparison_level == 'DIVISION' else district if comparison_level == 'DISTRICT' else tehsil,
                                 y=data,
                                 name=column_choices[idx],
                                 marker_color=color_palette[idx % len(color_palette)]))  # Set color
        fig.update_layout(title=f"Comparison of {', '.join(column_choices)} by {comparison_level}",
                          xaxis_title=comparison_level,
                          yaxis_title='Total Values',
                          barmode='stack',
                          template='plotly_dark')
        st.plotly_chart(fig)
    
    # Optionally, add line or pie charts as needed
    elif chart_type == 'Line Chart':
        st.subheader(f"Line Chart: {comparison_level} Comparison")
        for idx, data in enumerate(chart_data):
            st.plotly_chart(create_line_chart(province if comparison_level == 'PROVINCE' else division if comparison_level == 'DIVISION' else district if comparison_level == 'DISTRICT' else tehsil,
                                              data,
                                              f"Sum of {column_choices[idx]} by {comparison_level}",
                                              color_palette[idx % len(color_palette)]))
    
    elif chart_type == 'Pie Chart':
        st.subheader(f"Pie Chart: {comparison_level} Comparison")
        for idx, data in enumerate(chart_data):
            st.plotly_chart(create_pie_chart(province if comparison_level == 'PROVINCE' else division if comparison_level == 'DIVISION' else district if comparison_level == 'DISTRICT' else tehsil,
                                              data,
                                              f"Sum of {column_choices[idx]} by {comparison_level}"))

else:
    st.write("No columns selected for visualization.")

# Optional: Download button for filtered data
st.sidebar.header('Download Data')
if not filtered_data.empty:
    st.sidebar.download_button(
        label="Download CSV",
        data=filtered_data.to_csv(index=False).encode('utf-8'),
        file_name='filtered_population_data.csv',
        mime='text/csv'
    )
# Footer with links
st.markdown("""
---
### Connect with Me
- [LinkedIn](https://www.linkedin.com/in/furqan-khan-256798268/)
- [Kaggle](https://www.kaggle.com/fkgaming)
- [GitHub](https://github.com/furqank73)
""")
