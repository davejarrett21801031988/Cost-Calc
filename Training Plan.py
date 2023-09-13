import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

#users
names = ["David Jarrett", "Nicola Jarrett"]
usernames = ["djarrett", "njarrett"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "Cost_Calculator", "abcde", cookie_expiry_days = 30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

        st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
        st.title(":runner: Training Plan")
        st.markdown("##")

        #fixed_rate_mortgage(interest, years, payments_year, loan, start_date)

        # CSS to inject contained in a string
        hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        col_1, col_2, col_3, col_4 = st.columns(4)
        with col_1:
            fn_Hours = st.text_input("Maximum Hours per Week", value = 10, key = "Hours")
        with col_2:
            fn_Weeks = st.text_input("Weeks to Race", value = 10, key = "Weeks")
        with col_3:
            fn_Race = st.text_input("Race", value = 'Marathon', key = "Race")
        with col_4:
            fn_Target = st.text_input("Target Time", value = '02:29:59', key = "Target")
        st.markdown("##")

        Target_Pace = int(150/42.2) + (int((((150/42.2)-int(150/42.2))*60))/100)
        #day_phrase = str('Day ')+str(this_day)+str(' of ')+str(daysinmonth)
        Easy_Pace = Target_Pace + 1
        Speed_Pace = Target_Pace - 0.25

        first, left_column, right_column, mid_column, last = st.columns(5)
        with first:
            st.text("Target Race Pace:")
            st.subheader(f"{Target_Pace:,.2f}")
        with left_column:
            st.text("Easy Pace:")
            st.subheader(f"{Easy_Pace:,.2f}")
        with right_column:
            st.text("Speed Work Pace (1km):")
            st.subheader(f"{Speed_Pace:,.2f}")
        with mid_column:
            st.text("X:")
            #st.subheader(f"{(Total_Original_Payments - Total_Payments)/12:,.1f}")
        with last:
            st.text("Y:")
            #st.subheader(f"{Total_Payments/12:,.1f}")
        st.markdown("##")

        Biggest_Week = int(0.75 * int(fn_Weeks))
        #BW_RunningDistance = (BW_EasyRunning*4.5) + (BW_Speedwork*3.5)

        df_t = pd.DataFrame(columns=['Week', 'Easy Running', 'Speedwork', 'Cross Training', 'Running Distance', 'Running Time', 'Total Time', 'Index', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Total'])
        df_t['Week'] = list(range(1,int(fn_Weeks)+1))
        df_t['Index'] = df_t['Week'] - Biggest_Week
        df_t['Index'] = abs(df_t['Index'])
        df_t['Total Time'] = int(fn_Hours) * (1 - (df_t['Index'] * 0.07))
        df_t['Running Time'] = 0.7 * df_t['Total Time']
        df_t['Easy Running'] = 0.8 * df_t['Running Time']
        df_t['Speedwork'] = df_t['Running Time'] - df_t['Easy Running']
        df_t['Cross Training'] = df_t['Total Time'] - df_t['Running Time']
        df_t['Running Distance'] = (df_t['Easy Running'] * (60 / Easy_Pace)) + (df_t['Speedwork'] * (60 / (Speed_Pace + 0.25)))
        df_t['Mon X'] = (df_t['Cross Training'] * 0.33) * 60
        df_t['Wed X'] = (df_t['Cross Training'] * 0.33) * 60
        df_t['Fri X'] = (df_t['Cross Training'] * 0.33) * 60
        df_t['Sun'] = (df_t['Easy Running'] * (60 / Easy_Pace)) * 0.4
        df_t['Wed'] = (df_t['Easy Running'] * (60 / Easy_Pace)) * 0.18
        df_t['Fri'] = (df_t['Easy Running'] * (60 / Easy_Pace)) * 0.14
        df_t['Mon'] = (df_t['Easy Running'] * (60 / Easy_Pace)) * 0.08
        df_t['Tue Easy'] = ((df_t['Easy Running'] * (60 / Easy_Pace)) * 0.05)
        df_t['Tue Fast'] = ((df_t['Speedwork'] * (60 / (Speed_Pace + 0.25))) * 0.25)
        df_t['Thu Easy'] = ((df_t['Easy Running'] * (60 / Easy_Pace)) * 0.07)
        df_t['Thu Fast'] = ((df_t['Speedwork'] * (60 / (Speed_Pace + 0.25))) * 0.35)
        df_t['Sat Easy'] = ((df_t['Easy Running'] * (60 / Easy_Pace)) * 0.07)
        df_t['Sat Fast'] = ((df_t['Speedwork'] * (60 / (Speed_Pace + 0.25))) * 0.40)
        df_t['Total'] = df_t['Sun'] + df_t['Wed'] + df_t['Fri'] + df_t['Mon'] + df_t['Tue'] + df_t['Thu'] + df_t['Sat'] - df_t['Running Distance']
        df_t['Mon'] = df_t['Mon'].map('{:,.1f}km'.format) + ' + ' + df_t['Mon X'].map('{:,.0f}mins XTraining'.format)
        df_t['Tue'] = df_t['Tue Easy'].map('{:,.1f}km Easy'.format) + ' + ' + df_t['Tue Fast'].map('{:,.1f}km Fast'.format)
        df_t['Wed'] = df_t['Wed'].map('{:,.1f}km'.format) + ' + ' + df_t['Wed X'].map('{:,.0f}mins XTraining'.format)
        df_t['Thu'] = df_t['Thu Easy'].map('{:,.1f}km Easy'.format) + ' + ' + df_t['Thu Fast'].map('{:,.1f}km Fast'.format)
        df_t['Fri'] = df_t['Fri'].map('{:,.1f}km'.format) + ' + ' + df_t['Fri X'].map('{:,.0f}mins XTraining'.format)
        df_t['Sat'] = df_t['Sat Easy'].map('{:,.1f}km Easy'.format) + ' + ' + df_t['Sat Fast'].map('{:,.1f}km Fast'.format)
        df_t['Sun'] = df_t['Sun'].map('{:,.1f}km'.format)
        df_t['Running Distance'] = df_t['Running Distance'].map('{:,.1f}km'.format)
        df_t['Total Time'] = df_t['Total Time'].map('{:,.1f}hrs'.format)

        #st.subheader("Spend Rate for the Month")
        #st.text("With the current rate of spending in the Month, are we predicted to go over/under the Average Monthly Spend?")
        #st.text(day_phrase)
        st.table(df_t[['Week', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Running Distance', 'Total Time']])
        st.markdown("---")

        #print(Biggest_Week)
        #print(BW_TotalRunning)
        #print(BW_EasyRunning)
        #print(BW_Speedwork)
        #print(BW_XTraining)
