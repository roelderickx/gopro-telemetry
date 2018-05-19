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

import sys, os, getopt, subprocess, json

class Parameters:
    def __init__(self):
        # default parameters
        self.filename = ""
        self.overwrite = False
        self.verbose = False
        self.subprocessverbose = False


    def __usage(self):
        print("Usage: " + sys.argv[0] + " [OPTION]... inputfile\n"
              "Rerender input movie with speed and position on screen\n\n"
              "  -o --overwrite      Overwrite generated files (default = no)\n"
              "  -v --verbose        Display extra information while processing\n"
              "  -vv                 Display extra information and subprocess output\n"
              "  -h --help           Display help and exit\n")


    # returns True if parameters could be parsed successfully
    def parse_commandline(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "ovh", [
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
            elif opt in ("-o", "--overwrite"):
                self.overwrite = True
            elif opt in ("-v", "--verbose"):
                if not self.verbose:
                    self.verbose = True
                else:
                    self.subprocessverbose = True

        retval = True
        try:
            self.filename = args[0]
        except:
            print("Nothing to do!")
            retval = False

        if self.verbose:
            print("Parameters:")
            print("filename = " + self.filename)
            print("overwrite = " + str(self.overwrite))
            print("verbose = " + str(self.verbose))
            print("subprocessverbose = " + str(self.subprocessverbose))

        return retval


class GlobalVariablesFunctions:
    def __init__(self, parameters):
        self.params = parameters
        self.__ffprobeexe = ""
        self.__ffmpegexe = ""
        self.__gopro2jsonexe = ""
        # self.__gopro2gpxexe = ""
        self.__framerate = -1
        self.__duration = -1
        self.__video_width = -1
        self.__video_height = -1


    def log(self, text):
        if self.params.verbose:
            print(text)
    
    
    def run_command(self, args):
        retval = True
        output = ""
        try:
            self.log("Running command: " + ' '.join(args))
            process = subprocess.run(args, \
                                     stdout=subprocess.PIPE, \
                                     check=True, \
                                     universal_newlines=True)
            process.check_returncode()
            output = process.stdout
        except subprocess.CalledProcessError as e:
            self.log("Command failed, return code = " + str(e.returncode))
            retval = False
        
        return retval, output


    def ffmpeg_verbosity(self):
        if self.params.subprocessverbose:
            return 32 # Show informative messages during processing.
        else:
            return 8 # Only show errors after which the process absolutely cannot continue.


    def set_ffprobe_executable(self, ffprobeexe):
        self.__ffprobeexe = ffprobeexe.replace('\n', '')
        self.log("ffprobe found, executable location = " + self.__ffprobeexe)


    def get_ffprobe_executable(self):
        if self.__ffprobeexe == "":
            raise ValueError("ffprobe executable location is unknown")
        return self.__ffprobeexe
    
    
    def set_ffmpeg_executable(self, ffmpegexe):
        self.__ffmpegexe = ffmpegexe.replace('\n', '')
        self.log("ffmpeg found, executable location = " + self.__ffmpegexe)


    def get_ffmpeg_executable(self):
        if self.__ffmpegexe == "":
            raise ValueError("ffmpeg executable location is unknown")
        return self.__ffmpegexe
    
    
    def set_gopro2json_executable(self, gopro2jsonexe):
        self.__gopro2jsonexe = gopro2jsonexe.replace('\n', '')
        self.log("gopro2json found, executable location = " + self.__gopro2jsonexe)


    def get_gopro2json_executable(self):
        if self.__gopro2jsonexe == "":
            raise ValueError("gopro2json executable location is unknown")
        return self.__gopro2jsonexe
    
    
    def parse_framerate(self, instring):
        # get the part behind =
        rate = instring.split('=')[1]
        # strip the quotes
        rate = rate.replace('"', '').strip()
        #  split when / is found
        ratelist = rate.split('/')

        if len(ratelist) == 1:
            self.__framerate = float(ratelist[0])
        elif len(ratelist) == 2:
            self.__framerate = float(ratelist[0])/float(ratelist[1])

        self.log("Detected framerate = " + str(self.__framerate))


    def get_framerate(self):
        if self.__framerate == -1:
            raise ValueError("Framerate is not yet loaded")
        return self.__framerate
        

    def parse_duration(self, instring):
        # get the part behind =
        duration = instring.split('=')[1]
        # strip the quotes
        duration = duration.replace('"', '').strip()
        self.__duration = float(duration)
        self.log("Detected duration = " + str(self.__duration))


    def get_duration(self):
        if self.__duration == -1:
            raise ValueError("Duration is not yet loaded")
        return self.__duration
        

    def parse_video_width(self, instring):
        # get the part behind =
        width = instring.split('=')[1]
        self.__video_width = int(width)
        self.log("Detected frame width = " + str(self.__video_width))


    def get_video_width(self):
        if self.__video_width == -1:
            raise ValueError("Video width is not yet loaded")
        return self.__video_width


    def parse_video_height(self, instring):
        # get the part behind =
        height = instring.split('=')[1]
        self.__video_height = int(height)
        self.log("Detected frame height = " + str(self.__video_height))


    def get_video_height(self):
        if self.__video_height == -1:
            raise ValueError("Video height is not yet loaded")
        return self.__video_height

    
class Validator:
    def __init__(self, gvf):
        self.gvf = gvf

    
    def __is_ffprobe_installed(self):
        self.gvf.log("Checking installation of ffprobe")
        
        retval, output = self.gvf.run_command(["which", "ffprobe2.8"])
        
        if retval:
            self.gvf.set_ffprobe_executable(output)
        else:
            retval, output = self.gvf.run_command(["which", "ffprobe"])

            if retval:
                self.gvf.set_ffprobe_executable(output)
            else:
                self.gvf.log("ffprobe not found")
        
        return retval


    def __is_ffmpeg_installed(self):
        self.gvf.log("Checking installation of ffmpeg")
        
        retval, output = self.gvf.run_command(["which", "ffmpeg2.8"])
        
        if retval:
            self.gvf.set_ffmpeg_executable(output)
        else:
            retval, output = self.gvf.run_command(["which", "ffmpeg"])

            if retval:
                self.gvf.set_ffmpeg_executable(output)
            else:
                self.gvf.log("ffmpeg not found")
        
        return retval


    def __is_gopro2json_installed(self):
        self.gvf.log("Checking installation of gopro2json")
        
        retval, output = self.gvf.run_command(["which", "gopro2json"])
        
        if retval:
            self.gvf.set_gopro2json_executable(output)
        else:
            self.gvf.log("gopro2json not found")
        
        return retval
    
    
    def __is_created_by_gopro(self):
        self.gvf.log("Checking GoPro signature")
        
        retval, output = self.gvf.run_command([
            self.gvf.get_ffprobe_executable(),
            self.gvf.params.filename,
            "-v", str(self.gvf.ffmpeg_verbosity()),
            "-select_streams", "v:0",
            "-print_format", "flat",
            "-show_entries", "stream_tags=encoder"])
        
        if retval and "GoPro" in str(output):
            self.gvf.log("GoPro signature found")
        else:
            self.gvf.log("GoPro signature not found")
            retval = False

        return retval


    def __contains_telemetry(self):
        self.gvf.log("Checking availability of telemetry data")
        
        retval, output = self.gvf.run_command([
            self.gvf.get_ffprobe_executable(),
            self.gvf.params.filename,
            "-v", str(self.gvf.ffmpeg_verbosity()),
            "-print_format", "flat",
            "-show_entries", "stream=codec_tag_string"])
        
        if retval and "gpmd" in str(output):
            self.gvf.log("Telemetry data found")
        else:
            self.gvf.log("Telemetry data not found")
            retval = False

        return retval
        
    
    def __get_video_properties(self):
        self.gvf.log("Fetching video properties")
        
        retval, output = self.gvf.run_command([
            self.gvf.get_ffprobe_executable(),
            self.gvf.params.filename,
            "-v", str(self.gvf.ffmpeg_verbosity()),
            "-select_streams", "v:0",
            "-print_format", "flat",
            "-show_entries", "stream=r_frame_rate,duration,width,height"])
        
        if retval:
            outlist = str(output).split("\n")
            for prop in outlist:
                if "r_frame_rate" in prop:
                    self.gvf.parse_framerate(prop)
                elif "duration" in prop:
                    self.gvf.parse_duration(prop)
                elif "width" in prop:
                    self.gvf.parse_video_width(prop)
                elif "height" in prop:
                    self.gvf.parse_video_height(prop)
                        
        return retval


    def validate(self):
        retval = True
        
        if retval and not os.path.exists(self.gvf.params.filename):
            print("Validation error: filename " + self.gvf.params.filename + " was not found")
            retval = False
        
        if retval and not self.__is_ffprobe_installed():
            print("Validation error: ffprobe is not installed or not found in PATH")
            retval = False
        
        if retval and not self.__is_ffmpeg_installed():
            print("Validation error: ffmpeg is not installed or not found in PATH")
            retval = False
        
        if retval and not self.__is_gopro2json_installed():
            print("Validation error: gopro2json is not installed or not found in PATH")
            retval = False
        
        if retval and not self.__is_created_by_gopro():
            print("Validation error: file is not recorded with a GoPro camera")
            retval = False
        
        if retval and not self.__contains_telemetry():
            print("Validation error: telemetry data not found")
            retval = False
        
        if retval and not self.__get_video_properties():
            print("Validation error: amount of frames and framerate could not be detected")
            retval = False
        
        return retval


class Telemetry:
    POS_TOP_LEFT = 1
    POS_TOP_RIGHT = 2
    POS_BOTTOM_LEFT = 3
    POS_BOTTOM_RIGHT = 4

    def __init__(self, gvf):
        self.gvf = gvf
        self.telemetryfile = self.gvf.params.filename + ".telemetry.bin"
        self.telemetryjsonfile = self.gvf.params.filename + ".telemetry.json"
        self.telemetrycmdfile = self.gvf.params.filename + ".telemetry.cmd"
        self.jsondata = []


    def __get_telemetry_stream_number(self):
        self.gvf.log("Fetching telemetry data stream number")
        
        retval, output = self.gvf.run_command([
            self.gvf.get_ffprobe_executable(),
            self.gvf.params.filename,
            "-v", str(self.gvf.ffmpeg_verbosity()),
            "-print_format", "flat",
            "-show_entries", "stream=codec_tag_string"])
        
        if retval:
            streamlist = str(output).split('\n')
            gpmdstreamlist = [s for s in streamlist if "gpmd" in s]
            gpmdstream = gpmdstreamlist[0].split('.codec')[0][-1]
            
            self.gvf.log("Telemetry found at stream 0:" + gpmdstream)
        
            return retval, gpmdstream
        else:
            self.gvf.log("Telemetry stream number not found")
            
            return retval, None

    
    def __fetch_telemetry_stream(self, gpmdstream):
        self.gvf.log("Fetching telemetry data stream to " + self.telemetryfile)
        
        retval, output = self.gvf.run_command([
            self.gvf.get_ffmpeg_executable(),
            "-v", str(self.gvf.ffmpeg_verbosity()),
            "-y",
            "-i", self.gvf.params.filename,
            "-codec", "copy",
            "-map", "0:" + gpmdstream,
            "-f", "rawvideo",
            self.telemetryfile])
        
        return retval
    
    
    def __convert_telemetry_to_json(self):
        self.gvf.log("Converting telemetry to json format")

        retval = True
        retval, output = self.gvf.run_command([
            self.gvf.get_gopro2json_executable(),
            "-i", self.telemetryfile,
            "-o", self.telemetryjsonfile])
        
        return retval


    def __dump_ffmpeg_command_file(self):
        self.gvf.log("Parsing telemetry json")

        retval = True
        try:
            with open(self.telemetryjsonfile) as f:
                self.jsondata = json.load(f)
                self.gvf.log("Parsing succeeded")
        except json.decoder.JSONDecodeError as e:
            self.gvf.log("Parsing failed, error = " + e.msg)
            retval = False
    
        if retval:
            self.gvf.log("Converting json to ffmpeg command file")
            text_file = open(self.telemetrycmdfile, "w")
            interval_dataframe = self.gvf.get_duration() / len(self.jsondata['data'])
            start_time = 0
            for telemetrydata in self.jsondata['data']:
                # last record seems to crash ffmpeg
                # TODO investigate!
                if telemetrydata != self.jsondata['data'][-1]:
                    text = "Speed\\ {0:.1f}".format(float(telemetrydata['spd']) * 3.6)
                    text_file.write("{0:.3f}-{1:.3f} [enter] drawtext reinit 'text={2}:x=W-tw-10:y=H-th-10;\n\n".format(start_time, start_time + interval_dataframe, text))
                    start_time += interval_dataframe
            text_file.close()
        
        return retval
    
    
    def fetch_telemetry(self):
        self.gvf.log("Fetching telemetry")
        
        retval = True
        if not self.gvf.params.overwrite and os.path.exists(self.telemetryfile):
            self.gvf.log("Telemetry file exists already, skipping")
        else:
            retval, gpmdstream = self.__get_telemetry_stream_number()

            if retval:
                retval = self.__fetch_telemetry_stream(gpmdstream)
            
        if not self.gvf.params.overwrite and os.path.exists(self.telemetryjsonfile):
            self.gvf.log("Telemetry json file exists already, skipping")
        elif retval:
            retval = self.__convert_telemetry_to_json()
        
        if not self.gvf.params.overwrite and os.path.exists(self.telemetrycmdfile):
            self.gvf.log("Telemetry cmd file exists already, skipping")
        elif retval:
            retval = self.__dump_ffmpeg_command_file()

        return retval


class Renderer:
    def __init__(self, gvf, telemetry):
        self.gvf = gvf
        self.telemetry = telemetry

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


# MAIN

params = Parameters()
if not params.parse_commandline():
    sys.exit()

gvf = GlobalVariablesFunctions(params)

validator = Validator(gvf)
if not validator.validate():
    sys.exit()

# step 1: extract telemetry from inputfile
telemetry = Telemetry(gvf)
if not telemetry.fetch_telemetry():
    sys.exit()

# step 2: render telemetry data on video stream
renderer = Renderer(gvf, telemetry)
if not renderer.rerender_video_file():
    sys.exit()

