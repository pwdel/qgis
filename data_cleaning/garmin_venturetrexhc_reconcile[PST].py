import gpxpy
import gpxpy.gpx
import pandas as pd
# timezones
import pytz

gpx_file = open('work/OlympicNationalPark2021[COPY].gpx', 'r')

gpx = gpxpy.parse(gpx_file)

# initiate constructors
lat_list=[]
long_list=[]
elv_list=[]
time_list=[]

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # format time to be a regular string
            timepoint_formatted = '{0}'.format(point.time)
            # create lists to add to constructor later
            lat_list.append(point.latitude)
            long_list.append(point.longitude)
            elv_list.append(point.elevation)
            time_list.append(timepoint_formatted)

# create constructor dictionary of column labeled lists to add to dataframe
dictconstructor = {'lat': lat_list, 'long': long_list, 'elv': elv_list, 'time': time_list}

# dataframe constructor method
df_allgpxentries = pd.DataFrame(dictconstructor)

# delete lists
del lat_list
del long_list
del elv_list
# don't delete time_list because we need it
# del time_list

first_entry = df_allgpxentries.time[0]
print('first time entry is: ',first_entry)

pd_first_timestamp = pd.to_datetime(first_entry, format='%Y-%m-%d %H:%M:%S', errors='ignore')

print('the first timestamp entry is: ',pd_first_timestamp)
print('the datatype of the first timestamp entry is now: ',type(pd_first_timestamp))

# enter the first corrected timestamp
corrected_timestamp = '2021-05-14 15:45:00+0000'
print('the datatype of corrected_timestamp is: ',type(corrected_timestamp))

# get the time difference between the in a new dataframe
df_diff = pd.DataFrame(columns=['to','fr','ans'])
df_diff.to = [pd_first_timestamp]
df_diff.fr = [pd.Timestamp(corrected_timestamp)]
# index timedelta_float64 at 0 to extract numpy.float64 value
timedelta_float64 = (df_diff.fr-df_diff.to).astype('timedelta64[s]')[0]

print('the timedelta in float64 seconds is: ',timedelta_float64)

# check if timedelta and timedelta_pd equal

timedelta_pd = pd.Timedelta(seconds=timedelta_float64)
timedelta = (df_diff.fr-df_diff.to)[0]

print(timedelta)

if timedelta_pd == timedelta:
    print('equal')
    print(type(timedelta_pd))

# add timedelta_pd to first entry

print('pd_first_timestamp type: ',type(pd_first_timestamp))

print('timedelta_pd+pd_first_timestamp: ',timedelta_pd + pd_first_timestamp)

# add new column of timestamps converted from string to  to df_allgpxentries

# create list of converted timestamps
df_allgpxentries['timestamps'] = pd.to_datetime(df_allgpxentries.time, format='%Y-%m-%d %H:%M:%S', errors='ignore')

# update entries with calculated time delta
df_allgpxentries['updatedtimestamps'] = timedelta_pd + df_allgpxentries['timestamps']

#---- Timezone Stuff ----

# Check Data type
print("df_allgpxentries['updatedtimestamps'] type is",type(df_allgpxentries['updatedtimestamps']))
print("df_allgpxentries['updatedtimestamps'][0] type  is",type(df_allgpxentries['updatedtimestamps'][0]))
print("df_allgpxentries['updatedtimestamps'][0] value is",df_allgpxentries['updatedtimestamps'][0])

# apply lambda function on entire column
# only apply to df_allgpxentries['updatedtimestamps'] column
# .astimezone method on timestamp(s), convert from already time aware UTC to America/Lima
df_allgpxentries['updatedtimestamps'] = df_allgpxentries['updatedtimestamps'].apply(lambda x: x.astimezone(tz='America/Los_Angeles'))

# shift time timezone from UTC
# enter timezone as int
# number of hours to add to get back to UTC, opposite of timezone conversion
timezone_delta = int(7)
print(timezone_delta)
# convert to timestamp format
timezonedelta_df = pd.Timedelta(hours=timezone_delta)

df_allgpxentries['updatedtimestamps'] = df_allgpxentries['updatedtimestamps']+timezonedelta_df


print(df_allgpxentries.head)

# creating output gpx track
gpx = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points from dataframe:
for idx in df_allgpxentries.index:
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(df_allgpxentries.lat[idx], df_allgpxentries.long[idx],df_allgpxentries.elv[idx],df_allgpxentries.updatedtimestamps[idx]))

# print(gpx.to_xml())

with open('output.gpx', 'w') as f:
    f.write(gpx.to_xml())
