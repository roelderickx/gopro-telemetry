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
from ffmpeg import FFmpegLogger
from ffmpeg import FFmpeg
from gpt_parameters import Parameters
from gpt_telemetry import Telemetry

# MAIN

params = Parameters()
if not params.parse_commandline():
    sys.exit()

ffmpeg = FFmpeg(params.logger)

# TODO: see if we have to concat other parts of the video
#ffmpeg.gopro_concat_video(os.path.split(os.path.abspath(params.filename))[0])

if not os.path.exists(params.filename):
    params.logger.error("Validation error: filename " + params.filename + " was not found")
    sys.exit()

if not ffmpeg.is_created_by_gopro(params.filename):
    params.logger.error("Validation error: file is not recorded with a GoPro camera")
    sys.exit()

if not ffmpeg.contains_gopro_telemetry(params.filename):
    params.logger.error("Validation error: telemetry data not found")
    sys.exit()

telemetry = Telemetry(params, ffmpeg)

if not telemetry.initialized:
    sys.exit()

telemetry.run_plugins()

