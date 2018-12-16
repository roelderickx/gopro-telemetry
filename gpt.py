#!/usr/bin/env python

# gopro-telemetry -- render speed and position on gopro movies
# Copyright (C) 2018  Roel Derickx <roel.derickx AT gmail>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os
from ffmpeg import Logger
from ffmpeg import VideoProperties
from ffmpeg import FFmpeg
from gpt_parameters import Parameters
from gpt_telemetry import Telemetry

# MAIN

params = Parameters()
if not params.parse_commandline():
    sys.exit()

ffmpeg = FFmpeg(params.logger)

if not os.path.exists(params.filename):
    print("Validation error: filename " + params.filename + " was not found")
    sys.exit()

if not ffmpeg.is_created_by_gopro(params.filename):
    print("Validation error: file is not recorded with a GoPro camera")
    sys.exit()

if not ffmpeg.contains_gopro_telemetry(params.filename):
    print("Validation error: telemetry data not found")
    sys.exit()

retval, vp = ffmpeg.get_video_properties(params.filename)
if not retval:
    print("Validation error: amount of frames and framerate could not be detected")
    sys.exit()

telemetry = Telemetry(params, ffmpeg)

telemetry.add_speed(telemetry.POS_BOTTOM_LEFT, telemetry.SPEED_IMAGE)
telemetry.add_gps_location(telemetry.POS_BOTTOM_RIGHT)
telemetry.add_altitude(telemetry.POS_CENTER_RIGHT)
telemetry.add_temperature(telemetry.POS_TOP_RIGHT)
telemetry.add_datetime(telemetry.POS_BOTTOM_CENTER)

telemetry.generate_overlay()

# TODO: add overlay to input file

