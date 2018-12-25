# gopro-telemetry

A python script to add telemetry data to GoPro movies.

## Requirements

This script requires at least [python 3.5](https://www.python.org/), [ffmpeg](https://ffmpeg.org/) to realize all operations on the video file and [gopro-utils](https://github.com/stilldavid/gopro-utils) to parse the telemetry data.
Installation and configuration of these requirements can be found on their respective websites.

## Configuration

Gopro-telemetry will add each telemetry value using a plugin. There are plugins available to display speed, altitude, temperature and the date and time in UTC. However, for now they are limited to display the value as text.

The configuration of the plugins can be done in the file gpt_config.xml, an example configuration is included in this repository. For each plugin there are a number of common parameters; these include the label, whether the plugin is enabled or not, the python module to load, the tag to look for in the telemetry json file and the position where the plugin should be displayed.

Each plugin also has specific parameters. Currently the unit can be configured for the speed (either `metric_speed` for km/h or `imperial_speed` for mph) and the temperature (either `temp_celcius` or `temp_fahrenheit`).

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

## Processing

First of all, gopro-telemetry will search and copy the telemetry data stream from the input video file using ffmpeg, after which gopro-utils will convert the data to a human-readable json file.

Next, the plugins which are enabled will be run consecutively. This will create a temporary video file for each plugin, adding a new data element to the resulting video file of the previous plugin.

## Limitations

Support for GPS location on a map is not yet available, but this requires some knowledge to set up. See the [hikingmap project](https://github.com/roelderickx/hikingmap) to get an idea.

Performance has greatly improved since the previous version. Each data item can be added to a six minute video in about 20 minutes. Temporary diskspace is reduced to about 1 MB per minute, but you should provide enough diskspace for the resulting video files of each plugin as well.

