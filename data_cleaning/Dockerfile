# create an argument called, "BASE_CONTAINER" and point to jupyter minimal notebook image
ARG BASE_CONTAINER=jupyter/minimal-notebook

FROM $BASE_CONTAINER

LABEL author="Patrick Delaney"

# switch to user root briefly
USER root

# install depdencies
RUN pip install pandas numpy matplotlib plotly

# install gpx tools
RUN pip install gpxpy

# copy data we want to evaluate and play around with:
COPY /datainclude /home/jovyan/work

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
