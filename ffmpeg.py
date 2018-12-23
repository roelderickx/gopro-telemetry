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

from ffmpeg_logger import FFmpegLogger
from ffmpeg_videoproperties import FFmpegVideoProperties

class FFmpeg:
    def __init__(self, logger):
        self.logger = logger
        
        self.__ffprobeexe = ""
        self.__ffmpegexe = ""
        
        self.__find_ffprobe_executable()
        self.__find_ffmpeg_executable()


    def _run_command(self, args):
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
            self.logger.error("Command failed, return code = " + str(e.returncode))
            retval = False
        
        return retval, output


    def __set_ffprobe_executable(self, ffprobeexe):
        self.__ffprobeexe = ffprobeexe.replace('\n', '')
        self.logger.log("ffprobe found, executable location = " + self.__ffprobeexe)


    def __find_ffprobe_executable(self):
        self.logger.log("Checking installation of ffprobe")
        
        retval, output = self._run_command(["which", "ffprobe"])

        if retval:
            self.__set_ffprobe_executable(output)
        else:
            self.logger.error("ffprobe not found")
        
        return retval


    def __set_ffmpeg_executable(self, ffmpegexe):
        self.__ffmpegexe = ffmpegexe.replace('\n', '')
        self.logger.log("ffmpeg found, executable location = " + self.__ffmpegexe)


    def __find_ffmpeg_executable(self):
        self.logger.log("Checking installation of ffmpeg")
        
        retval, output = self._run_command(["which", "ffmpeg"])

        if retval:
            self.__set_ffmpeg_executable(output)
        else:
            self.logger.error("ffmpeg not found")
        
        return retval


    def get_ffprobe_executable(self):
        if self.__ffprobeexe == "":
            raise ValueError("ffprobe executable location is unknown")
        return self.__ffprobeexe
    
    
    def get_ffmpeg_executable(self):
        if self.__ffmpegexe == "":
            raise ValueError("ffmpeg executable location is unknown")
        return self.__ffmpegexe


    # description: check if a video file is created by GoPro
    # parameters : filename : the video file to check
    # returns    : True when GoPro signature is found
    def is_created_by_gopro(self, filename):
        self.logger.log("Checking GoPro signature in " + filename)
        
        retval, output = self._run_command([
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


    # description: check if a video file contains GoPro telemetry data 
    # parameters : filename : the video file to check
    # returns    : True when telemetry data is found
    def contains_gopro_telemetry(self, filename):
        self.logger.log("Checking availability of GoPro telemetry data in " + filename)
        
        retval, output = self._run_command([
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
        self.logger.log("Fetching telemetry data stream number from " + filename)
        
        retval, output = self._run_command([
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
            
            return False, None

    
    # description: extract GoPro telemetry data from a video file
    # remarks    : the video file should contain telemetry data, test first with
    #              is_created_by_gopro() and contains_gopro_telemetry()
    # parameters : infilename : the video file containing telemetry data
    #              outfilename : the filename where the telemetry data should be written
    #              overwrite : if True then outfilename will always be overwritten
    # returns    : True when telemetry data is found and could be extracted
    def fetch_telemetry_stream(self, infilename, outfilename, overwrite = False):
        self.logger.log("Extracting telemetry data from " + infilename)
        
        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("Telemetry file already exists, skipping")
        else:
            retval, gpmdstream = self.__get_telemetry_stream_number(infilename)

            if retval:
                retval, output = self._run_command([
                    self.get_ffmpeg_executable(),
                    "-v", str(self.logger.get_ffmpeg_verbosity()),
                    "-y",
                    "-i", infilename,
                    "-codec", "copy",
                    "-map", "0:" + gpmdstream,
                    "-f", "rawvideo",
                    outfilename])
        
        return retval


    # description: get framerate, duration, width and height from a video file
    # parameters : filename : the video file of which the parameters should be fetched
    # returns    : True if successful and an instance of FFmpegVideoProperties
    def get_video_properties(self, filename):
        self.logger.log("Fetching video properties of " + filename)
        
        retval, output = self._run_command([
            self.get_ffprobe_executable(),
            filename,
            "-v", str(self.logger.get_ffmpeg_verbosity()),
            "-select_streams", "v:0",
            "-print_format", "flat",
            "-show_entries", "stream=r_frame_rate,duration,width,height"])
        
        vp = FFmpegVideoProperties(self.logger)
        if retval:
            vp.parse(str(output))
                        
        return retval, vp


    # description: rescales a video file
    # parameters : infilename : the video file to be rescaled
    #              newscale : the new dimensions of the video, this can be anything the
    #                         scale videofilter of ffmpeg understands
    #                         eg: 640:360 or iw/1:ih/2
    #              outfilename : the resulting video file
    #              overwrite : if True then outfilename will always be overwritten
    # returns    : True if successful
    def rescale_video(self, infilename, newscale, outfilename, overwrite = False):
        self.logger.log("Rescaling " + infilename)
        
        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("Output file already exists, skipping")
        else:
            retval, output = self._run_command([
                self.get_ffmpeg_executable(),
                "-v", str(self.logger.get_ffmpeg_verbosity()),
                "-y",
                "-i", infilename,
                "-vf", "scale=" + newscale,
                "-c:a", "copy",
                outfilename])
                        
        return retval


    # description: extracts a section from a video file
    # parameters : infilename : the video file where the section will be extracted from
    #              start_hh,
    #              start_mi,
    #              start_ss: the timestamp (hour, minute and second) of the start of the
    #                        section to be extracted.
    #                        hh and mi are integers, ss is a float
    #              duration_hh,
    #              duration_mi,
    #              duration_ss: the duration (hour, minute and second) of the section to
    #                           be extracted.
    #                           hh and mi are integers, ss is a float
    #              outfilename : the resulting video file
    #              overwrite : if True then outfilename will always be overwritten
    # returns    : True if successful
    def extract_section_from_video(self, \
                    infilename, start_hh, start_mi, start_ss, \
                    duration_hh, duration_mi, duration_ss, \
                    outfilename, overwrite = False):
        self.logger.log("Extracting section from " + infilename)

        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("Output file already exists, skipping")
        else:
            retval, output = self._run_command([
                self.get_ffmpeg_executable(),
                "-v", str(self.logger.get_ffmpeg_verbosity()),
                "-y",
                "-strict", "2",
                "-ss", "{:02d}:{:02d}:00.000".format(start_hh, max(0, start_mi - 1)),
                "-i", infilename,
                "-ss", "00:{:02d}:{:06.3f}".format(min(start_mi, 1), start_ss),
                "-t", "{:02d}:{:02d}:{:06.3f}".format(duration_hh, duration_mi, duration_ss),
                #"-c", "copy",
                outfilename])
        
        return retval


    # description: concatenate two or more video files
    # parameters : infilenames : a list of video files
    #                            if the filenames don't start with / then a relative
    #                            path is assumed
    #              outfilename : the resulting video file
    #              overwrite : if True then outfilename will always be overwritten
    # returns    : True if successful
    def concat_video(self, infilenames, outfilename, overwrite = False):
        self.logger.log("Concatenating files %s to %s" % (", ".join(infilenames), outfilename))

        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("Output file already exists, skipping")
        else:
            self.logger.log("Creating temporary concatenation file")
            (fd, concattempfile) = tempfile.mkstemp(prefix = "class_ffmpeg_concat_video", \
                                                    suffix = ".list")
            f = os.fdopen(fd, 'w')
            for filename in infilenames:
                f.write("file " + os.path.abspath(filename) + "\n")
            f.close()
            
            retval, output = self._run_command([
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
                self.logger.log("Removing temp file " + concattempfile)
                os.remove(concattempfile)
        
        return retval


    # description: concatenate GoPro video files according to the GoPro naming scheme
    #              the resulting files are name __GPxxxx.MP4
    # parameters : inputdir : the path to search for video files
    #              cleanup : original video files will be removed if this parameter is set
    #              overwrite : if True then outfilename will always be overwritten
    # returns    : True if successful
    def gopro_concat_video(self, inputdir, cleanup = False, overwrite = False):
        self.logger.log("Concatenating GoPro files")
        
        filelist = sorted(os.listdir(inputdir))
        
        # https://gopro.com/help/articles/question_answer/GoPro-Camera-File-Naming-Convention
        # Camera Models: HD HERO2, HERO3, HERO3+, HERO (2014), HERO Session, 
        # HERO4, HERO5 Black, HERO5 Session
        videofilelist = [x for x in filelist if x[:4] == "GOPR" and x[-3:] == "MP4"]
        # Camera Model: HERO6 Black
        videofilelist = videofilelist + \
                        [x for x in filelist if x[:4] in ("GH01", "GX01") and x[-3:] == "MP4"]
        self.logger.log("Found video files %s" % (", ".join(videofilelist)))
        
        comblist = [[y for y in filelist if y[4:8] in x] for x in videofilelist]
        
        for filenames in comblist:
            fullfilename = os.path.join(params.inputdir, filenames[0])
            newfilename = os.path.join(params.inputdir, "__GP" + filenames[0][4:8] + ".MP4")
            
            if len(filenames) == 1:
                self.logger.log("Renaming %s to %s" % (fullfilename, newfilename))
                os.rename(fullfilename, newfilename)
            else:
                self.concat_video(filenames, newfilename, overwrite)

                if retval:
                    if cleanup:
                        self.logger.log("Removing original files")
                        for filename in filenames:
                            os.remove(os.path.join(params.inputdir, filename))
                else:
                    return False
        
        return True


    def apply_custom_filter(self, infilename, filterparams, outfilename, overwrite = False):
        self.logger.log("Applying custom filter on %s to %s" % (infilename, outfilename))

        retval = True
        if not overwrite and os.path.exists(outfilename):
            self.logger.log("Output file already exists, skipping")
        else:
            cmd = [ self.get_ffmpeg_executable(),
                    "-v", str(self.logger.get_ffmpeg_verbosity()),
                    "-y",
                    "-i", infilename ] + \
                  filterparams + \
                  [ outfilename ]
            
            retval, output = self._run_command(cmd)
        
        return retval

