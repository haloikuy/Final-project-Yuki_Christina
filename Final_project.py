#import
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from plotly import express as px
import seaborn as sns

#deal with the data
df = pd.read_csv('hotel_bookings.csv')

#处理缺失的数据
df.isnull().sum().sort_values(ascending=False)

#处理异常的数据（通过ipynb ，可以看出哪些数据需要被处理）
df.loc[df['lead_time']                      > 380, ['lead_time']                   ] = 380
df.loc[df['stays_in_weekend_nights']        > 6, ['stays_in_weekend_nights']       ] = 6
df.loc[df['stays_in_week_nights']           > 10, ['stays_in_week_nights']         ] = 10
df.loc[df['adults']                         > 4, ['adults']                        ] = 4
df.loc[df['children']                       > 8, ['lead_time']                     ] = 0
df.loc[df['babies']                         > 8, ['babies']                        ] = 0
df.loc[df['booking_changes']                > 5, ['booking_changes']               ] = 5
df.loc[df['days_in_waiting_list']           > 0, ['days_in_waiting_list']          ] = 1
df.loc[df['previous_cancellations']         > 0, ['previous_cancellations']        ] = 1
df.loc[df['previous_bookings_not_canceled'] > 0, ['previous_bookings_not_canceled']] = 1

#清除掉重复的数据
df.duplicated().sum()
df.drop_duplicates(inplace = True)
#从11万-8万，有3万条重复的数据被删除


#set a cover
st.markdown('![cover](https://user-images.githubusercontent.com/115609320/199061924-6b9d1b96-7786-4c21-9ef8-b71fda327e27.jpg)')
st.title('Final project by YucenXie & BeiChen')

st.header('Introduction of Hotel_Dataset ')
df


st.header('Basic Overview about the dataset')
#展示一些基础数据的图片
st.markdown('![basic information](https://user-images.githubusercontent.com/115609320/199069746-aaa7f650-cca3-464a-9860-4ba039ce0d68.jpg)')







st.header('Some filters & Visualization')
#交互工具1
# create a price filter
adr_filter = st.slider('adr', 62.0, 157.71, 65.0)  # min, max, default
# filter by price
df = df[df.adr >= adr_filter]

#交互工具2
# create a multi select marker-segment
market_segment_filter = st.sidebar.multiselect(
     'Chose the Market Segment type',
     df.market_segment.unique(),  # options
     df.market_segment.unique())  # defaults
# filter by market segment
df = df[df.market_segment.isin(market_segment_filter)]

#交互工具3
# create a income level
df['babies_and_children'] = df['babies'] + df['children']
children_and_babies_filter = st.sidebar.radio(
    "Chose the customers have children or not",
    ('Only adults', 'Adults with babies and children'))
if children_and_babies_filter == 'Only adults':
    df = df[df.babies_and_children == 0]
elif children_and_babies_filter == 'Babies and Children':
    df = df[df.babies_and_children >0]


st.subheader('Cancelation')

#取消率与年份之间的关系
st.write('Cancellation rate about year and month')
df_cancel_year=pd.crosstab(df.arrival_date_year,df.is_canceled,margins=True)
df_cancel_year['cancel-percent']=df_cancel_year[1]*100/df_cancel_year['All']
df_cancel_year.drop('All',inplace=True)


#取消率与月份之间的关系

df_cancel_month=pd.crosstab(df.arrival_date_month,df.is_canceled,margins=True)
df_cancel_month['cancel-percent']=df_cancel_month[1]*100/df_cancel_month['All']
df_cancel_month.drop('All',inplace=True)


#进行排版
fig, ax = plt.subplots(1, 2,figsize=(15, 5))

df_cancel_year['cancel-percent'].plot.bar(ax=ax[0],color='#C9BFCB')
#ax[0].xticks(rotation=0)
ax[0].set_xlabel('Year')
ax[0].set_ylabel('cancellation')
#ax[0].title('Cancellation rates across 2015-2017')

df_cancel_month['cancel-percent'].plot.bar(ax=ax[1],color='#A58E9E')
#ax[1].xticks(rotation=0)
ax[1].set_xlabel('Month')
ax[1].set_ylabel('cancellation')
#ax[1].title('Cancellation rates across month')
st.pyplot(fig)


#create a bar to show the canlellation rate about the lead time
df_cancel_leadtime = pd.crosstab(df.lead_time,df.is_canceled,margins=True)
df_cancel_leadtime['cancel-percent']=df_cancel_leadtime[1]*100/df_cancel_leadtime['All']
df_cancel_leadtime.drop('All',axis=1,inplace=True)
df_cancel_leadtime.drop('All',axis=0,inplace=True)

st.write('Cancellation rate about the lead time')
fig, ax =plt.subplots(figsize=(15,5))
df_cancel_leadtime['cancel-percent'].plot(color='#BAB5D6')
st.pyplot(fig)



#是否交押金和取消人数的关系
st.write('Cancellation rate about the deposite')
df['is_canceled']=df['is_canceled'].astype('str')
canceled_bookings = df[df['is_canceled'] == '1']

fig, ax = plt.subplots(figsize = (15, 5))

