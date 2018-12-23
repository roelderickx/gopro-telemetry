# gopro-telemetry

A python script to add telemetry data to GoPro movies.

## Requirements

This script requires at least [python 3.5](https://www.python.org/), [ffmpeg](https://ffmpeg.org/) to realize all operations on the video file and [gopro-utils](https://github.com/stilldavid/gopro-utils) to parse the telemetry data.
Installation and configuration of these requirements can be found on their respective websites.

## Configuration

TODO: explain the workings of gpt_config.xml

## Usage

Usage is straightforward, everything is configured in the configuration XML file described above.

```
Usage: gpt.py [OPTION]... inputfile

  -c --config         Configuration file (default = gpt_config.xml)
  -o --overwrite      Overwrite generated files (default = no)
  -v --verbose        Display extra information while processing
  -vv                 Display extra information including output of subprocesses
                                         (ffmpeg and gopro2json)
  -h --help           Display help and exit
```

## Limitations

Support for GPS location on a map is not yet available but planned, but this requires some knowledge to set up. See the [hikingmap project](https://github.com/roelderickx/hikingmap) to get an idea.

Performance has greatly improved since the previous version. The speed can be added to a six minute video in about 20 minutes. Temporary diskspace is reduced to about 1 MB per minute, but you should provide enough diskspace for the resulting video as well.

