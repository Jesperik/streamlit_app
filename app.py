from datetime import datetime
import streamlit as st
import time

# IMPORTANT: Importing the class won't make Streamlit reinitialize it at each iteration. 
# See: https://docs.streamlit.io/develop/concepts/design/custom-classes
from my_class import MyClass



def main():
    st.session_state.setdefault('app_instance', MyClass())
    try:
        run(st.session_state.app_instance)
    except:
        st.error('ERROR: The program crashed unexpectedly!')

def run(app):
    initialize_states()
    display_header()
    display_body()
    display_footer()
    display_sidebar(app)
    get_data(app)
    display_plot(app)
    download_data(app)

def initialize_states():
    # Initialize session states
    if "stock" not in st.session_state:
            st.session_state.stock = None
    if "ma" not in st.session_state:
            st.session_state.ma = None
    if "start_date" not in st.session_state:
            st.session_state.start_date = None
    if "end_date" not in st.session_state:
            st.session_state.end_date = None
    if "plot" not in st.session_state:
            st.session_state.plot = False
    if "button" not in st.session_state:
            st.session_state.button = False

def display_header():
    st.title(':chart_with_upwards_trend: Stock Market Data Viewer :chart_with_downwards_trend:')
    st.markdown('This app allows you to view synthetic stock market data and plot a moving average trendline. '
                'The purpose of the app is to showcase some of the functionality of Streamlit.')

def display_body():
    ht, hm, hb = 25, 500, 100
    h = ht + hm + hb
    st.session_state.container_outer = st.container(height=h, border=True)
    with st.session_state.container_outer:
        st.session_state.container_top = st.container(height=ht, border=False)
        st.session_state.container_middle = st.container(height=hm, border=False)
        st.session_state.container_bottom = st.container(height=hb, border=False)
    with st.session_state.container_top:
        if "placeholder" not in st.session_state:
            st.session_state.placeholder = st.text('Press "Execute" in the sidebar pane to plot data.')

def display_footer():
    st.info('Use the sidebar to select a stock, set the moving average window, and visualize the data.')
    st.markdown('Created by [Jesper Eriksson](https://www.linkedin.com/in/jesper-eriksson000/)')

def display_sidebar(app):
    st.sidebar.header('User Input')
    st.session_state.stock = st.sidebar.selectbox('Select stock:', app.stocks.keys(), on_change=reset_states)
    st.session_state.start_date = st.sidebar.date_input('Start date', value=datetime(2020, 1, 1), on_change=reset_states)
    st.session_state.end_date = st.sidebar.date_input('End date', value=datetime(2023, 1, 1), on_change=reset_states)

    if st.sidebar.button('Execute'):
        st.session_state.placeholder.empty()
        with st.session_state.container_top:
            with st.spinner('Fetching data...'):
                time.sleep(3)
        st.session_state.button = True
        st.session_state.plot = True

    # Padding
    st.sidebar.markdown("##")

    st.session_state.ma = st.sidebar.slider('Select moving average window:', min_value=5, max_value=100, value=20, step=5, on_change=ma_changed, args=(app,))

def reset_states():
    st.session_state.stock = None
    st.session_state.ma = None
    st.session_state.start_date = None
    st.session_state.end_date = None
    st.session_state.plot = False
    st.session_state.button = False
    st.session_state.placeholder.text('Press "Execute" in the sidebar pane to plot data.')

def ma_changed(app):
    if st.session_state.button:
        # Update the moving average in the stock_data DataFrame
        st.session_state.placeholder.empty()
        app.stock_data['MA'] = app.stock_data['Close'].rolling(window=st.session_state.ma).mean()
        st.session_state.plot = True

def get_data(app):
    if st.session_state.button:
        app.set_states(st.session_state.start_date,
                       st.session_state.end_date,
                       st.session_state.ma)
        app.generate_data(st.session_state.stock)

def display_plot(app):
    with st.session_state.container_middle:
        if st.session_state.plot:
            tab1, tab2, tab3 = st.tabs(["Data", "Stats", "List"])
            with tab1:
                fig = app.plot_data(st.session_state.stock)
                st.plotly_chart(fig)
            with tab2:
                col1, col2, col3 = st.columns(3)
                col1.metric(label="Max", value=f"{app.stock_stats['max']} USD", delta=f"{round(app.stock_stats['max']-app.stock_stats['avg'], 1)} USD above average")
                col2.metric(label="Min", value=f"{app.stock_stats['min']} USD", delta=f"{round(app.stock_stats['min']-app.stock_stats['avg'], 1)} USD below average")
                col3.metric(label="Spread", value=f"{app.stock_stats['spread']} USD")
            with tab3:
                st.dataframe(app.stock_data, hide_index=True, use_container_width=True)

def download_data(app):
    if st.session_state.button:
        with st.session_state.container_bottom:
            csv = convert_df(app.stock_data)

            st.download_button(label="Download data as CSV",
                            data=csv,
                            file_name=f"{st.session_state.stock}_stock_data.csv",
                            mime="text/csv",)

# IMPORTANT: Cache the conversion to prevent computation on every rerun
# See: https://docs.streamlit.io/develop/concepts/architecture/caching
@st.cache_data
def convert_df(df):
    return df.to_csv().encode("utf-8")



# Run the app
if __name__ == '__main__':
    main()
