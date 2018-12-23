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

class FFmpegVideoProperties:
    def __init__(self, logger):
        self.logger = logger
        self.framerate = 0
        self.duration = 0.0
        self.video_width = 0
        self.video_height = 0


    def __parse_framerate(self, instring):
        # get the part behind =
        rate = instring.split('=')[1]
        # strip the quotes
        rate = rate.replace('"', '').strip()
        #  split when / is found
        ratelist = rate.split('/')

        if len(ratelist) == 1:
            self.framerate = float(ratelist[0])
        elif len(ratelist) == 2:
            self.framerate = float(ratelist[0])/float(ratelist[1])
        self.logger.log("Detected framerate = " + str(self.framerate))
        

    def __parse_duration(self, instring):
        # get the part behind =
        duration = instring.split('=')[1]
        # strip the quotes
        duration = duration.replace('"', '').strip()
        self.duration = float(duration)
        self.logger.log("Detected duration = " + str(self.duration))
        

    def __parse_video_width(self, instring):
        # get the part behind =
        width = instring.split('=')[1]
        self.video_width = int(width)
        self.logger.log("Detected frame width = " + str(self.video_width))


    def __parse_video_height(self, instring):
        # get the part behind =
        height = instring.split('=')[1]
        self.video_height = int(height)
        self.logger.log("Detected frame height = " + str(self.video_height))


    def parse(self, ffproberesult):
        outlist = ffproberesult.split("\n")
        for prop in outlist:
            if "r_frame_rate" in prop:
                self.__parse_framerate(prop)
            elif "duration" in prop:
                self.__parse_duration(prop)
            elif "width" in prop:
                self.__parse_video_width(prop)
            elif "height" in prop:
                self.__parse_video_height(prop)

