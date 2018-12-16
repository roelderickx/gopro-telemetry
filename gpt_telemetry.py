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

import sys, os, subprocess, json
from ffmpeg import Logger
from ffmpeg import VideoProperties
from ffmpeg import FFmpeg

class Telemetry:
    POS_TOP_LEFT = 1
    POS_TOP_CENTER = 2
    POS_TOP_RIGHT = 3
    POS_CENTER_LEFT = 4
    POS_CENTER_CENTER = 5
    POS_CENTER_RIGHT = 6
    POS_BOTTOM_LEFT = 7
    POS_BOTTOM_CENTER = 8
    POS_BOTTOM_RIGHT = 9
    
    SPEED_TEXT = 0
    SPEED_IMAGE = 1
    
    def __init__(self, params, ffmpeg):
        self.logger = params.logger

        self.__gopro2jsonexe = ""
        self.__telemetryfile = params.filename + ".telemetry.bin"
        self.__telemetryjsonfile = params.filename + ".telemetry.json"

        self.__find_gopro2json_executable()
        ffmpeg.fetch_telemetry_stream(params.filename, self.__telemetryfile, params.overwrite)
        self.__convert_telemetry_to_json(params.overwrite)


    def __run_command(self, args):
        retval = True
        output = ""
        try:
            self.logger.log("Running command: " + subprocess.list2cmdline(args))
            process = subprocess.run(args, \
                                     stdout = subprocess.PIPE, \
                                     check = True, \
                                     universal_newlines = True)
            process.check_returncode()
            output = process.stdout
        except subprocess.CalledProcessError as e:
            self.logger.log("Command failed, return code = " + str(e.returncode))
            retval = False
        
        return retval, output


    def __set_gopro2json_executable(self, gopro2jsonexe):
        self.__gopro2jsonexe = gopro2jsonexe.replace('\n', '')
        self.logger.log("gopro2json found, executable location = " + self.__gopro2jsonexe)


    def __find_gopro2json_executable(self):
        self.logger.log("Checking installation of gopro2json")
        
        retval, output = self.__run_command(["which", "gopro2json"])

        if retval:
            self.__set_gopro2json_executable(output)
        else:
            self.logger.log("gopro2json not found")
        
        return retval


    def get_gopro2json_executable(self):
        if self.__gopro2jsonexe == "":
            raise ValueError("gopro2json executable location is unknown")
        return self.__gopro2jsonexe


    def __convert_telemetry_to_json(self, overwrite = False):
        self.logger.log("Converting telemetry to json format")

        retval = True
        if not overwrite and os.path.exists(self.__telemetryjsonfile):
            self.logger.log("Telemetry json file already exists, skipping")
        else:
            retval, output = self.__run_command([
                self.get_gopro2json_executable(),
                "-i", self.__telemetryfile,
                "-o", self.__telemetryjsonfile])
        
        return retval


    def add_speed(self, position, speed_type):
        pass


    def add_gps_location(self, position):
        pass


    def add_altitude(self, position):
        pass


    def add_temperature(self, position):
        pass


    def add_datetime(self, position):
        pass


    def generate_overlay(self):
        pass
'''
    def __convert_json_to_ffmpeg_command(self, overwrite = False):
        self.logger.log("Parsing telemetry json")

        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("FFmpeg command file already exists, skipping")
        else:
            jsondata = []
            try:
                with open(self.__telemetryjsonfile) as f:
                    jsondata = json.load(f)
                    self.logger.log("Parsing succeeded")
            except json.decoder.JSONDecodeError as e:
                self.logger.log("Parsing failed, error = " + e.msg)
                retval = False
        
            if retval:
                self.logger.log("Converting json to ffmpeg command file")
                text_file = open(self.__telemetrycmdfile, "w")
                interval_dataframe = self.gvf.get_duration() / len(jsondata['data'])
                start_time = 0
                for telemetrydata in jsondata['data']:
                    # last record seems to crash ffmpeg
                    # TODO investigate!
                    if telemetrydata != jsondata['data'][-1]:
                        text = "Speed\\ {0:.1f}".format(float(telemetrydata['spd']) * 3.6)
                        text_file.write("{0:.3f}-{1:.3f} [enter] drawtext reinit 'text={2}:x=W-tw-10:y=H-th-10;\n\n".format(start_time, start_time + interval_dataframe, text))
                        start_time += interval_dataframe
                text_file.close()
        
        return retval

    def rerender_video_file(self):
        self.gvf.log("Rendering telemetry data on video stream")
        
        retval, output = self.gvf.run_command([
            self.gvf.get_ffmpeg_executable(),
            "-v", str(self.gvf.ffmpeg_verbosity()),
            "-y",
            "-i", self.gvf.params.filename,
            "-acodec", "copy",
            "-vf", "sendcmd=f=" + self.gvf.params.filename + ".telemetry.cmd," + \
                   "drawtext=text='':" + \
                            "fontfile=/usr/share/fonts/TTF/DejaVuSans.ttf:" + \
                            "fontsize=72:" + \
                            "borderw=2:" + \
                            "bordercolor=0x000000:" + \
                            "fontcolor=0xFFFFFF",
            self.gvf.params.filename + ".rendered.mp4"])
        
        if retval:
            self.gvf.log("Rendering successfull, output file = " + \
                         self.gvf.params.filename + ".rendered.mp4")
        else:
            self.gvf.log("Rendering failed")
        
        return retval
'''

