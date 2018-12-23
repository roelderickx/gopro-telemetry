#!/usr/bin/env python

# gpt_plugin_parameters.py -- parameter class from gopro-telemetry plugins
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
from xml.dom import minidom
from ffmpeg import FFmpegLogger

class PluginParameters:
    POS_HORIZ_LEFT = -1
    POS_HORIZ_CENTER = 0
    POS_HORIZ_RIGHT = 1
    POS_VERT_TOP = -1
    POS_VERT_CENTER = 0
    POS_VERT_BOTTOM = 1

    def __init__(self, logger):
        self.logger = logger
        
        # default parameters
        self.horizpos = self.POS_HORIZ_RIGHT
        self.vertpos = self.POS_VERT_BOTTOM
        self.pluginlib = ""
        self.jsontag = ""
        self.pluginparams = {}


    def __get_xml_subtag_value(self, xmlnode, sublabelname, defaultvalue):
        elements = xmlnode.getElementsByTagName(sublabelname)
        return str(elements[0].firstChild.nodeValue) \
                      if elements and elements[0].childNodes \
                      else defaultvalue


    def parse_plugin_parameters(self, xmlnode):
        hpos = self.__get_xml_subtag_value(xmlnode.getElementsByTagName('position')[0], \
                                           'horiz', 'right').lower()
        if hpos == "left":
            self.horizpos = self.POS_HORIZ_LEFT
        elif hpos == "center":
            self.horizpos = self.POS_HORIZ_CENTER
        else:
            self.horizpos = self.POS_HORIZ_RIGHT

        vpos = self.__get_xml_subtag_value(xmlnode.getElementsByTagName('position')[0], \
                                           'vert', 'bottom').lower()
        if vpos == "top":
            self.vertpos = self.POS_VERT_TOP
        elif vpos == "center":
            self.vertpos = self.POS_VERT_CENTER
        else:
            self.vertpos = self.POS_VERT_BOTTOM
        
        self.pluginlib = self.__get_xml_subtag_value(xmlnode, 'pluginlib', '')
        self.jsontag = self.__get_xml_subtag_value(xmlnode, 'jsontag', '')
        
        self.logger.log("Plugin parameters:")
        self.logger.log("horizpos = " + hpos)
        self.logger.log("vertpos = " + vpos)
        self.logger.log("jsontag = " + self.jsontag)
        
        for param in xmlnode.getElementsByTagName('params')[0].childNodes:
            if param.nodeType == param.ELEMENT_NODE:
                self.pluginparams[param.nodeName] = param.firstChild.nodeValue;
        
        for param in self.pluginparams:
            self.logger.log(param + " = " + self.pluginparams[param])


    def get_position_ffmpeg(self):
        xpos = "x="
        if self.horizpos == self.POS_HORIZ_LEFT:
            xpos = xpos + "10"
        elif self.horizpos == self.POS_HORIZ_CENTER:
            xpos = xpos + "(W-tw)/2"
        else:
            xpos = xpos + "W-tw-10"

        ypos = "y="
        if self.vertpos == self.POS_VERT_TOP:
            ypos = ypos + "10"
        elif self.vertpos == self.POS_VERT_CENTER:
            ypos = ypos + "(H-th)/2"
        else:
            ypos = ypos + "H-th-10"
        return xpos + ":" + ypos

