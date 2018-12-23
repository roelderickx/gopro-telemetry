#!/usr/bin/env python

# class FFmpeg -- python interface to the ffmpeg command
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

class FFmpegLogger:
    verbosity_off = 0
    verbosity_normal = 1
    verbosity_detail = 2
    
    def __init__(self, verbositylevel = verbosity_off):
        self.verbositylevel = verbositylevel


    def increase_verbosity(self):
        self.verbositylevel += 1


    def get_ffmpeg_verbosity(self):
        if self.verbositylevel >= self.verbosity_detail:
            return 32 # Show informative messages during processing.
        else:
            return 8 # Only show errors after which the process absolutely cannot continue.


    def log(self, text):
        if self.verbositylevel >= self.verbosity_normal:
            print(text)


    def error(self, text):
        print(text)

