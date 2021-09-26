## Background on Bug

https://support.garmin.com/en-US/?faq=qpVUfZBKI28PqnPd6HuXa6

> Garmin has identified an issue with GPS firmware that causes the time and date to be wrong. A software update is available that resolves this concern. Due to the age of the devices and the complexity of updating, it is not recommended to update unless you specifically need accurate date and time.

## What Do We Want to Accomplish?

* Syncing the time up properly so that our trek shows the appropriate date and time.
* Be able to upload the correct date and time to an application like Strava for further analysis.
* Output needs to be GPX.

## GPX File Format

Basically, it looks like the following:

'''
<trk>
  <name>ACTIVE LOG</name>
  <extensions>
    <gpxx:TrackExtension>
      <gpxx:DisplayColor>Black</gpxx:DisplayColor>
    </gpxx:TrackExtension>
  </extensions>
  <trkseg>
    <trkpt lat="-9.494030512869358" lon="-77.410549074411392">
      <ele>3845.41064453125</ele>
      <time>2002-01-24T12:08:58Z</time>
    </trkpt>

...

'''

## Python GPX Library

https://stackoverflow.com/questions/11105663/how-to-extract-gpx-data-with-python

## Running Jupyter Notebook with Docker

[reference guide](https://towardsdatascience.com/how-to-run-jupyter-notebook-on-docker-7c9748ed209f#9927)

### Running Jupyter Notebook Stack on Docker Locally

To Run Docker as a non-specific build.

```
docker run -p 8888:8888 jupyter/minimal-notebook
```
### Building a Docker File with Jupyter and Installing Data Science Tools

* Use the Dockerfile that is set up within data_cleaning
* Note, this includes some data science tools, as well as, "gpxpy" which is a gpx analysis tool.
* Build the Dockerfile within the directory:

```
docker build -t jupyter/custom-notebook .
```
Then run the image. You can look at the image using, "docker images" - once you have the name, then you can run it. Note, the "-t" option within the command above tags the image with a name, "jupyter/custom-notebook"

```
docker run -p 8888:8888 jupyter/custom-notebook
```

From there you can go in and run your jupyter notebook regularly.

### gpxpy Documentation

https://github.com/tkrajina/gpxpy

The most basic code demonstration using gpxpy is the following (there are many more utilities included)

```
import gpxpy
import gpxpy.gpx

gpx_file = open('Quilcayhuanca-Cojup_2021[COPY].gpx', 'r')

gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))

for waypoint in gpx.waypoints:
    print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))

for route in gpx.routes:
    print('Route:')
    for point in route.points:
        print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))

# There are many more utility methods and functions:
```

### Including GPX File in Docker Container

One way to do this is to specify the location of the local folder you want to give access to on the Docker Container.

This is what is described by Docker as a, "[bind mount](https://docs.docker.com/storage/bind-mounts/)." However, on MacOS and Windows only certain filesystems are allowed, so this is not recommended.

Another way to do this is to simply use COPY.  COPY is an updated version of ADD, which is still in the Docker suite of tools due to compatibility issues.

#### Using COPY to Add Folder Directly Into Jupyter Notebook

The default Jupyter notebook directory is /work. We have to find where this is on the Docker container by logging into the Docker shell.

```
docker exec -it zen_lederberg /bin/bash
```
zen_lederberg was the assigned name of the Docker container at the time of authoring this document.  

If we wanted to give this a custom name, we can do this during running the container with:

```
docker run --name datanotebook -p 8888:8888 jupyter/custom-notebook
```

If we want to rename an app in operation, we can do the following:

```
docker rename zen_lederberg datanotebook
```

So right away, upon logging into the docker container shell, we see that, "work" seems to be the default directory.

```
(base) jovyan@0fb1600defb4:~$ ls
work
```
Within that work directory is a ipynb file we created as well as a gpx file we created dynamically while the container was running

```
(base) jovyan@0fb1600defb4:~/work$ ls
'GPX Test.ipynb'   test.gpx
```
However our objective is really to include a data folder full of experimental data and files, let's call it, "datainclude" within that jupyter notebook, "work" directory. We can use the following format for, COPY:

```
COPY /source/file/path  /destination/path
```
Hence in our build file, we use:

```
COPY /datainclude /work/datainclude
```
We can build our container once again and run with a custom name:

```
docker build -t jupyter/custom-notebook .
docker run --name datanotebook -p 8888:8888 jupyter/custom-notebook
```
So now when you look at the jupyter data notebook...ta-da! The data folder you had specified should be in there...except it's not! What happened?

When we ran the COPY command, we assumed that, the destination path, "work" was the end-all-be all path as shown when we immediately log into docker using the bin/bash functionality, when in reality, where docker logs us into by deafault is a user folder. So where was the work file that we created located?

Basically it's right directly under "/" the main directory, rather than the user directory for work. So the / directory is where all of this stuff is kept:

```
(base) jovyan@ecd4d9f761ea:/$ ls
bin  boot  dev  etc  home  lib  lib32  lib64  libx32  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var  work
```
To find our real destination directory, we can run the command, "pwd" within the immediate home directory when we log in under the shell within docker in the first place:

```
(base) jovyan@ecd4d9f761ea:~/work$ pwd
/home/jovyan/work
```
But how do we know our user will always be, "jovyan"?

This user comes from the [jupyter documentation](https://jupyter.readthedocs.io/en/latest/community/content-community.html#what-is-a-jovyan), it was a user set up, specific to Jupyter, which has sudo commands.

Hypothetically when building the document we could simply replace, 'jovyan' in the file structure with the USER designator:

USER $NB_UID

Let's see if that works...

```
COPY /datainclude /home/$NB_UID/work
```
Then running docker...

```
docker build -t jupyter/custom-notebook .
docker run --name datanotebook -p 8888:8888 jupyter/custom-notebook
```
Nope!  We don't see the folder copied into the appropriate location. Where did it go this time?

```
docker exec -it datanotebook /bin/bash

...

jovyan@139f107ec71c:/home/1000/work$

```
So basically the build file took the user number rather than the user name and created a directory.

```
COPY /datainclude /home/jovyan/work
```


#### Saving a Jupyterfile Created in the Docker Container to Local

This would be achieved using bind mounts.

https://stackoverflow.com/questions/31448821/how-to-write-data-to-host-file-system-from-docker-container

However, what are we really trying to achieve here? We may be interested in saving our Jupyter notebook for a following session.

There are different use cases here:

1. Perhaps we may need to just save the Jupyter notebook work in general, because we're busy.
2. Perhaps we want to have the Docker container start up with some kind of default Jupyter notebook, with a pre-written list of imports and code to get us going, something that we use on a repetitive basis.


## Fixing Time Record

The Garmin Venture HC has an error which makes the time record off by almost 20 years. We can fix this by shifting the time recorded throughout the trek.

### By How Much Time Is the Record Off?

* Our start time on the first day was at approximately 6:45AM CST.



## Displaying Data with Matplotlib

https://gis.stackexchange.com/questions/338392/getting-elevation-for-multiple-lat-long-coordinates-in-python


### Creating an Effective Oxygen Pressure Profile


### Displaying in Plotly

Matplotlib to Plotly Converter

https://towardsdatascience.com/matplotlib-to-plotly-chart-conversion-4bd260e73434


### Displaying on Map

https://retz.blog/posts/mapping-gpx-file-data-with-python-plotly-and-mapbox
