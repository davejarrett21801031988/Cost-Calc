import firebase_admin
import pandas as pd
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
from datetime import date
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
import json
import calendar
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import numpy_financial as npf
import numpy as np
from collections import OrderedDict
from dateutil.relativedelta import *
import plotly.graph_objects as go
#import matplotlib.pyplot as plt
#from pywaffle import Waffle

if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAK.json')

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://costcalculator-bd26f-default-rtdb.firebaseio.com'
        })

st.set_page_config(page_title="Cost Calculator",
                page_icon=":moneybag:",
                layout="wide"
)

#user
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

    #read data
    data = db.reference('py/Transactions').get()
    #print(len(data))
    df = pd.json_normalize(data)
    df2 = pd.DataFrame(columns=['Transaction_ID', 'Item', 'Amount', 'Who', 'Category', 'Percentage_Split'])
    #print(df2)

    for key in data.keys():
        Transaction_ID = key
        #print(Transaction_ID)
        jsondata = pd.json_normalize(data[Transaction_ID])
        jsondata["Transaction_ID"] = Transaction_ID
        #print(jsondata)
        df3 = pd.concat([jsondata, df2], ignore_index=True)
        df2 = df3

    #print(df3)

    df3["Transaction_ID"] = df3["Transaction_ID"].astype(str)
    df3["Amount"] = df3["Amount"].astype(float)
    df3["Item Count"] = 1
    df3["Date"] = df3["Transaction_ID"].str[:8]
    df3["Amount Spent"] = df3["Amount"].astype(str)
    df3["Amount Spent"] = "£"+df3["Amount Spent"]
    df3["Day"] = df3["Transaction_ID"].str[0:2]
    df3["Day"] = df3["Day"].astype(int)
    df3["Month"] = df3["Transaction_ID"].str[2:4]
    df3["Month"] = df3["Month"].astype(int)
    #df3['Month Name'] = df3["Month"].apply(lambda x: calendar.month_abbr[x])
    df3["Year"] = df3["Transaction_ID"].str[4:8]
    df3["Year"] = df3["Year"].astype(int)
    df3["Hour"] = df3["Transaction_ID"].str[8:10]
    df3["Hour"] = df3["Hour"].astype(int)
    df3["Minute"] = df3["Transaction_ID"].str[10:12]
    df3["Minute"] = df3["Minute"].astype(int)
    df3["Second"] = df3["Transaction_ID"].str[12:14]
    df3["Second"] = df3["Second"].astype(int)
    df3["Per"] = df3["Percentage_Split"].astype(float)
    df3["Dave_Owe"] = df3["Amount"] * (df3["Per"] / 100)
    df3["Niki_Owe"] = df3["Amount"] * (1-(df3["Per"]  / 100))
    df3["Percentage Split (Dave)"] = df3["Percentage_Split"].astype(str)
    df3["Date"] = pd.to_datetime(df3[['Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']])
    #df3["Period"] = df3["Date"].dt.to_period('M')
    df3["Period"] = df3["Year"].astype(str) + '-' + df3["Month"].astype(str)
    df3["Period"] = df3["Period"].astype(str)
    df3["Month"] = df3["Month"].apply(lambda x: calendar.month_abbr[x])

    df3_slim = df3[['Period','Category','Amount']]
    df3_complete = (
        df3_slim.groupby(by=["Period","Category"],as_index=False).sum(["Amount"])
    )
    df3_complete["Concat"] = df3_complete["Period"] + df3_complete["Category"]
    #print(df3_complete)

    #df3.info()
    optionsperiods = ['2022-4','2022-5']
    df_periods = pd.DataFrame(columns=['Period', 'Join'])
    df_categories = pd.DataFrame(columns=['Category', 'Join'])
    df_periods["Period"] = df3["Period"].unique()
    df_periods["Join"] = 1
    df_categories["Category"] = df3["Category"].unique()
    df_categories["Join"] = 1
    df_distincts = df_periods.merge(df_categories, on='Join', how='left')
    df_distincts["Concat"] = df_distincts["Period"] + df_distincts["Category"]
    df_distincts = df_distincts[~df_distincts["Period"].isin(optionsperiods)]
    #CarTest = ['Cars']
    #df_distincts = df_distincts[df_distincts["Category"].isin(CarTest)]
    #df_distincts = df_distincts[~df_distincts["Period"].isin(this_period)]
    #print(df_distincts)

    df_join = df_distincts.merge(df3_complete, on='Concat', how='left')
    df_join = df_join[['Amount','Category_x','Period_x']].sort_values(by=["Period_x", "Category_x"])
    df_join["Amount"] = df_join["Amount"].fillna(0)
    zeroes = [0]
    df_join = df_join[df_join["Amount"].isin(zeroes)]
    df_join = df_join.rename(columns={'Category_x': 'Category', 'Period_x': 'Period'})
    df_join["Item"] = ""
    df_join["Percentage_Split"] = 50
    df_join["Dave_Owe"] = 0
    df_join["Niki_Owe"] = 0
    df_join["Percentage Split (Dave)"] = 50
    df_join["Per"] = 50
    df_join["Amount Spent"] = '£0'
    df_join["Who"] = 'Dave'
    df_join["Year"] = df_join["Period"].str[0:4]
    df_join["Year"] = df_join["Year"].astype(int)
    df_join["Month"] = df_join["Period"].str[5:7]
    df_join["Month"] = df_join["Month"].astype(int)
    df_join["Day"] = 1
    df_join["Hour"] = 1
    df_join["Minute"] = 1
    df_join["Second"] = 1
    df_join["Item Count"] = 1
    df_join["Transaction_ID"] = '99999999999999'
    #print(df_join)
    df_join["Date"] = pd.to_datetime(df_join[['Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']])
    #print(df_join)
    #print(df3)
    df_join_full = pd.concat([df_join, df3])#, ignore_index=True)
    #print(df_join_full)

    df3 = df_join_full
    unique_categories = df3["Category"].unique()
    default_categories = [category for category in unique_categories if category != 'Extension']

    # ---Sidebar---
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")
    st.sidebar.header("Please filter here:")
    Who_Sidebar = st.sidebar.multiselect(
        "Who:",
        options=df3["Who"].unique(),
        default=df3["Who"].unique()
    )
    Month_Sidebar = st.sidebar.multiselect(
        "Month:",
        options=df3["Period"].unique(),
        default=df3["Period"].unique()
    )
    Category_Sidebar = st.sidebar.multiselect(
        "Category:",
        options=unique_categories,
        default=default_categories
    )

    df_selection = df3.query(
        "Who == @Who_Sidebar & Period == @Month_Sidebar & Category == @Category_Sidebar"
    )

    options1 = ['Niki']
    Niki_df = df3[df3['Who'].isin(options1)]

    options2 = ['Dave']
    Dave_df = df3[df3['Who'].isin(options2)]

    options3 = ['Balancing Figure']
    Spend_df = df_selection[~df_selection['Category'].isin(options3)]

    Total_Spent = Spend_df["Amount"].sum()
    Total_Spent = "£"+"{:,.2f}".format(Total_Spent)
    Total_Items = Spend_df["Item Count"].sum()
    Owage = (Niki_df["Dave_Owe"].sum() - Dave_df["Niki_Owe"].sum())
    #print(Niki_df)
    #print(Dave_df)
    if Owage < 0:
        Owage = (Dave_df["Niki_Owe"].sum() - Niki_df["Dave_Owe"].sum())
        Owage = "£"+"{:,.2f}".format(Owage)
        Owage_Title = "Niki owes Dave:"
    else:
        Owage = "£"+"{:,.2f}".format(Owage)
        Owage_Title = "Dave owes Niki:"

    #bar chart 1
    #amount_by_person = px.df3
    #print(amount_by_person)
    #amount_by_person.info()

    amount_by_person = Spend_df[["Who","Category","Amount"]]

    amount_by_person_grouped = (
        amount_by_person.groupby(by=["Who","Category"],as_index=False).sum(["Amount"]).sort_values(by=["Who"])
    )

    #print (amount_by_person_grouped)

    fig_amount_by_person = px.bar(
        data_frame = amount_by_person_grouped,
        x="Who",
        y="Amount",
        color="Category",
        color_discrete_map={
                "Cats": "lightsteelblue",
                "Drinks": "cornflowerblue",
                "House Bills": "royalblue",
                "Food": "lavender",
                "Guildford Flat": "midnightblue",
                "Fuel": "navy",
                "Other Bills": "darkblue",
                "Mortgage Interest": "mediumblue",
                "Mortgage Capital": "blue",
                "Balancing Figure": "slateblue",
                "Dog": "darkslateblue",
                "Fun": "mediumslateblue",
                "House Stuff": "mediumpurple",
                "Cars": "indigo",
                "Baby": "darkorchid",
                "Extension": "thistle",
                "Childcare": "navy"
                },
        #orientation = "h",
        title="Amount per Person ",
        #template="plotly_white",
    )
    fig_amount_by_person.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False)),
        yaxis=(dict(showgrid=False)),
        #showlegend=False,
    )

    amount_by_month = Spend_df[["Period","Category","Amount"]]

    amount_by_month_grouped = (
        amount_by_month.groupby(by=["Period","Category"],as_index=False).sum(["Amount"]).sort_values(by=["Period"])
    )
    #print(amount_by_month_grouped)

    t = datetime.now()
    this_year = int(t.strftime("%Y"))
    this_month = int(t.strftime("%m"))
    this_day = int(t.strftime("%d"))
    daysinmonth = calendar.monthrange(this_year, this_month)[1]

    if this_month == 1:
        previous_period = str(this_year - 1) + '-12'
    else:
        previous_period = str(this_year) + '-' + str(this_month - 1)
    previous_period = [previous_period]
    #print(previous_period)

    #print(this_day)
    this_year = str(this_year)
    this_month = str(this_month)
    this_period = this_year + '-' + this_month
    #this_period = this_period.astype(str)
    this_period = [this_period]
    #print(this_period)

    day_phrase = str('Day ')+str(this_day)+str(' of ')+str(daysinmonth)
    #print(day_phrase)

    amount_by_month_grouped_notthismonth = amount_by_month_grouped[~amount_by_month_grouped["Period"].isin(this_period)]
    amount_by_month_grouped_thismonth = amount_by_month_grouped[amount_by_month_grouped["Period"].isin(this_period)]
    #print(amount_by_month_grouped_notthismonth)
    #print(amount_by_month_bills_6)

    periodcalc = amount_by_month_grouped_notthismonth.loc[:, ['Period']]
    periodcalc["Periods"] = 1
    periodcalc_2 = (
        periodcalc.groupby(by=["Period"],as_index=False).sum(["Periods"])
    )
    periodcalc_2["Periods"] = 1
    periodcalc_3 = (
        periodcalc_2.groupby(by=["Period"],as_index=False).sum(["Periods"])
    )
    options333 = ['2022-4','2022-5']
    #options333 = options333.reshape(-1,1)
    periodcalc_4 = periodcalc_3[~periodcalc_3['Period'].isin(options333)]
    periodcalc_5 = periodcalc_4["Periods"].sum()
    #print(options333)
    #print(periodcalc_3)

    amount_by_month_bills_1 = Spend_df[["Period","Category","Item","Amount"]]
    amount_by_month_bills_2 = (
        amount_by_month_bills_1.groupby(by=["Period","Category","Item"],as_index=False).sum(["Amount"]).sort_values(by=["Period"])
    )
    options_bills = ["House Bills"]
    amount_by_month_bills_3 = amount_by_month_bills_2[amount_by_month_bills_2["Category"].isin(options_bills)]
    amount_by_month_bills_4 = amount_by_month_bills_3[~amount_by_month_bills_3["Period"].isin(this_period)]
    amount_by_month_bills_5 = (
        amount_by_month_bills_4.groupby(by=["Item"],as_index=False).sum(["Amount"])
    )
    amount_by_month_bills_5_adj = pd.DataFrame(columns=['Item','Adj_Amount'])
    amount_by_month_bills_5_adj['Item'] = ['Council Tax','TV Licence','Water','Road Fund','Internet','Gas & Electricity','Building & Contents Insurance','Amazon Prime','BT Sport','Ring','Netflix','Firelighters and Wood','Cashback','Spotify']
    amount_by_month_bills_5_adj['Adj_Amount'] = [1980.36,92.75,161.64,0,145.76,493.41,489.39,98.75,175,49.98,0,0,-6.24,0]
    amount_by_month_bills_6 = amount_by_month_bills_5.merge(amount_by_month_bills_5_adj, on='Item', how='outer')
    amount_by_month_bills_6['Overall Amount'] = amount_by_month_bills_6['Adj_Amount'].fillna(0) + amount_by_month_bills_6['Amount'].fillna(0)
    amount_by_month_bills_7 = amount_by_month_bills_6[['Item','Overall Amount']].sort_values(by=['Overall Amount'], ascending=False)
    #print(amount_by_month_bills_6)
    months_done = (periodcalc_5 + 7)
    month_phrase = str(months_done) + str(' complete Months')
    amount_by_month_bills_7['Monthly Cost'] = amount_by_month_bills_7['Overall Amount'] / months_done
    amount_by_month_bills_7['Overall Amount'] = amount_by_month_bills_7['Overall Amount'].map('£{:,.2f}'.format)
    amount_by_month_bills_7['Monthly Cost'] = amount_by_month_bills_7['Monthly Cost'].map('£{:,.2f}'.format)

    amount_by_month_grouped_notthismonth_pie = amount_by_month_grouped_notthismonth[['Category','Amount']]
    amount_by_month_grouped_notthismonth_pie_2 = (
        amount_by_month_grouped_notthismonth_pie.groupby(by=["Category"],as_index=False).sum(["Amount"])
    )
    #print(amount_by_month_grouped_notthismonth_pie)

    amount_by_month_grouped_notthismonth_pie_2["Average Spend"] = amount_by_month_grouped_notthismonth_pie_2["Amount"]/periodcalc_5
    amount_by_month_grouped_notthismonth_pie_3 = amount_by_month_grouped_notthismonth_pie_2[['Category','Average Spend']]
    optionsa = ['Guildford Flat']
    amount_by_month_grouped_notthismonth_pie_4 = amount_by_month_grouped_notthismonth_pie_3[~amount_by_month_grouped_notthismonth_pie_3["Category"].isin(optionsa)].sort_values(by=["Category"])
    #print(amount_by_month_grouped_notthismonth_pie_4)
    #print(amount_by_month_grouped_thismonth)
    spend_rate = amount_by_month_grouped_notthismonth_pie_4.merge(amount_by_month_grouped_thismonth, on='Category', how='left')
    spend_rate_2 = spend_rate
    spend_rate_2['Spend this Month'] = spend_rate_2['Amount']
    spend_rate_3 = spend_rate_2.loc[:, ['Category','Average Spend','Spend this Month']]
    spend_rate_3['Spend Rate Average'] = spend_rate_2['Average Spend']*(this_day/daysinmonth)
    spend_rate_3['Spend Rate'] = (spend_rate_2['Spend this Month']/spend_rate_3['Spend Rate Average'])-1
    spend_rate_3 = spend_rate_3.sort_values(by=['Spend Rate'], ascending=False)
    spend_rate_3 = spend_rate_3.fillna(0)
    spend_rate_3["Average Monthly Spend"] = spend_rate_3["Average Spend"]
    spend_rate_4 = spend_rate_3.loc[:, ['Category','Average Monthly Spend','Spend this Month','Spend Rate']]
    spend_rate_4['Average Monthly Spend'] = spend_rate_4['Average Monthly Spend'].map('£{:,.2f}'.format)
    spend_rate_4['Spend this Month'] = spend_rate_4['Spend this Month'].map('£{:,.2f}'.format)
    spend_rate_4['Spend Rate'] = spend_rate_4['Spend Rate']*100
    if spend_rate_4.empty:
        dummy = 1
    else:
        spend_rate_4.loc[spend_rate_4['Spend Rate'] > 0 , 'Status'] = 'Over Spending!'
        spend_rate_4.loc[spend_rate_4['Spend Rate'] <= 0 , 'Status'] = ''

    # values are split at decimal point
    #lst = []
    #for each in spend_rate_4['Spend Rate']:
    #    lst.append(str(each).split('.')[0])

    # all values converting to integer data type
    #spend_rate_4['Spend Rate'] = [int(i) for i in lst]
    #print(final_list)

    spend_rate_4['Spend Rate'] = spend_rate_4['Spend Rate'].map('{:,.1f}%'.format)
    spend_rate_5 = spend_rate_4

    average_by_month = Spend_df[["Period","Amount"]]
    average_by_month = average_by_month[~average_by_month["Period"].isin(this_period)]

    average_by_month_grouped = (
        average_by_month.groupby(by=["Period"],as_index=False).sum(["Amount"]).sort_values(by=["Period"])
    )

    optionsperiods = ['2022-4','2022-5']
    Average_spend_df = average_by_month_grouped[~average_by_month_grouped["Period"].isin(optionsperiods)]
    #print(Average_spend_df)

    #print(list(Spend_df_2))
    #print(average_by_month_grouped)
    #print(Average_spend)

    options77 = ['Guildford Flat']
    amount_by_month_grouped_2 = amount_by_month_grouped[~amount_by_month_grouped["Category"].isin(options77)].sort_values(by=["Category"])
    amount_by_month_grouped_2['Amount Text'] = amount_by_month_grouped_2['Amount'].map('£{:,.2f}'.format)
    average_by_month_total = (
        amount_by_month_grouped_2.groupby(by=["Period"],as_index=False).sum(["Amount"]).sort_values(by=["Period"])
    )
    average_by_month_total['Amount Text'] = average_by_month_total['Amount'].map('£{:,.2f}'.format)
    #print(average_by_month_total)
    #print(amount_by_month_grouped_2)

    amount_by_month_grouped_flat = df3[df3["Category"].isin(options77)]
    GuildfordStart = 29273.753
    amount_by_month_grouped_flat_figure = -amount_by_month_grouped_flat["Amount"].sum() + GuildfordStart
    amount_by_month_grouped_flat_figure = "£"+"{:,.2f}".format(amount_by_month_grouped_flat_figure)
    if amount_by_month_grouped_flat_figure == '£-0.00':
        amount_by_month_grouped_flat_figure = '£0.00'
    #print(amount_by_month_grouped_flat_figure)

    average_by_month_99 = Spend_df[["Period","Amount","Category"]]
    average_by_month_99 = average_by_month_99[~average_by_month_99["Period"].isin(this_period)]
    average_by_month_99 = average_by_month_99[~average_by_month_99["Period"].isin(optionsperiods)]
    average_by_month_99 = average_by_month_99[~average_by_month_99["Category"].isin(options77)]
    #print(average_by_month_99)
    average_by_month_grouped_99 = (
        average_by_month_99.groupby(by=["Period"],as_index=False).sum(["Amount"]).sort_values(by=["Period"])
    )
    #print(average_by_month_grouped_99)
    average_by_month_grouped_99_Previous = average_by_month_grouped_99[~average_by_month_grouped_99["Period"].isin(previous_period)]
    #print(average_by_month_grouped_99_Previous)

    if average_by_month_grouped_99.empty:
        Average_spend = "£0.00"
        Average_Mortgage_Capital = "£0.00"
    else:
        Average_spend = average_by_month_grouped_99["Amount"].mean()

        Average_spend_Previous = average_by_month_grouped_99_Previous["Amount"].mean()

        #print(Average_spend
        #print(Average_spend_Previous

        df_selection_cap = df3.query(
            "Period == @Month_Sidebar & Category == 'Mortgage Capital'"
        )
        amount_by_month_cap = df_selection_cap[["Period","Category","Amount"]]
        amount_by_month_grouped_cap = (
            amount_by_month_cap.groupby(by=["Period","Category"],as_index=False).sum(["Amount"]).sort_values(by=["Period"])
        )

        #Mortgage_Capital = [1841.74,1839.79,1837.86,1835.91,1833.98]
        #options77_cap = ['Mortgage Capital']
        #Mortgage_Capital_df = amount_by_month_grouped[amount_by_month_grouped["Category"].isin(options77_cap)]
        Mortgage_Capital_df = amount_by_month_grouped_cap[~amount_by_month_grouped_cap["Period"].isin(this_period)]
        #print(Mortgage_Capital_df)
        Average_Mortgage_Capital = Mortgage_Capital_df["Amount"].mean()
        Average_Mortgage_Capital_perc = (Average_Mortgage_Capital / Average_spend)*100
        if (np.isnan(Average_Mortgage_Capital)):
            Average_Mortgage_Capital = 0
        if (np.isnan(Average_Mortgage_Capital_perc)):
            Average_Mortgage_Capital_perc = 0
        Average_Mortgage_Capital = "£"+"{:,.2f}".format(Average_Mortgage_Capital)
        Average_Mortgage_Capital_perc = "{:,.1f}%".format(Average_Mortgage_Capital_perc)
        Average_Mortgage_Capital = Average_Mortgage_Capital+" ("+Average_Mortgage_Capital_perc+") "
        #print(Average_Mortgage_Capital_perc)

        Average_Spend_Change = Average_spend - Average_spend_Previous
        #print(Average_Spend_Change)
        if Average_Spend_Change >= 0:
            Average_Spend_Change = "£"+"{:,.2f}".format(Average_Spend_Change)
        else:
            Average_Spend_Change = "-£"+"{:,.2f}".format(Average_Spend_Change*-1)
        Average_spend = "£"+"{:,.2f}".format(Average_spend)
        Average_spend = Average_spend+" ("+Average_Spend_Change+") "


    # Calculate the 3-month rolling average
    average_by_month_total['Rolling_Avg'] = average_by_month_total['Amount'].rolling(window=12).mean()

    #bar chart
    fig_line = px.bar(
        data_frame = amount_by_month_grouped_2,
        x = "Period",
        y = "Amount",
        #text = "Amount Text",
        color = "Category",
        color_discrete_map={
                "Cats": "lightsteelblue",
                "Drinks": "cornflowerblue",
                "House Bills": "royalblue",
                "Food": "lavender",
                "Guildford Flat": "midnightblue",
                "Fuel": "navy",
                "Other Bills": "darkblue",
                "Mortgage Interest": "mediumblue",
                "Mortgage Capital": "blue",
                "Balancing Figure": "slateblue",
                "Dog": "darkslateblue",
                "Fun": "mediumslateblue",
                "House Stuff": "mediumpurple",
                "Cars": "indigo",
                "Baby": "darkorchid",
                "Extension": "thistle",
                "Childcare": "navy"
                },
        title = "Spend per Month",
        #template="plotly_white",
    )
    fig_line.add_trace(go.Scatter(
        x=average_by_month_total['Period'],
        y=average_by_month_total['Amount'],
        text=average_by_month_total['Amount Text'],
        mode='text',
        textposition='top center',
        textfont=dict(
            size=12,
        ),
        showlegend=False
    ))
    fig_line.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y")
    fig_line.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False)),
        yaxis=(dict(showgrid=False)),
        #showlegend=False,
    )

    # Add the rolling average line
    fig_line.add_scatter(
        x=average_by_month_total["Period"],
        y=average_by_month_total["Rolling_Avg"],
        mode='markers',
        name='12-Month Rolling Average',
        line=dict(color='red'),
    )

    # Format hover text for Amount values as British pounds (£)
    fig_line.update_traces(
        hovertemplate='Period: %{x}<br>Amount: £%{y}'
    )

