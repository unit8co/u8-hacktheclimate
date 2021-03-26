# Hack the climate - for a sustainable world!

Developed as part of the DevPost climate hackathon: https://hacktheclimate.devpost.com/

## Challenge picked

Methane as a greenhouse gas is 84 times more powerful than carbon dioxide over a 20-year period. Around a third of anthropogenic methane emissions come from the fossil fuel industry; it seeps from deep coal mines, it vents from oil and gas wells, and it leaks from pipelines. The extent of these emissions has historically been underestimated, and voluntary reporting of emissions has proved insufficient. With global demand for fossil fuels forecast to rebound, it is more important than ever to understand the climate impact of their production. Only in recent years have the tools become available to measure methane emissions directly, although the practice is in its infancy. The challenge is to use the available monitoring data to identify large methane emission events, and attribute these to fossil fuel infrastructure on the ground. This will help to identify the offending players and raise awareness of the true climate impact of fossil fuels

## Inspiration

We are entering the last 2 decades before climate change becomes irreversible. Methane is a large contributor to global warming and there is a lack of accountability for large pollution events, especially by  the coal/fossil and gas industry

New satellite imaging has recently allowed to keep track of methane emissions close to real-time. However, access to the data and the potential methane leak event is still complicated. We think we can make that simpler so people can be aware of new leaks as they arrive and enable them to take actions

## What it does

Our tool uses satellite data from (Sentinel 5P and other sources) to automatically detect new potential methane leaks by custering abnormal emissions and linking them to the fossil infrastructure.

An easy UI allows then everyone to look at recent methane events and get more information on what happens: criticality of event, size, location, visual images.

We hope that gives an easy tool for people to track and then easily raise awareness on such events as they unfold

### Notebooks

Some example notebooks can be found in the `notebooks/` directory

### Library

The library can be found under `methane/` folder with some autogenrated document

### Azure

Azure function are available in the `azure-daily-hotspots/` directory

## How we built it

* Use Google Earth Engine to access methane, IR and wind data
* Extract all methane hotspots by abnormal methane cluster
* Link these "hotspots" to the fossil infratructure (mines, plants and pipelines)
* Assess the link between the event and the infrastructure and create a criticality score for events
* Automate the pipeline using Azure function so it refreshes daily 
* Create a user-friendly UI to be able to monitor all events detected with all required contextual information

## Challenges we ran into

* Google Earth Engine is not so user friendly and exporting data from it is challenging
* Identifying methane clusters was challenging. We think we can still improve the detection with more complex logic by better including infrared and with more complex models

## Accomplishments that we're proud of

* Developed an E2E pipeline for detecting methane hotspots linekd to fossile infrastructure
* An easy-to-use UI that run and gets refreshed automatically that can already be used

## What we learned

* Geosatellite data is its own beast
* Methane data is hard to access and any initiative to make it easier to work on it will be helpful to others
* Don't give up, things work out in the end

## What's next for Methane Leaks - Unit8 Climate

* Get feedback on current tools
* Work on improving model and espcially how to best link detected events with a precise source
