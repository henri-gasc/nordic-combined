# Nordic Combined

Here are some ideas on how to visualize the simualtion:

1. Still image. Work, but not very clear.
2. Video like [time_vs_distance](./time_vs_distance.mp4). Better(?) but takes very long to render. It took me about >2h to render the simple simulation.
3. Video like [athlete_distance](./athlete_distance.mp4). Only works on video format. Thanks to multiprocessing is fast => need ffmpeg to fuse the images in a single video after.

## Slipstream effect

### With energy level

Each athlete has maximum speed they can achieve, and minimum speed at which they do not tire themselves at. In slipstream, the athlete behind do not tire as fast as without (can even regenerate speed if slow enough).

### Without energy level

Get a boost for 5 seconds after 2 seconds in slipstream.