#    # Get the unique categories from your data
#    categories = amount_by_month_grouped_notthismonth_pie_4['Category'].unique()
#
#    # Define the color map with the same length as the number of categories
#    color_map = {
#        "Cats": "lightsteelblue",
#        "Drinks": "cornflowerblue",
#        "House Bills": "royalblue",
#        "Food": "lavender",
#        "Guildford Flat": "midnightblue",
#        "Fuel": "navy",
#        "Other Bills": "darkblue",
#        "Mortgage Interest": "mediumblue",
#        "Mortgage Capital": "blue",
#        "Balancing Figure": "slateblue",
#        "Dog": "darkslateblue",
#        "Fun": "mediumslateblue",
#        "House Stuff": "mediumpurple",
#        "Cars": "indigo",
#        "Baby": "darkorchid",
#        "Extension": "thistle"
#    }
#
#    # Filter the color map to include only the categories present in your data
#    filtered_color_map = {category: color_map[category] for category in categories if category in color_map}
#
#    # Convert the data frame to a dictionary
#    data = amount_by_month_grouped_notthismonth_pie_4.set_index('Category')['Average Spend'].to_dict()
#
#    fig_pie = plt.figure(
#        FigureClass=Waffle,
#        rows=10,  # Adjust the number of rows to change the aspect ratio
#        values=data,
#        colors=[filtered_color_map[category] for category in data.keys()],
#        title={'label': 'Average Spend per Month', 'loc': 'center'},
#        legend={'loc': 'upper left', 'bbox_to_anchor': (1, 1)}
#    )

    fig_pie = px.pie(
        data_frame = amount_by_month_grouped_notthismonth_pie_4,
        labels = "Category",
        values = "Average Spend",
        #sort = False,
        names = "Category",
        #layout_showlegend = True,
        color = "Category",
        color_discrete_map={
                "Cats": "lightsteelblue",
                "Drinks": "cornflowerblue",
                "House Bills": "royalblue",
                "Food": "lavender",
                "Guildford Flat": "midnightblue",
                "Fuel": "navy",
                "Other Bills": "darkblue",
                "Mortgage Interest": "mediumblue",
                "Mortgage Capital": "blue",
                "Balancing Figure": "slateblue",
                "Dog": "darkslateblue",
                "Fun": "mediumslateblue",
                "House Stuff": "mediumpurple",
                "Cars": "indigo",
                "Baby": "darkorchid",
                "Extension": "thistle",
                "Childcare": "navy"
                },
        #category_orders = dict(Category=[
        #        "Cats",
        #        "Drinks",
        #        "House Bills",
        #        "Food",
        #        "Guildford Flat",
        #        "Fuel",
        #        "Other Bills",
        #        "Mortgage Interest",
        #        "Mortgage Capital",
        #        "Balancing Figure",
        #        "Dog",
        #        "Fun",
        #        "House Stuff",
        #        "Cars"
        #        ]),
        title = "Average Spend per Month"
        )

    #fig_pie.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    #read data
    data_car = db.reference('py/Cars').get()
    df_car = pd.json_normalize(data_car)
    df2_car = pd.DataFrame(columns=['Mileage'])
    #print(df2_car)

    for key in data_car.keys():
        Car = key
        #print(Transaction_ID)
        jsondata = pd.json_normalize(data_car[Car])
        jsondata["Car"] = Car
        #print(jsondata)
        df3_car = pd.concat([jsondata, df2_car], ignore_index=True)
        df2_car = df3_car

    #print(df3_car)

    cars_1 = pd.DataFrame(columns=['Car','Registration','Registered Date','Purchase Date','Purchase Days','Registered Days','Starting Mileage (Us)','Our Mileage','Annual Mileage (Us)','Annual Mileage (Total)','Estimated Value','Today'])
    cars_1['Car'] = ['Mazda CX-5','Peugeot 308','Mercedes A45','Mazda MX-5','VW Polo']
    cars_1['Registration'] = ['HT68 JZR','EF15 UAC','HF64 PWX','HN13 LZW','RV60 VWD']
    cars_1['Registered Date'] = [date(2019,1,26),date(2015,6,19),date(2014,9,26),date(2013,6,30),date(2010,9,4)]
    cars_1['Purchase Date'] = [date(2019,1,26),date(2019,2,1),date(2016,12,13),date(2015,6,13),date(2013,9,14)]
    cars_1['Today'] = [date.today(),date.today(),date(2019,1,26),date(2019,2,1),date(2016,12,13)]
    cars_1['Registered Days'] = cars_1['Today'] - cars_1['Registered Date']
