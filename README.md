# gopro-telemetry

A python script to add telemetry data to GoPro movies.

## Requirements

This script requires at least [python 3.5](https://www.python.org/), [ffmpeg](https://ffmpeg.org/) to realize all operations on the video file and [gopro-utils](https://github.com/stilldavid/gopro-utils) to parse the telemetry data.
Installation and configuration of these requirements can be found on their respective websites.

## Usage

Usage is very simple, as this is the initial version there is not so much to configure:

Usage: ./gpt.py [OPTION]... inputfile

  -o --overwrite      Overwrite generated files (default = no)
  -v --verbose        Display extra information while processing
  -vv                 Display extra information including output of subprocesses
                                         (ffmpeg and gopro2json)
  -h --help           Display help and exit

## Limitations

At the moment only the speed in km/h is supported, in the bottom right corner. Support for GPS location on a map is planned, but this requires some knowledge to set up. See the [hikingmap project](https://github.com/roelderickx/hikingmap) to get an idea.

Performance is also an issue. The extraction of audio and telemetry data is rather fast, but extracting every frame, editing and re-assembling the videofile takes a while.
Also, disk space might be an issue. The individual frames as png files take up about 30x as much space as the input movie and you should provide the same storage a second time for the adapted frames.

For a 1.4 GB input movie (HD at 50fps) it took me about 1 hour for data extraction and several hours for the rendering of the speed data, while disk space for the temporary files is about 100 GB.

