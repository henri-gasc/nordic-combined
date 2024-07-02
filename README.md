# Nordic Combined

## Code organization

You can put the PDFs with the data in [`pdf_results`](./pdf_results/) and use the [extract](./extract.py) Python script to write the data from the PDFs to [`extracted`](./extracted/).

You can use [`main.py`](./main.py) to run a simulation.

[`athelete.py`](./athlete.py) contains the code pertaining to each athlete.  
In [`render.py`](./render.py), you will find the base class for rendering and showing the simulation, whereas the code for the simulation proper is in [`simulation.py`](./simulation.py).  
[`utils.py`](./utils.py) has utility functions, things too small to be in a separate file.  

[`plot.py`](./plot.py) and [`parse.py`](./parse.py) are scripts used to plot things when needed. (for example, the evolution of the correctness rate for a single race for `plot.py`.)

## Ideas

Here are some ideas on how to visualize the simualtion:

1. Still image. Work, but not very clear.
2. Video like [time_vs_distance](./time_vs_distance.mp4). Better(?) but takes very long to render. It took me about >2h to render the simple simulation.
3. Video like [athlete_distance](./athlete_distance.mp4). Only works on video format. Thanks to multiprocessing is fast => need ffmpeg to fuse the images in a single video after.

## Slipstream effect

### With energy level

Each athlete has maximum speed they can achieve, and minimum speed at which they do not tire themselves at. In slipstream, the athlete behind do not tire as fast as without (can even regenerate speed if slow enough).

### Without energy level

Get a boost for 5 seconds after 2 seconds in slipstream.