#   print('------------------------NEW ROW---------------------------------')
#   print(cars_1['Registered Days'].dtype)
    cars_1['Registered Days'] = cars_1['Registered Days'].astype(str)
#   print(cars_1['Registered Days'])
    cars_1['Registered Days'] = cars_1['Registered Days'].str.split(' ').str[0].astype(int)
#   print(cars_1['Registered Days'])
    cars_1['Registered Days'] = cars_1['Registered Days']/365
#   print(cars_1['Registered Days'])
#   print(cars_1['Registered Days'].dtype)
    cars_1['Purchase Days Orig'] = cars_1['Today'] - cars_1['Purchase Date']
    cars_1['Purchase Days Orig'] = cars_1['Purchase Days Orig'].astype(str)
    cars_1['Purchase Days'] = (cars_1['Purchase Days Orig'].str.split(' ').str[0].astype(int))/365
#   print(cars_1['Purchase Days Orig'])
    cars_1['Years'] = cars_1['Purchase Days'].map('{:,.1f}'.format)
    cars_1['Purchase Months'] = (cars_1['Purchase Days Orig'].str.split(' ').str[0].astype(int))/30.42
    cars_1['Starting Mileage (Us)'] = [5,32460,11996,20000,23016]
    cars_1 = cars_1.merge(df2_car, on='Car', how='left')
    cars_1['Mileage'] = cars_1['Mileage'].astype(int)
    cars_1['Our Mileage'] = cars_1['Mileage'] - cars_1['Starting Mileage (Us)']
    cars_1['Annual Mileage (Us)'] = cars_1['Our Mileage'] / cars_1['Purchase Days']
    cars_1['Annual Mileage (Total)'] = cars_1['Mileage'] / cars_1['Registered Days']
    cars_1['Estimated/Sold Value'] = [18000,5000,1778.04,6800,3000]
    cars_1['Annual Mileage (Total)'] = cars_1['Annual Mileage (Total)'].map('{:,.1f}'.format)
    cars_1['Annual Mileage (Us)'] = cars_1['Annual Mileage (Us)'].map('{:,.1f}'.format)
    cars_1['Mileage'] = cars_1['Mileage'].map('{:,.1f}'.format)
