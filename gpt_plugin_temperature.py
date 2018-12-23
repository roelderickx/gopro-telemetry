#!/usr/bin/env python

# gpt_plugin_temperature -- render temperature on gopro movies
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

import sys, os, tempfile

def render(params, jsondata, ffmpeg, inputfile, outputfile, overwrite = False):
    # write to tempfile
    (fd, temptextfile) = tempfile.mkstemp(prefix = "gpt_plugin_temperature", suffix = ".txt")
    f = os.fdopen(fd, 'w')

    start_time = 0
    textpos = params.get_position_ffmpeg()
    for jd in jsondata[:-1]:  # TODO: investigate why last record crashes ffmpeg
        text = "Temp\\ {0:.1f}".format(jd[0])
        f.write("{0:.3f}-{1:.3f} [enter] ".format(start_time, start_time + jd[1]))
        f.write("drawtext reinit 'text={0}:{1}';\n".format(text, textpos))
        start_time = start_time + jd[1]

    f.close()

    # render
    retval = ffmpeg.apply_custom_filter(\
                inputfile, \
                ["-acodec", "copy",
                 "-vf", "sendcmd=f=" + temptextfile + "," + \
                        "drawtext=text='':" + \
                                 "fontfile=/usr/share/fonts/TTF/DejaVuSans.ttf:" + \
                                 "fontsize=72:" + \
                                 "borderw=2:" + \
                                 "bordercolor=0x000000:" + \
                                 "fontcolor=0xFFFFFF",], \
                outputfile,
                overwrite)

    # remove temp file
    if temptextfile and os.path.isfile(temptextfile):
        params.logger.log("Removing temp file " + temptextfile)
        os.remove(temptextfile)
    
    return retval

