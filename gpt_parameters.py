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

import sys, getopt
from ffmpeg import FFmpegLogger

class Parameters:
    def __init__(self):
        # default parameters
        self.filename = ""
        self.configfile = "gpt_config.xml"
        self.overwrite = False
        self.logger = FFmpegLogger(FFmpegLogger.verbosity_off)


    def __usage(self):
        print("Usage: " + sys.argv[0] + " [OPTION]... inputfile\n"
              "Rerender input movie with speed and position on screen\n\n"
              "  -c --config       Configuration file (default = " + self.configfile + ")\n"
              "  -o --overwrite    Overwrite generated files (default = no)\n"
              "  -v --verbose      Display extra information while processing\n"
              "  -vv               Display extra information and subprocess output\n"
              "  -h --help         Display help and exit\n")


    # returns True if parameters could be parsed successfully
    def parse_commandline(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "c:ovh", [
                "config=",
                "overwrite",
                "verbose",
                "help"])
        except getopt.GetoptError:
            self.__usage()
            return False
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.__usage()
                return False
            elif opt in ("-c", "--config"):
                self.configfile = str(arg)
            elif opt in ("-o", "--overwrite"):
                self.overwrite = True
            elif opt in ("-v", "--verbose"):
                self.logger.increase_verbosity()
        
        retval = True
        try:
            self.filename = args[0]
        except:
            self.logger.error("Nothing to do!")
            retval = False

        self.logger.log("Parameters:")
        self.logger.log("filename = " + self.filename)
        self.logger.log("configuration file = " + self.configfile)
        self.logger.log("overwrite = " + str(self.overwrite))
        self.logger.log("verbosity level = " + str(self.logger.verbositylevel))

        return retval

