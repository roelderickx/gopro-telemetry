# gopro-telemetry

A python script to add telemetry data to GoPro movies.

## Requirements

This script requires at least [python 3.5](https://www.python.org/), [ffmpeg](https://ffmpeg.org/) to realize all operations on the video file and [gopro-utils](https://github.com/stilldavid/gopro-utils) to parse the telemetry data.
Installation and configuration of these requirements can be found on their respective websites.

## Usage

Usage is very simple, as this is the initial version there is not so much to configure:

```
Usage: gpt.py [OPTION]... inputfile

  -o --overwrite      Overwrite generated files (default = no)
  -v --verbose        Display extra information while processing
  -vv                 Display extra information including output of subprocesses
                                         (ffmpeg and gopro2json)
  -h --help           Display help and exit
```

## Limitations

At the moment only the speed in km/h is supported, in the bottom right corner. Support for GPS location on a map is planned, but this requires some knowledge to set up. See the [hikingmap project](https://github.com/roelderickx/hikingmap) to get an idea.

Also, the code is a mess but since this is a prototype it will probably be rewritten at some point. Reliability and functionality are the main priority now.

Performance has greatly improved since the previous version. The speed can be added to a six minute video in about 20 minutes. Temporary diskspace is reduced to about 1 MB per minute, but you should provide enough diskspace for the resulting video as well.

