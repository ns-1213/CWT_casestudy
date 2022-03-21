'''
python script written by Nicholas Smedley on 20/03/2022

'''

import pandas as pd
import numpy as np


data = pd.read_csv('bookings.csv',names=['bookingID','travellerID','companyID','booking_date','departure_date','origin','destination','price','status'])
data['booking_date'] = pd.to_datetime(data['booking_date'])
data['departure_date'] = pd.to_datetime(data['departure_date'])

def booking_error(data):
    '''
    removes any bookings that have a booking date set before the departure date

    :param data:
    :return:
        -data frame
        -sends data to csv
        -prints number of rows in data frame
    '''
    data.drop(data[(data.booking_date > data.departure_date) & (data.status != 'BOOKED')].index,inplace=True)
    return data,data.to_csv('q1.csv'),print('bookings without errors =',len(data))

def trip_calc(data):
    '''
    groups each trip together and returns a data frame containing data of each trip
    :param data:
    :return:
        -the trip data frame
        -the top 10 companies by spending are returned as a csv
        - prints the total number of trips
    '''
    booked_data = booking_error(data)[0]
    booked_data['price'] = np.where(booked_data['status'] == 'CANCELLED',booked_data['price']*-1,booked_data['price'])
    booked_data.rename(columns={'bookingID': 'tripID'}, inplace=True)
    clean_data = booked_data.groupby('tripID').agg({'travellerID':'max','companyID':'max','booking_date': 'max','departure_date':'max','origin':'max','destination':'max','price':'sum'})
    top_10 = clean_data.groupby('companyID').agg({'price':'sum'}).sort_values('price',ascending=False).head(10)
    return clean_data,top_10.to_csv('q2.csv'), print('number of trips =',len(clean_data))
def route_calc(data):
    '''
    returns a dataframe containing the total cost each company paid for each route and sends the top 10 to csv
    :param data:
    :return:
        -route cost dataframe
        -top 10 routes sent to csv
    '''
    clean_data = trip_calc(data)[0]
    sum_route = clean_data.groupby(['companyID','origin','destination']).agg({'price':'sum'}).reset_index()
    top_10 = sum_route.sort_values('price',ascending=False).head(10)
    return sum_route,top_10.to_csv('q3.csv',index=False)
def exchange_calc(data):
    '''
    calculates the percentage contribution of exchanges to trip prices for each traveller and then gives the top 2 for each company proveded it is above 8%.
    :param data:
    :return:
        -dataframe of top 2 travellers for each company
        -top 2 provided precentage is above 8 to csv
        -number of rows that use more than 8 percent and are part of top 2
    '''
    booked_data = booking_error(data)[0]
    grouped_data = booked_data.groupby(['companyID','travellerID']).apply(lambda x: x[x['status'] == 'EXCHANGED']['price'].sum()/x[x['status'] != 'CANCELLED']['price'].sum()).reset_index()
    grouped_data.columns = ['companyID','travellerID','percent_exchanged']
    # grouped_data = booked_data.merge(grouped_data_status,on = ['companyID','travellerID'])
    clean_data = grouped_data.sort_values(by=['companyID','percent_exchanged'],ascending=False)
    clean_data = clean_data.groupby('companyID').head(2)
    clean_data_8percent= clean_data.drop(clean_data[clean_data.percent_exchanged < 0.08].index)
    return clean_data,clean_data_8percent.to_csv('q4.csv',index = False),print('people above 8% exchange cost =',len(clean_data_8percent))



route_calc(data)
exchange_calc(data)