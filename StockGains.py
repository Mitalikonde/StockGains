import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from datetime import date
from plotly import graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly
import time

st.set_page_config(layout="wide")

def add_meta_tag():
    meta_tag = """
        <head>
            <meta name="google-site-verification" content="QBiAoAo1GAkCBe1QoWq-dQ1RjtPHeFPyzkqJqsrqW-s" />
        </head>
    """
    st.markdown(meta_tag, unsafe_allow_html=True)

add_meta_tag()

# Navbar Section
st.write('# StockGains')

# Home Page Content
st.write("## Welcome to StockGains!")
st.write("""
    StockGains is your go-to platform for insightful analysis of the Indian stock market.
    
    ### Features:
    - **Stock Prediction**: Forecast future stock prices using historical data and advanced algorithms.
    - **Comparative Metrics**: Analyze and compare different sectors or peer companies to gain market insights.
    
    Explore the options below to get started!
""")

# Radio buttons on the main page with no default selection
selected = st.radio("Navigation", ["Stock Prediction", "Comparative Metrics"], horizontal=True)


# Initialize start and end date inputs only if a section is selected
if selected:
    if selected in ['Stock Prediction', 'Comparative Metrics']:
        start = st.date_input('Start Date', datetime.date(1900, 1, 1))
        end = st.date_input('End Date', datetime.date.today())

        stock_df = pd.read_csv("StockStreamTickersData.csv")

        # Stock Prediction Section
        if selected == 'Stock Prediction':
            st.subheader("Stock Prediction")
            tickers = stock_df["Company Name"]
            a = st.selectbox('Pick a Company', tickers)

            with st.spinner('Loading...'):
                time.sleep(2)

            dict_csv = pd.read_csv('StockStreamTickersData.csv', header=None, index_col=0).to_dict()[1]
            symb_list = [dict_csv.get(a)]

            if not a:
                st.write("Enter a Stock Name")
            else:
                data = yf.download(symb_list, start=start, end=end)
                data.reset_index(inplace=True)
                st.subheader(f'Raw Data of {a}')
                st.write(data)

                def plot_raw_data():
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
                    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
                    fig.layout.update(title_text=f'Time Series Data of {a}', xaxis_rangeslider_visible=True)
                    st.plotly_chart(fig)

                plot_raw_data()
                n_years = st.slider('Years of Prediction:', 1, 4)
                period = n_years * 365

                df_train = data[['Date', 'Close']]
                df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

                m = Prophet()
                m.fit(df_train)
                future = m.make_future_dataframe(periods=period)
                forecast = m.predict(future)

                st.subheader(f'Forecast Data of {a}')
                st.write(forecast)

                st.subheader(f'Forecast Plot for {n_years} Years')
                fig1 = plot_plotly(m, forecast)
                st.plotly_chart(fig1)

                st.subheader(f"Forecast Components of {a}")
                fig2 = m.plot_components(forecast)
                st.write(fig2)

        # Comparative Analysis Section
        elif selected == 'Comparative Metrics':
            st.subheader("Comparative Analysis")
            analysis_type = st.radio(
                'Select Analysis Type',
                ['Sector Comparison']
            )

            if analysis_type == 'Sector Comparison':
                st.write("### Sector Comparison")

                # Load sector data
                sector_data = pd.read_csv('SectorData.csv')  # Ensure you have this CSV file
                sectors = sector_data['Sector'].unique()
                selected_sector = st.selectbox('Select a Sector', sectors)

                if selected_sector:
                    sector_companies = sector_data[sector_data['Sector'] == selected_sector]['Company Name']
                    dropdown = st.multiselect('Pick Your Assets', sector_companies)

                    # Load tickers data
                    dict_csv = pd.read_csv('StockStreamTickersData.csv', header=None, index_col=0).to_dict()[1]
                    symb_list = [dict_csv.get(i) for i in dropdown if dict_csv.get(i) is not None]

                    if len(symb_list) > 0:
                        with st.spinner('Fetching Data...'):
                            data = yf.download(symb_list, start=start, end=end)['Adj Close']
                        st.line_chart(data)

            # elif analysis_type == 'Peer Comparison':
            #     st.write("### Peer Comparison")

            #     # Load peers data
            #     peers_data = pd.read_csv('PeersData.csv')  # Ensure you have this CSV file
            #     st.write("Peers Data Columns:", peers_data.columns)  # Debugging output

            #     if 'Company Name' not in peers_data.columns or 'Peers' not in peers_data.columns:
            #         st.error("PeersData.csv must contain 'Company Name' and 'Peers' columns.")
            #     else:
            #         companies = peers_data['Company Name'].unique()
            #         selected_company = st.selectbox('Select a Company', companies)

            #         if selected_company:
            #             peer_companies = peers_data[peers_data['Company Name'] == selected_company]['Peers']
            #             st.write("Peers Found:", peer_companies.tolist())  # Debugging output
                        
            #             if peer_companies.empty:
            #                 st.write("No peers found for the selected company.")
            #             else:
            #                 dropdown = st.multiselect('Pick Peers to Compare', peer_companies.tolist())

            #                 # Load tickers data
            #                 dict_csv = pd.read_csv('StockStreamTickersData.csv', header=None, index_col=0).to_dict()[1]
            #                 st.write("Ticker Mapping:", dict_csv)  # Debugging output

            #                 symb_list = [dict_csv.get(i) for i in dropdown if dict_csv.get(i) is not None]
            #                 st.write("Selected Tickers:", symb_list)  # Debugging output

            #                 if len(symb_list) > 0:
            #                     with st.spinner('Fetching Data...'):
            #                         data = yf.download(symb_list, start=start, end=end)['Adj Close']
            #                     st.line_chart(data)
            #                 else:
            #                     st.write("No valid tickers selected.")