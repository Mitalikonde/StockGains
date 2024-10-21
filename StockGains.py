import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objs as go
import time

# Set up page
st.set_page_config(layout="wide", page_title="StockGains", page_icon=":chart_with_upwards_trend:")

# Custom CSS for unique UI and design improvements
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    /* Full-page background */
    body {
        background: linear-gradient(135deg, #000046, #1cb5e0);
        font-family: 'Poppins', sans-serif;
        color: white;
    }

    /* Floating cards with glass effect */
    .card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        color: #dabcff;
    }

    /* Add spacing between StockGains and Welcome section */
    .welcome-section {
        margin-top: 40px;
    }

    /* Custom Navbar */
    .navbar {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .navbar h1 {
        font-size: 28px;
        color: #dabcff;
        margin: 0;
    }

    /* Buttons with animations */
    .stButton button {
        background-color: #1cb5e0;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #000046;
        transform: scale(1.05);
    }

    /* Custom styling for date input boxes */
    .stDateInput {
        width: 200px;  /* Adjust the width as needed */
        margin: auto;  /* Center the input boxes */
    }

    /* Footer */
    footer {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        margin-top: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# Main Function
def main():
    # Navbar Section
    st.markdown("""<div class='navbar'><h1>StockGains</h1></div>""", unsafe_allow_html=True)

    # Welcome Section
    st.markdown("""
        <div class="card welcome-section" style="text-align: center;">
            <h2>Welcome to StockGains!</h2>
            <p>Your go-to platform for insightful analysis of the Indian stock market.</p>
            <p><i>Pick a feature below to get started.</i></p>
        </div>
    """, unsafe_allow_html=True)

    # Navigation using radio buttons
    selected = st.radio("Choose an option", ["Stock Prediction", "Comparative Metrics"], horizontal=True)

    # Stock Prediction Section
    if selected == "Stock Prediction":
        st.markdown("<div class='card'><h2>Stock Prediction</h2></div>", unsafe_allow_html=True)
        stock_df = pd.read_csv("StockStreamTickersData.csv")
        tickers = stock_df["Company Name"]

        # Date pickers for data analysis
        start_date = st.date_input("Start Date", datetime.date(2015, 1, 1), key='start_date')
        end_date = st.date_input("End Date", datetime.date.today(), key='end_date')

        selected_company = st.selectbox('Pick a Company', tickers)
        if selected_company:
            symbol = stock_df.loc[stock_df['Company Name'] == selected_company, 'Symbol'].values[0]
            data = yf.download(symbol, start=start_date, end=end_date)

            if not data.empty:
                st.write(f"Displaying raw data for {selected_company}:")
                st.dataframe(data)

                with st.spinner('Generating Prediction Model...'):
                    time.sleep(2)

                # Plot raw data
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
                fig.update_layout(title=f"{selected_company} Stock Prices", xaxis_rangeslider_visible=True)
                st.plotly_chart(fig)

                # Prophet Forecast
                df_train = data[['Close']].reset_index()
                df_train.columns = ['ds', 'y']

                m = Prophet()
                m.fit(df_train)
                future = m.make_future_dataframe(periods=365)
                forecast = m.predict(future)

                st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
                fig1 = plot_plotly(m, forecast)
                st.plotly_chart(fig1)

    # Comparative Metrics Section
    elif selected == "Comparative Metrics":
        st.markdown("<div class='card'><h2>Comparative Metrics</h2></div>", unsafe_allow_html=True)
        sector_data = pd.read_csv('SectorData.csv')
        sectors = sector_data['Sector'].unique()

        # Date pickers for data analysis
        start_date = st.date_input("Start Date", datetime.date(2015, 1, 1), key='comp_start_date')
        end_date = st.date_input("End Date", datetime.date.today(), key='comp_end_date')
        
        selected_sector = st.selectbox('Select a Sector', sectors)

        if selected_sector:
            sector_companies = sector_data[sector_data['Sector'] == selected_sector]['Company Name']
            selected_companies = st.multiselect('Pick Companies', sector_companies)

            if selected_companies:
                stock_df = pd.read_csv('StockStreamTickersData.csv')
                symbols = [stock_df.loc[stock_df['Company Name'] == company, 'Symbol'].values[0] for company in selected_companies]
                data = yf.download(symbols, start=start_date, end=end_date)['Adj Close']

                if not data.empty:
                    st.line_chart(data)

    
    # Footer Section
    st.markdown("""
    <footer>
        <p>StockGains - Empowering your market insights | 2024</p>
    </footer>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == '__main__':
    main()