sns.countplot(ax = ax, y = 'deposit_type', data = canceled_bookings, orient = "h" ,palette = 'BuPu').set(ylabel = None)
ax.bar_label(ax.containers[0], padding = 4)
plt.title('Deposit type of cancelled bookings')

st.pyplot(fig)

#客户类型和取消人数的关系

st.write('Cancellation rate about the customer type')
fig, ax =plt.subplots(figsize=(20, 10))

df1=df[df['customer_type']=='Transient']
df1_cancel = pd.crosstab(df1.arrival_date_month,df1.is_canceled,margins=True)
df1_cancel['cancel_percent']=df1_cancel['1']*100/df1_cancel['All']
df1_cancel.drop('All',axis=1,inplace=True)
df1_cancel.drop('All',axis=0,inplace=True)
df1_cancel=df1_cancel.reindex(['January','February','March','April','May','June','July','August','September',
'October','November','December'])
df1_cancel=df1_cancel.reset_index()


sns.lineplot(
    x='arrival_date_month',
    y='cancel_percent',
    data=df1_cancel,
    ci =None, 
    palette = 'viridis', 
    alpha = 0.6,
    label='Transient',
    lw=5,
    
)

df2=df[df['customer_type']=='Contract']
df2_cancel = pd.crosstab(df2.arrival_date_month,df2.is_canceled,margins=True)
df2_cancel['cancel_percent']=df2_cancel['1']*100/df2_cancel['All']
df2_cancel.drop('All',axis=1,inplace=True)
df2_cancel.drop('All',axis=0,inplace=True)
df2_cancel=df2_cancel.reindex(['January','February','March','April','May','June','July','August','September',
'October','November','December'])
df2_cancel=df2_cancel.reset_index()
sns.lineplot(
    x='arrival_date_month',
    y='cancel_percent',
    data=df2_cancel,
    ci =None, 
    palette = 'viridis', 
    alpha = 0.6,
    label='Contract',
    lw=5,
    
)

df3=df[df['customer_type']=='Transient-Party']
df3_cancel = pd.crosstab(df3.arrival_date_month,df3.is_canceled,margins=True)
df3_cancel['cancel_percent']=df3_cancel['1']*100/df3_cancel['All']
df3_cancel.drop('All',axis=1,inplace=True)
df3_cancel.drop('All',axis=0,inplace=True)
df3_cancel=df3_cancel.reindex(['January','February','March','April','May','June','July','August','September',
'October','November','December'])
df3_cancel=df3_cancel.reset_index()
sns.lineplot(
    x='arrival_date_month',
    y='cancel_percent',
    data=df3_cancel,
    ci =None, 
    palette = 'viridis', 
    alpha = 0.6,
    label='Transient-Party',
    lw=5
    
)

df4=df[df['customer_type']=='Group']
df4_cancel = pd.crosstab(df4.arrival_date_month,df4.is_canceled,margins=True)
df4_cancel['cancel_percent']=df4_cancel['1']*100/df4_cancel['All']
df4_cancel.drop('All',axis=1,inplace=True)
df4_cancel.drop('All',axis=0,inplace=True)
df4_cancel=df4_cancel.reindex(['January','February','March','April','May','June','July','August','September',
'October','November','December'])
df4_cancel=df4_cancel.reset_index()
sns.lineplot(
    x='arrival_date_month',
    y='cancel_percent',
    data=df4_cancel,
    ci =None, 
    palette = 'viridis', 
    alpha = 0.6,
    label='Group',
    lw=5
    
)
plt.title('Cutomer type of cancelled bookings')
st.pyplot(fig)

#取消率与车位的关系
st.write('Cancellation rate about the car parking and meal')
tbl2=pd.crosstab(df.required_car_parking_spaces,df.is_canceled,margins=True)
tbl2['cancel-percent']=tbl2['1']*100/tbl2['All']
tbl2.drop('All',inplace=True)

fig, ax = plt.subplots(1,2,figsize=(15, 7))
tbl2['cancel-percent'].plot.bar(color='#e4bfcb',ax=ax[0])
plt.xticks(rotation=0)
plt.xlabel('required_car_parking_spaces')
plt.ylabel('Cancellation %')
plt.title('Cancellation rates about car parking')
plt.show()


#取消率与包餐的关系
tbl3=pd.crosstab(df.meal,df.is_canceled,margins=True)
tbl3['cancel-percent']=tbl3['1']*100/tbl3['All']
tbl3.drop('All',inplace=True)


tbl3['cancel-percent'].plot.bar(color='#eec5cc',ax=ax[1])
plt.xticks(rotation=0)
plt.xlabel('meal')
plt.ylabel('Cancellation %')
plt.title('Cancellation rates about meal')
plt.show()
st.pyplot(fig)


#房价的关系
st.subheader('Average room price（adr)')

#房价与月份的关系
st.write('ADR about the month')
fig, ax =plt.subplots(figsize=(15, 7))
confirmed_bookings = df[df['is_canceled']=='0']
sns.lineplot(x = 'arrival_date_month', 
            y = 'adr', 
            hue = 'hotel', 
            data = confirmed_bookings, 
            ci =None, 
            palette = 'viridis', 
            alpha = 0.6,
            lw=5)
plt.title('Monthly ADR')
plt.xlabel('Months')


plt.tight_layout()
st.pyplot(fig)










