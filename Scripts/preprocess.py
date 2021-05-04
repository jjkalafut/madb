'''
Preprocess a netflow csv into MIDAS-R a ready format
'''

import pandas as pd
import os
import datetime as dt
import sys

input_file_name = sys.argv[ 1 ]
output_file_name = input_file_name + ".processed"
truth_file_name = input_file_name + ".truth"
ip_map_file_name = input_file_name + ".ipmap"
time_file_name = input_file_name + ".timemap"
shape_file_name = input_file_name + ".shape"

initial_datetime = None
ip_map = {}
on_ip = 0

time_divisor = 1 #CHANGE TO ADJUST TIME STEPS. LOWER = MORE STEPS. 60 = 1min steps, 120 = 2min steps

def ipToNumber( ip ):
    global on_ip
    global ip_map
    if ip not in ip_map:
        ip_map[ ip ] = on_ip
        on_ip += 1
        return ( on_ip - 1 )
    else:
        return ip_map[ ip ]

def timedeltaToSeconds( td ):
    return ( td.days * 86400 ) + td.seconds

def dateStringToInt( ds ):
    global initial_datetime
    global time_divisor
    time_delta = dt.datetime.strptime( ds,'%Y-%m-%d %H:%M:%S') - initial_datetime
    return ( 1 + ( timedeltaToSeconds( time_delta ) // time_divisor ) )

#0 is normal data, 1 is bad data
def flagData( type ):
    if( type == 'background'):
        return 0
    else:
        return 1

#Read csv file as a DataFrame
df = pd.read_csv( input_file_name,
    names=["Date","Duration","Source IP","Dest IP","Source Port","Target Port","Protocol","Col 6","Col 7","Col 8","Col 9","Col 10","Target"],
    usecols=["Date","Source IP", "Dest IP", "Target" ] )

print("loaded data")

with open( shape_file_name, 'w' ) as shape_out:
    shape_out.write( str(df.shape[0]) )

# Change the Target column values such that: 'background' -> 0; 'blacklist' -> 1
print("Bad types:" + str(df.Target.unique()))
df[ "Target" ] = df[ "Target" ].map( lambda t: flagData( t ) )

df.to_csv( truth_file_name, index=False, columns=["Target"], header=False) #Write DateFrame back as a csv file
df.drop(columns=['Target'])
print("wrote truth col")

#map ips to integers
df[ "Source IP" ] = df[ "Source IP" ].map( lambda ip: ipToNumber( ip ) )
df[ "Dest IP" ] = df[ "Dest IP" ].map( lambda ip: ipToNumber( ip ) )
#output data keys
with open( ip_map_file_name, 'w' ) as ip_out:
    for key, value in ip_map.items():
        ip_out.write( key + "," + str( value ) + "\n")
ip_map = {}
print("set ips")

#time to dela T step integer
# ex time 2016-07-27 13:43:21
initial_datetime = dt.datetime.strptime( df['Date'].iloc[0],'%Y-%m-%d %H:%M:%S')
last_datetime = dt.datetime.strptime( df['Date'].iloc[-1],'%Y-%m-%d %H:%M:%S')
df[ "Date" ] = df[ "Date" ].map( lambda ds: dateStringToInt( ds ) )


print("set datetime")

#output preprocess data
df.to_csv( output_file_name, index=False, columns=["Source IP","Dest IP","Date"], header=False) #Write DateFrame back as a csv file

df = None

num_time_inc = timedeltaToSeconds( last_datetime - initial_datetime ) // time_divisor
with open( time_file_name, 'w' ) as time_out:
    for x in range( 1, num_time_inc + 2 ):
        time_out.write( str( x ) + "," + ( initial_datetime + dt.timedelta(seconds=( time_divisor * x ) ) ).isoformat() + "\n")
