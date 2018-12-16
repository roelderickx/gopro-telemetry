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

import sys, os, subprocess, tempfile

class Logger:
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


class VideoProperties:
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


class FFmpeg:
    def __init__(self, logger):
        self.logger = logger
        
        self.__ffprobeexe = ""
        self.__ffmpegexe = ""
        
        self.__find_ffprobe_executable()
        self.__find_ffmpeg_executable()


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


    def __set_ffprobe_executable(self, ffprobeexe):
        self.__ffprobeexe = ffprobeexe.replace('\n', '')
        self.logger.log("ffprobe found, executable location = " + self.__ffprobeexe)


    def __find_ffprobe_executable(self):
        self.logger.log("Checking installation of ffprobe")
        
        retval, output = self.__run_command(["which", "ffprobe"])

        if retval:
            self.__set_ffprobe_executable(output)
        else:
            self.logger.log("ffprobe not found")
        
        return retval


    def __set_ffmpeg_executable(self, ffmpegexe):
        self.__ffmpegexe = ffmpegexe.replace('\n', '')
        self.logger.log("ffmpeg found, executable location = " + self.__ffmpegexe)


    def __find_ffmpeg_executable(self):
        self.logger.log("Checking installation of ffmpeg")
        
        retval, output = self.__run_command(["which", "ffmpeg"])

        if retval:
            self.__set_ffmpeg_executable(output)
        else:
            self.logger.log("ffmpeg not found")
        
        return retval


    def get_ffprobe_executable(self):
        if self.__ffprobeexe == "":
            raise ValueError("ffprobe executable location is unknown")
        return self.__ffprobeexe
    
    
    def get_ffmpeg_executable(self):
        if self.__ffmpegexe == "":
            raise ValueError("ffmpeg executable location is unknown")
        return self.__ffmpegexe


    # check if file is created by GoPro
    def is_created_by_gopro(self, filename):
        self.logger.log("Checking GoPro signature")
        
        retval, output = self.__run_command([
            self.get_ffprobe_executable(),
            filename,
            "-v", str(self.logger.get_ffmpeg_verbosity()),
            "-select_streams", "v:0",
            "-print_format", "flat",
            "-show_entries", "stream_tags=encoder"])
        
        if retval and "GoPro" in str(output):
            self.logger.log("GoPro signature found")
        else:
            self.logger.log("GoPro signature not found")
            retval = False

        return retval


    # check if filename contains GoPro telemetry data 
    def contains_gopro_telemetry(self, filename):
        self.logger.log("Checking availability of telemetry data")
        
        retval, output = self.__run_command([
            self.get_ffprobe_executable(),
            filename,
            "-v", str(self.logger.get_ffmpeg_verbosity()),
            "-print_format", "flat",
            "-show_entries", "stream=codec_tag_string"])
        
        if retval and "gpmd" in str(output):
            self.logger.log("Telemetry data found")
        else:
            self.logger.log("Telemetry data not found")
            retval = False

        return retval


    def __get_telemetry_stream_number(self, filename):
        self.logger.log("Fetching telemetry data stream number")
        
        retval, output = self.__run_command([
            self.get_ffprobe_executable(),
            filename,
            "-v", str(self.logger.get_ffmpeg_verbosity()),
            "-print_format", "flat",
            "-show_entries", "stream=codec_tag_string"])
        
        if retval:
            streamlist = str(output).split('\n')
            gpmdstreamlist = [s for s in streamlist if "gpmd" in s]
            gpmdstream = gpmdstreamlist[0].split('.codec')[0][-1]
            
            self.logger.log("Telemetry found at stream 0:" + gpmdstream)
        
            return retval, gpmdstream
        else:
            self.logger.log("Telemetry stream number not found")
            
            return retval, None

    
    # infilename = gopro created MP4 file
    #              test first with is_created_by_gopro() and contains_gopro_telemetry()
    # outfilename = outut telemetry file, binary stream
    def fetch_telemetry_stream(self, infilename, outfilename, overwrite = False):
        self.logger.log("Fetching telemetry")
        
        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("Telemetry file already exists, skipping")
        else:
            retval, gpmdstream = self.__get_telemetry_stream_number(infilename)

            if retval:
                self.logger.log("Fetching telemetry data stream to " + outfilename)
                
                retval, output = self.__run_command([
                    self.get_ffmpeg_executable(),
                    "-v", str(self.logger.get_ffmpeg_verbosity()),
                    "-y",
                    "-i", infilename,
                    "-codec", "copy",
                    "-map", "0:" + gpmdstream,
                    "-f", "rawvideo",
                    outfilename])
        
        return retval


    # get framerate, duration, width and height from filename
    # returns boolean if succeeded and an instance of VideoProperties
    def get_video_properties(self, filename):
        self.logger.log("Fetching video properties")
        
        retval, output = self.__run_command([
            self.get_ffprobe_executable(),
            filename,
            "-v", str(self.logger.get_ffmpeg_verbosity()),
            "-select_streams", "v:0",
            "-print_format", "flat",
            "-show_entries", "stream=r_frame_rate,duration,width,height"])
        
        vp = VideoProperties(self.logger)
        if retval:
            vp.parse(str(output))
                        
        return retval, vp


    # rescales infilename to outfilename
    # newscale can be anything the scale videofilter of ffmpeg understands
    # eg 640:360 or iw/1:ih/2
    def rescale_video(self, infilename, outfilename, newscale, overwrite = False):
        self.logger.log("Rescaling video")
        
        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("Rescaled file already exists, skipping")
        else:
            retval, output = self.__run_command([
                self.get_ffmpeg_executable(),
                "-v", str(self.logger.get_ffmpeg_verbosity()),
                "-y",
                "-i", infilename,
                "-vf", "scale=" + newscale,
                "-c:a", "copy",
                outfilename])
                        
        return retval


    # concatenate infilenames to outfilename
    # infilenames is a list of filenames
    #             if the filenames don't start with / then a relative path is assumed
    def concat_video(self, infilenames, outfilename, overwrite = False):
        self.logger.log("Concatenating files")

        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("Concatenated file already exists, skipping")
        else:
            self.logger.log("Creating temporary concatenation file")
            (fd, concattempfile) = tempfile.mkstemp(prefix = "class_ffmpeg_concat_video", \
                                                    suffix = ".list")
            f = os.fdopen(fd, 'w')
            for filename in infilenames:
                f.write("file " + os.path.abspath(filename) + "\n")
            f.close()
            
            retval, output = self.__run_command([
                self.get_ffmpeg_executable(),
                "-v", str(self.logger.get_ffmpeg_verbosity()),
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concattempfile,
                "-c", "copy",
                outfilename])
            
            # remove temp file
            if concattempfile and os.path.isfile(concattempfile):
                print("Removing temp file " + concattempfile)
                os.remove(concattempfile)
        
        return retval


# cutup video
# first -ss parameter: fast search
# second -ss parameter: precision search, offset id previous search
# -t parameter: duration
#ffmpeg -y -strict 2 -ss 00:15:00 -i GP012495.MP4 -ss 00:00:58 -t 00:00:19.1 -c copy jo_kmo_rijdt_door_rood.mp4


# render timelapse
#ffmpeg -y -start_number 1840 -r 25 -i G001%04d.JPG -r 25 dag1_aankomst.mp4