#   print(cars_1)

    amount_by_month_cars_1 = Spend_df[["Period","Category","Item","Amount"]]
    amount_by_month_cars_2 = (
        amount_by_month_cars_1.groupby(by=["Period","Category","Item"],as_index=False).sum(["Amount"]).sort_values(by=["Period"])
    )
    options_cars = ["Cars"]
    amount_by_month_cars_3 = amount_by_month_cars_2[amount_by_month_cars_2["Category"].isin(options_cars)]
    amount_by_month_cars_4 = amount_by_month_cars_3[~amount_by_month_cars_3["Period"].isin(this_period)]
    amount_by_month_cars_5 = (
        amount_by_month_cars_4.groupby(by=["Item"],as_index=False).sum(["Amount"])
    )
    amount_by_month_cars_5_adj_308 = pd.DataFrame(columns=['Car','Item','Adj_Amount'])
    amount_by_month_cars_5_adj_308['Car'] = ['Peugeot 308','Peugeot 308','Peugeot 308','Peugeot 308','Peugeot 308']
    amount_by_month_cars_5_adj_308['Sub-Category'] = ['Payments','Recovery','Tax','Insurance','Servicing and Fixes']
    amount_by_month_cars_5_adj_308['Adj_Amount'] = [6950,59.6,0,1190.74,1780.73]

    amount_by_month_cars_5_adj_A45 = pd.DataFrame(columns=['Car','Item','Adj_Amount'])
    amount_by_month_cars_5_adj_A45['Car'] = ['Mercedes A45','Mercedes A45','Mercedes A45','Mercedes A45','Mercedes A45']
    amount_by_month_cars_5_adj_A45['Sub-Category'] = ['Payments','Recovery','Tax','Insurance','Servicing and Fixes']
    amount_by_month_cars_5_adj_A45['Adj_Amount'] = [13755.36,0,407.5,1885.35,1305.86]

    amount_by_month_cars_5_adj_MX5 = pd.DataFrame(columns=['Car','Item','Adj_Amount'])
    amount_by_month_cars_5_adj_MX5['Car'] = ['Mazda MX-5','Mazda MX-5','Mazda MX-5','Mazda MX-5','Mazda MX-5']
    amount_by_month_cars_5_adj_MX5['Sub-Category'] = ['Payments','Recovery','Tax','Insurance','Servicing and Fixes']
    amount_by_month_cars_5_adj_MX5['Adj_Amount'] = [16599.76,34.67,882.5,1449.78,1846.16]

    amount_by_month_cars_5_adj_Polo = pd.DataFrame(columns=['Car','Item','Adj_Amount'])
    amount_by_month_cars_5_adj_Polo['Car'] = ['VW Polo','VW Polo','VW Polo','VW Polo','VW Polo']
    amount_by_month_cars_5_adj_Polo['Sub-Category'] = ['Payments','Recovery','Tax','Insurance','Servicing and Fixes']
    amount_by_month_cars_5_adj_Polo['Adj_Amount'] = [10154.44,64.61,245.01,790.32,887.27]

    amount_by_month_cars_5_adj_cx5 = pd.DataFrame(columns=['Car','Item','Adj_Amount'])
    amount_by_month_cars_5_adj_cx5['Car'] = ['Mazda CX-5','Mazda CX-5','Mazda CX-5','Mazda CX-5','Mazda CX-5']
    amount_by_month_cars_5_adj_cx5['Sub-Category'] = ['Payments','Recovery','Tax','Insurance','Servicing and Fixes']
    amount_by_month_cars_5_adj_cx5['Adj_Amount'] = [29021.28,0,655,1163.78,664.02]
    amount_by_month_cars_6_adj = pd.concat([amount_by_month_cars_5_adj_cx5, amount_by_month_cars_5_adj_308, amount_by_month_cars_5_adj_A45, amount_by_month_cars_5_adj_MX5, amount_by_month_cars_5_adj_Polo], ignore_index=True)

    options_cars = ['Cars']
    df_selection_cars = df_selection[df_selection["Category"].isin(options_cars)]
    df_selection_cars['Car'] = ''
    df_selection_cars['Sub-Category'] = ''
    df_selection_cars.loc[df_selection_cars['Item'].str.contains('Peugeot')==True , 'Car'] = 'Peugeot 308'
    df_selection_cars.loc[df_selection_cars['Item'].str.contains('Mazda')==True , 'Car'] = 'Mazda CX-5'
    df_selection_cars.loc[df_selection_cars['Item'].str.contains('Payments')==True , 'Sub-Category'] = 'Payments'
    df_selection_cars.loc[df_selection_cars['Item'].str.contains('Recovery')==True , 'Sub-Category'] = 'Recovery'
    df_selection_cars.loc[df_selection_cars['Item'].str.contains('Tax')==True , 'Sub-Category'] = 'Tax'
    df_selection_cars.loc[df_selection_cars['Item'].str.contains('Insurance')==True , 'Sub-Category'] = 'Insurance'
    df_selection_cars.loc[df_selection_cars['Item'].str.contains('Servicing')==True , 'Sub-Category'] = 'Servicing and Fixes'
    amount_by_month_cars_10_adj = df_selection_cars[["Car","Amount"]]
    amount_by_month_cars_11_adj = (
        amount_by_month_cars_10_adj.groupby(by=["Car"],as_index=False).sum(["Amount"])
    )

    amount_by_month_cars_100_adj = df_selection_cars[["Car","Sub-Category","Amount"]]
    amount_by_month_cars_110_adj = (
        amount_by_month_cars_100_adj.groupby(by=["Car","Sub-Category"],as_index=False).sum(["Amount"])
    )
    amount_by_month_cars_60_adj = amount_by_month_cars_6_adj.merge(amount_by_month_cars_110_adj, on=['Car','Sub-Category'], how='left')
    amount_by_month_cars_60_adj['Total Amount'] = amount_by_month_cars_60_adj['Amount'].fillna(0) + amount_by_month_cars_60_adj['Adj_Amount'].fillna(0)
    amount_by_month_cars_61_adj = amount_by_month_cars_60_adj[["Car","Sub-Category","Total Amount"]]
    amount_by_month_cars_600_adj = pd.pivot_table(amount_by_month_cars_61_adj, values = 'Total Amount', index=['Sub-Category'], columns = 'Car').reset_index()
    amount_by_month_cars_600_adj["Mazda CX-5"] = amount_by_month_cars_600_adj["Mazda CX-5"].map('£{:,.2f}'.format)
    amount_by_month_cars_600_adj["Mazda MX-5"] = amount_by_month_cars_600_adj["Mazda MX-5"].map('£{:,.2f}'.format)
    amount_by_month_cars_600_adj["Peugeot 308"] = amount_by_month_cars_600_adj["Peugeot 308"].map('£{:,.2f}'.format)
    amount_by_month_cars_600_adj["Mercedes A45"] = amount_by_month_cars_600_adj["Mercedes A45"].map('£{:,.2f}'.format)
    amount_by_month_cars_600_adj["VW Polo"] = amount_by_month_cars_600_adj["VW Polo"].map('£{:,.2f}'.format)
        #print(amount_by_month_cars_600_adj)

    amount_by_month_cars_7_adj = (
        amount_by_month_cars_6_adj.groupby(by=["Car"],as_index=False).sum(["Adj_Amount"])
    )
    cars_1 = cars_1.merge(amount_by_month_cars_7_adj, on='Car', how='left')
    cars_2 = cars_1.merge(amount_by_month_cars_11_adj, on='Car', how='outer')
        #cars_2['Total Cost'] = cars_2['Adj_Amount']
    cars_2['Total Cost'] = cars_2['Adj_Amount'].fillna(0) + cars_2['Amount'].fillna(0)
        #print(cars_2)
    cars_2['Monthly Cost'] = cars_2['Total Cost']/cars_1['Purchase Months']
    cars_2['Monthly Cost (after Selling)'] = (cars_2['Total Cost']-cars_1['Estimated/Sold Value'])/cars_1['Purchase Months']
    cars_2['Total Cost'] = cars_2['Total Cost'].map('£{:,.2f}'.format)
    cars_2['Monthly Cost'] = cars_2['Monthly Cost'].map('£{:,.2f}'.format)
    cars_2['Estimated/Sold Value'] = cars_2['Estimated/Sold Value'].map('£{:,.2f}'.format)
    cars_2['Monthly Cost (after Selling)'] = cars_2['Monthly Cost (after Selling)'].map('£{:,.2f}'.format)

    exc_cars = ['']
    cars_3 = cars_2[~cars_2["Car"].isin(exc_cars)]

    exc_trans = ['99999999999999']
    df_selection_999 = df_selection[~df_selection["Transaction_ID"].isin(exc_trans)]

    # --- mainpage ---
    selected = option_menu(
        menu_title = None,
        options=["Overview","Add Data","Modify Data","Cars"],#,"Mortgage Calculator"],
        orientation = "horizontal"
    )

    if selected == "Overview":

        st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
        st.title(":moneybag: Cost Calculator")
        st.markdown("##")
        #st.text("text")

        left_column, right_column, mid_column, last = st.columns(4)
        with left_column:
            st.text("Guildford Flat Rent (since Oct 14):")
            st.subheader(f"{amount_by_month_grouped_flat_figure}")
        with right_column:
            st.text("Average Shared Spend per Month:")
            st.subheader(f"{Average_spend}")
        with mid_column:
            st.text("Average Mortgage Capital per Month:")
            st.subheader(f"{Average_Mortgage_Capital}")
        with last:
            st.text(Owage_Title)
            st.subheader(f"{Owage}")

        left_column, right_column, mid_column, last = st.columns(4)
        with left_column:
            st.text("Joint Salary:")
            st.subheader(f"£155,266.00")
        with right_column:
            st.text("Bathroom, Carpets & Sofas (0%):")
            st.subheader(f"£5,338.10")
        with mid_column:
            st.text("Dave's Credit Cards (0%):")
            st.subheader(f"£4,406.13")
        with last:
            st.text("Mortgage Remaining:")
            st.subheader(f"£555,433.93")
        #st.markdown("##")

        left_column, right_column, mid_column, last = st.columns(4)
        with left_column:
            st.text("Joint ISA Savings: ")
            st.subheader(f"£64,060.63")
        with right_column:
            st.text("Joint Other Savings: ")
            st.subheader(f"£1,600.00")
        with mid_column:
            st.text("Joint Pensions:")
            st.subheader(f"£174,287.90")
        with last:
            st.text("House Capital:")
            st.subheader(f"£544,566.07")

        st.markdown("---")

        #left_column, right_column = st.columns(2)
        #with left_column:
        #    st.plotly_chart(fig_line)
        #with right_column:
        #    st.plotly_chart(fig_pie)
        #with last:
        #    st.text("help")
            #st.plotly_chart(fig_line_totals)

        fig_line.update_layout(
            legend=dict(
                orientation="h",  # Horizontal orientation
                yanchor="top",
                y=-0.3,  # Positioning the legend below the chart
                xanchor="center",
                x=0.5
            )
        )

        fig_pie.update_layout(
            legend=dict(
                orientation="h",  # Horizontal orientation
                yanchor="top",
                y=-0.3,  # Positioning the legend below the chart
                xanchor="center",
                x=0.5
            )
        )

        #st.markdown(unsafe_allow_html=True)
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("---")

        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("---")

        # CSS to inject contained in a string
        hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        st.subheader("Spend Rate for the Month")
        st.text("With the current rate of spending in the Month, are we predicted to go over/under the Average Monthly Spend?")
        st.text(day_phrase)
        st.table(spend_rate_5)
        st.markdown("---")

        st.subheader("House Bills")
        st.text("Breakdown of House Bills for The Spinney since we moved in:")
        st.text(month_phrase)
        st.table(amount_by_month_bills_7)

        # CSS to inject contained in a string
        hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Last 25 Transactions")
        st.table(df_selection_999[['Transaction_ID','Date','Item','Amount Spent','Who','Category','Percentage Split (Dave)']].sort_values(by=['Date'], ascending=False).head(25))

    if selected == "Add Data":

        st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
        st.title(":moneybag: Cost Calculator")
        st.markdown("##")
        st.text("To add data please populate the following 5 options and click 'Submit'.")


        col_1, col_2, col_3, col_4, col_5 = st.columns(5)
        with col_1:
            fn_Who = st.selectbox("Who",["","Niki","Dave","Credit Card"], key = "Who")
        with col_2:
            fn_Category = st.selectbox("Category",["","Baby","Balancing Figure","Cars","Cats","Childcare","Dog","Drinks","Extension","Food","Fuel","Fun","Guildford Flat","House Bills","House Stuff","Mortgage Interest","Mortgage Capital","Other Bills"], key = "Category")
        with col_3:
            if fn_Category == "House Bills":
                fn_Item = st.selectbox("Item",["","Amazon Prime","BT Sport","Building & Contents Insurance","Cashback","Council Tax","Firelighters and Wood","Gas & Electricity","Internet","Netflix","Ring","Road Fund","Spotify","TV Licence","Water"], key = "Item")
            else:
                if fn_Category == "Cars":
                    fn_Item = st.selectbox("Item",["","Peugeot 308 - Insurance","Peugeot 308 - Payments","Peugeot 308 - Recovery","Peugeot 308 - Servicing and Fixes","Peugeot 308 - Tax","Mazda CX-5 - Insurance","Mazda CX-5 - Payments","Mazda CX-5 - Recovery","Mazda CX-5 - Servicing and Fixes","Mazda CX-5 - Tax"], key = "Item")
                else:
                    fn_Item = st.text_input("Item", key = "Item")
        with col_4:
            fn_Amount = st.text_input("Amount (£)", key = "Amount")
        with col_5:
            fn_Percentage_Split = st.number_input("Percentage Split (%) (Dave)", value = 50, key = "Percentage_Split")
        st.markdown("##")

        def clear_text():
            st.session_state["Amount"] = ""
            st.session_state["Item"] = ""
            st.session_state["Who"] = ""
            st.session_state["Category"] = ""

        #save data
        ref = db.reference('py/')
        #Transactions_ref = ref.child('Transactions')
        #Transactions_ref.set({
        #    transaction_ID:{
        #        'Item': Item_Col[0],
        #        'Amount': Amount_Col[0],
        #        'Who': Who_Col[0]
        #    }
        #})

        ts = datetime.now()
        transaction_ID = ts.strftime("%d%m%Y%H%M%S")

        def update_data():
            #update data
            ts = datetime.now()
            transaction_ID = ts.strftime("%d%m%Y%H%M%S")
            #transaction_ID = '14062022105706'
            hopper_ref = ref.child('Transactions')
            hopper_ref.update({
                transaction_ID:{
                    'Item': fn_Item,
                    'Amount': fn_Amount,
                    'Who': fn_Who,
                    'Category': fn_Category,
                    'Percentage_Split': fn_Percentage_Split,
                }
            })
            clear_text()

        a, b, c, d, e, f, g, h, col_4, col_5 = st.columns(10)
        with col_4:
            fn_submit = st.button("Submit", on_click = update_data)
        with col_5:
            fn_clear = st.button("Clear", on_click = clear_text)
        #st.markdown("##")
        st.markdown("---")

        #p

        #print(fn_Amount)
        #print(fn_Item)

        # CSS to inject contained in a string
        hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        st.subheader("Data Table")
        st.table(df_selection_999[['Transaction_ID','Date','Item','Amount Spent','Who','Category','Percentage Split (Dave)']].sort_values(by=['Date'], ascending=False))
        #st.markdown("##")

    if selected == "Modify Data":

        st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
        st.title(":moneybag: Cost Calculator")
        st.markdown("##")
        st.text("To modify existing data, make sure that the Transaction_ID matches exactly. Make the changes and click 'Submit'.")

        col_0, col_1, col_2, col_3, col_4, col_5 = st.columns(6)
        with col_0:
            fn_Transaction_ID = st.text_input("Transaction_ID", key = "Transaction_ID")
        with col_1:
            fn_Who = st.selectbox("Who",["","Niki","Dave","Credit Card"], key = "Who")
        with col_2:
            fn_Category = st.selectbox("Category",["","Baby","Balancing Figure","Cars","Cats","Childcare","Dog","Drinks","Extension","Food","Fuel","Fun","Guildford Flat","House Bills","House Stuff","Mortgage Interest","Mortgage Capital","Other Bills"], key = "Category")
        with col_3:
            if fn_Category == "House Bills":
                fn_Item = st.selectbox("Item",["","Amazon Prime","BT Sport","Building & Contents Insurance","Cashback","Council Tax","Firelighters and Wood","Gas & Electricity","Internet","Netflix","Ring","Road Fund","Spotify","TV Licence","Water"], key = "Item")
            else:
                if fn_Category == "Cars":
                    fn_Item = st.selectbox("Item",["","Peugeot 308 - Insurance","Peugeot 308 - Payments","Peugeot 308 - Recovery","Peugeot 308 - Servicing and Fixes","Peugeot 308 - Tax","Mazda CX-5 - Insurance","Mazda CX-5 - Payments","Mazda CX-5 - Recovery","Mazda CX-5 - Servicing and Fixes","Mazda CX-5 - Tax"], key = "Item")
                else:
                    fn_Item = st.text_input("Item", key = "Item")
        with col_4:
            fn_Amount = st.text_input("Amount (£)", key = "Amount")
        with col_5:
            fn_Percentage_Split = st.number_input("Percentage Split (%) (Dave)", value = 50, key = "Percentage_Split")
        st.markdown("##")

        def clear_text():
            st.session_state["Transaction_ID"] = ""
            st.session_state["Amount"] = ""
            st.session_state["Item"] = ""
            st.session_state["Who"] = ""
            st.session_state["Category"] = ""

        ref = db.reference('py/')
        def update_data():
            #update data
            transaction_ID = fn_Transaction_ID
            hopper_ref = ref.child('Transactions')
            hopper_ref.update({
                transaction_ID:{
                    'Item': fn_Item,
                    'Amount': fn_Amount,
                    'Who': fn_Who,
                    'Category': fn_Category,
                    'Percentage_Split': fn_Percentage_Split,
                }
            })
            clear_text()

        a, b, c, d, e, f, g, h, col_4, col_5 = st.columns(10)
        with col_4:
            fn_submit = st.button("Submit", on_click = update_data)
        with col_5:
            fn_clear = st.button("Clear", on_click = clear_text)
        #st.markdown("##")
        st.markdown("---")

        #print(fn_Amount)
        #print(fn_Item)

        # CSS to inject contained in a string
        hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        st.subheader("Data Table")
        st.table(df_selection_999[['Transaction_ID','Date','Item','Amount Spent','Who','Category','Percentage Split (Dave)']].sort_values(by=['Date'], ascending=False))
        #st.markdown("##")

    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden}
        footer {visibility: hidden}
        </style>
        """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    if selected == "Cars":

        # CSS to inject contained in a string
        hide_table_row_index = """
                    <style>
                    tbody th {display:none}
                    .blank {display:none}
                    </style>
                    """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
        st.title(":moneybag: Cost Calculator")
        st.markdown("##")
        st.text("Car Mileage and Estimated Value:")

        #save data
        ref = db.reference('py/')
        #Cars_ref = ref.child('Cars')
        #Car = 'Mercedes A45'
        #Cars_ref.set({
        #    Car:{
        #        'Mileage': 44276
        #    }
        #})

        def update_mileage():
           #update data
            Car = fn_Car
            #Car = 'Mazda MX-5'
            car_hopper_ref = ref.child('Cars')
            car_hopper_ref.update({
                Car:{
                    'Mileage': fn_Mileage
                    #'Mileage': 10000
                }
            })

        #st.markdown("##")
        st.table(cars_3[['Car','Registration','Years','Mileage','Annual Mileage (Us)','Annual Mileage (Total)','Total Cost','Monthly Cost','Estimated/Sold Value','Monthly Cost (after Selling)']])
        st.write("Link to Mazda CX-5 Prices: [link](https://www.autotrader.co.uk/car-search?postcode=gu273nt&radius=200&make=Mazda&model=CX-5&include-delivery-option=on&maximum-mileage=30000&transmission=Manual&fuel-type=Petrol&year-from=2018&year-to=2018&advertising-location=at_cars&page=1)")
        st.write("Link to Peugeot 308 Prices: [link](https://www.autotrader.co.uk/car-search?postcode=gu273nt&radius=200&make=Peugeot&model=308&include-delivery-option=on&maximum-mileage=70000&transmission=Manual&fuel-type=Diesel&year-from=2015&year-to=2015&advertising-location=at_cars&page=1)")
        st.markdown("---")
        st.text("Update Mileage:")

        col_0, col_1 = st.columns(2)
        with col_0:
            fn_Car = st.selectbox("Car",["Mazda CX-5","Peugeot 308","Mercedes A45","Mazda MX-5","VW Polo"], key = "Car")
        with col_1:
            fn_Mileage = st.text_input("Mileage", key = "Mileage")

        fn_submit = st.button("Submit", on_click = update_mileage)

        st.markdown("---")
        st.text("Car Costs:")
            #print(df_selection_cars)
            #st.text("...")
            #df_selection_cars = df_selection_cars[['Date','Car','Item','Amount Spent']].sort_values(by=['Date'], ascending=False)
        st.table(amount_by_month_cars_600_adj)

    # if selected == "Mortgage Calculator":
    #
    #     st.markdown(f"<div id='linkto_{0}'></div>", unsafe_allow_html=True)
    #     st.title(":moneybag: Cost Calculator")
    #     st.markdown("##")
    #
    #     #fixed_rate_mortgage(interest, years, payments_year, loan, start_date)
    #
    #     # CSS to inject contained in a string
    #     hide_table_row_index = """
    #                 <style>
    #                 tbody th {display:none}
    #                 .blank {display:none}
    #                 </style>
    #                 """
    #
    #     # Inject CSS with Markdown
    #     st.markdown(hide_table_row_index, unsafe_allow_html=True)
    #
    #     col_1, col_2, col_3, col_4, col_5 = st.columns(5)
    #     with col_1:
    #         fn_Loan = st.text_input("Amount Borrowed (£)", value = 574965, key = "Loan")
    #     with col_2:
    #         fn_Year = st.text_input("Term (Years)", value = 25, key = "Term")
    #     with col_3:
    #         fn_Rate = st.text_input("Interest Rate (%)", value = 1.19, key = "Rate")
    #     with col_4:
    #         fn_Start = st.text_input("Start Date", value = '2022-11-01', key = "Start")
    #     with col_5:
    #         fn_Over = st.text_input("Regular Overpayment (£)", value = 0, key = "Over")
    #     st.markdown("##")
    #
    #     interest_rate = float(fn_Rate)/100
    #     years = int(fn_Year)
    #     annual_payments = 12
    #     beg_balance = float(fn_Loan)
    #     RegularOverpayment = float(fn_Over)
    #     start = datetime.strptime(fn_Start, '%Y-%m-%d')
    #
    #     overpayments = pd.DataFrame(columns=['Date','Overpayment'])
    #     overpayments['Date'] = ['2022-05-01']
    #     overpayments['Date'] = overpayments['Date'].astype(str)
    #     #overpayments['Overpayment'] = [60000]
    #
    #     periods = years * annual_payments
    #     df_m = pd.DataFrame(index=range(1, periods+1))
    #     df_m["Date"] = pd.date_range(start, periods=periods, freq='MS', name='Payment Date').date
    #     df_m["Date"] = df_m["Date"].astype(str)
    #
    #     df_over = pd.DataFrame(index=range(1, periods+1))
    #     df_over.insert(0, 'Period', range(1, 1 + len(df_over)))
    #     df_over["Overpayment"] = 0
    #     #df_over.loc[20,['Overpayment']] = 60000
    #     #over_row = df_over["Overpayment"].loc[df_over['Period'] == 10]
    #     #print(df_over)
    #
    #     #save data
    #     #ref = db.reference('py/')
    #     #Period = 1
    #     #Overpayments_ref = ref.child('Overpayments')
    #     #Overpayments_ref.set({
    #     #    Period:{
    #     #        'Amount': 0
    #     #    }
    #     #})
    #
    #     def update_over():
    #         df_over.loc[fn_period,['Overpayment']] = int(fn_overpayment)
    #
    #     def clear_over():
    #         df_over["Overpayment"] = 0
    #
    #     first, left_column = st.columns(2)
    #     with first:
    #         fn_period =  st.selectbox("Period",df_over["Period"], key = "Period")
    #     with left_column:
    #         fn_overpayment = st.text_input("Overpayment (£)", value = 0, key = "Overpayment")
    #     #with next:
    #     #    fn_submitover = st.button("Add one-off Overpayment", on_click = "")
    #     #with final:
    #     #    fn_clearover = st.button("Clear all one-off Overpayments", on_click = "")
    #     st.markdown("##")
    #
    #     df_over.loc[fn_period,['Overpayment']] = int(fn_overpayment)
    #
    #     df_mc = df_m.merge(overpayments, on='Date', how='left')
    #
    #     df_mc["Overpayment"] = df_mc["Overpayment"].fillna(0)
    #     df_mc.insert(0, 'Period', range(1, 1 + len(df_mc)))
    #
    #     def amortize(principal, interest_rate, years, RegularOverpayment, annual_payments=12, start_date=date.today()):
    #
    #         pmt = -round(npf.pmt(interest_rate/annual_payments, years*annual_payments, principal), 2)
    #         # initialize the variables to keep track of the periods and running balances
    #         p = 1
    #         beg_balance = principal
    #         end_balance = principal
    #
    #         while end_balance > 10:
    #
    #             addl_principal = RegularOverpayment
    #
    #             # Recalculate the interest based on the current balance
    #             interest = round(((interest_rate/annual_payments) * beg_balance), 2)
    #             #print(interest)
    #
    #             # Determine payment based on whether or not this period will pay off the loan
    #             pmt = min(pmt, beg_balance + interest)
    #             principal = pmt - interest
    #             #print(principal)
    #
    #             lumpover = df_over.loc[p]['Overpayment']
    #
    #             #print(lumpover)
    #
    #             if lumpover > 0:
    #                 addl_principal = lumpover + RegularOverpayment
    #
    #             # Ensure additional payment gets adjusted if the loan is being paid off
    #             addl_principal = min(addl_principal, beg_balance - principal)
    #             end_balance = beg_balance - (principal + addl_principal)
    #             #print(end_balance)
    #
    #             yield OrderedDict([('Month',start_date),
    #                                ('Period', p),
    #                                ('Beginning Balance', beg_balance),
    #                                ('Payment', pmt),
    #                                ('Capital', principal),
    #                                ('Interest', interest),
    #                                ('Additional Capital', addl_principal),
    #                                ('End Balance', end_balance)])
    #
    #             # Increment the counter, balance and date
    #             p += 1
    #             start_date += relativedelta(months=1)
    #             beg_balance = end_balance
    #
    #     schedule = pd.DataFrame(amortize(beg_balance, interest_rate, years, RegularOverpayment, start_date=start))
    #     Total_Interest = schedule["Interest"].sum()
    #     Total_Payments = schedule["Period"].count()
    #     Total_Overpayments = schedule["Additional Capital"].sum()
    #
    #     def amortize_orig(principal, interest_rate, years, addl_principal=0, annual_payments=12, start_date=date.today()):
    #
    #         pmt = -round(npf.pmt(interest_rate/annual_payments, years*annual_payments, principal), 2)
    #         # initialize the variables to keep track of the periods and running balances
    #         p = 1
    #         beg_balance = principal
    #         end_balance = principal
    #
    #         while end_balance > 10:
    #
    #             addl_principal = 0
    #
    #             # Recalculate the interest based on the current balance
    #             interest = round(((interest_rate/annual_payments) * beg_balance), 2)
    #
    #             # Determine payment based on whether or not this period will pay off the loan
    #             pmt = min(pmt, beg_balance + interest)
    #             principal = pmt - interest
    #
    #             #if p == 10:
    #                 #addl_principal = 60000
    #
    #             # Ensure additional payment gets adjusted if the loan is being paid off
    #             addl_principal = min(addl_principal, beg_balance - principal)
    #             end_balance = beg_balance - (principal + addl_principal)
    #
    #             yield OrderedDict([('Month',start_date),
    #                                ('Period', p),
    #                                ('Beginning Balance', beg_balance),
    #                                ('Payment', pmt),
    #                                ('Capital', principal),
    #                                ('Interest', interest),
    #                                ('Additional Capital', addl_principal),
    #                                ('End Balance', end_balance)])
    #
    #             # Increment the counter, balance and date
    #             p += 1
    #             start_date += relativedelta(months=1)
    #             beg_balance = end_balance
    #
    #     schedule_orig = pd.DataFrame(amortize_orig(beg_balance, interest_rate, years, addl_principal=0, start_date=start))
    #     Total_Original_Interest = schedule_orig["Interest"].sum()
    #     Total_Original_Payments = schedule_orig["Period"].count()
    #
    #     scheduleComparison = schedule_orig.merge(schedule, on='Period', how='left')
    #
    #     scheduleComparison_2 = scheduleComparison[['Period','End Balance_x','End Balance_y']]
    #     scheduleComparison_2['End Balance_y'] = scheduleComparison_2['End Balance_y'].fillna(0)
    #     scheduleComparison_2['Original Balance (no overpayments)'] = scheduleComparison_2['End Balance_x']
    #     scheduleComparison_2['Adjusted Balance (with overpayments)'] = scheduleComparison_2['End Balance_y']
    #     #print(scheduleComparison_2)
    #
    #     scheduleComparison_3 = scheduleComparison[['Period','Interest_x','Interest_y']]
    #     scheduleComparison_3['Interest_y'] = scheduleComparison_3['Interest_y'].fillna(0)
    #     scheduleComparison_3['Original Interest'] = scheduleComparison_3['Interest_x']
    #     scheduleComparison_3['Adjusted Interest'] = scheduleComparison_3['Interest_y']
    #     #print(scheduleComparison_3)
    #
    #     schedule_line = px.line(
    #         data_frame = scheduleComparison_2,
    #         x = "Period",
    #         y = ["Original Balance (no overpayments)","Adjusted Balance (with overpayments)"],
    #         labels={
    #                      "Period": "Period",
    #                      "value": "Balance (£)"
    #                  },
    #         #color = "variables",
    #         color_discrete_map={
    #                 "Adjusted Balance (with overpayments)'": "green",
    #                 "Original Balance (no overpayments)": "blue"
    #                 },
    #         title = "Balance over Time",
    #     )
    #     schedule_line.update_xaxes(
    #         #dtick="M1",
    #         nticks=20
    #         #tickformat="%b\n%Y"
    #     )
    #     schedule_line.update_layout(
    #         plot_bgcolor="rgba(0,0,0,0)",
    #         xaxis=(dict(showgrid=False)),
    #         yaxis=(dict(showgrid=False)),
    #         legend_title="",
    #     )
    #
    #     interestsaved_pie = pd.DataFrame(columns=['Category','Interest'])
    #     interestsaved_pie['Category'] = ['Interest Saved','Interest Paid']
    #     interestsaved_pie['Interest'] = [(Total_Original_Interest - Total_Interest), Total_Interest]
    #     #print(interestsaved_pie)
    #
    #     fig_pie_2 = px.pie(
    #         data_frame = interestsaved_pie,
    #         labels = "Category",
    #         values = "Interest",
    #         names = "Category",
    #         color = "Category",
    #         color_discrete_map={
    #                 "Interest Saved'": "green",
    #                 "Interest Paid": "blue"
    #                 },
    #         title = "Interest Saved",
    #         )
    #
    #     schedule["Beginning Balance"] = schedule["Beginning Balance"].map('£{:,.2f}'.format)
    #     schedule["Payment"] = schedule["Payment"].map('£{:,.2f}'.format)
    #     schedule["Capital"] = schedule["Capital"].map('£{:,.2f}'.format)
    #     schedule["Interest"] = schedule["Interest"].map('£{:,.2f}'.format)
    #     schedule["Additional Capital"] = schedule["Additional Capital"].map('£{:,.2f}'.format)
    #     schedule["End Balance"] = schedule["End Balance"].map('£{:,.2f}'.format)
    #
    #     df_mc["Overpayment"] = df_mc["Overpayment"].map('£{:,.2f}'.format)
    #
    #     first, left_column, right_column, mid_column, last = st.columns(5)
    #     with first:
    #         st.text("Overpayments:")
    #         st.subheader(f"£{Total_Overpayments:,.2f}")
    #     with left_column:
    #         st.text("Total Interest:")
    #         st.subheader(f"£{Total_Interest:,.2f}")
    #     with right_column:
    #         st.text("Interest saved:")
    #         st.subheader(f"£{Total_Original_Interest - Total_Interest:,.2f}")
    #     with last:
    #         st.text("Years saved:")
    #         st.subheader(f"{(Total_Original_Payments - Total_Payments)/12:,.1f}")
    #     with mid_column:
    #         st.text("Total Years:")
    #         st.subheader(f"{Total_Payments/12:,.1f}")
    #
    #     first, left_column = st.columns(2)
    #     with first:
    #         st.plotly_chart(schedule_line)
    #     with left_column:
    #         st.plotly_chart(fig_pie_2)
    #
    #     st.table(schedule)
