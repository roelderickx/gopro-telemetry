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

import sys, os, json, subprocess, importlib
from xml.dom import minidom
from ffmpeg import FFmpegLogger
from ffmpeg import FFmpegVideoProperties
from ffmpeg import FFmpeg
from gpt_plugin_parameters import PluginParameters

class Telemetry:
    def __init__(self, params, ffmpeg):
        self.logger = params.logger

        self.__params = params
        self.__ffmpeg = ffmpeg

        self.__gopro2jsonexe = ""
        self.__telemetryfile = params.filename + ".telemetry.bin"
        self.__telemetryjsonfile = params.filename + ".telemetry.json"
        self.__outputfile = params.filename + ".rendered.mp4"
        
        self.__vp = None
        self.__jsondata = []

        self.initialized = \
            self.__find_gopro2json_executable() and \
            self.__ffmpeg.fetch_telemetry_stream(params.filename, \
                                                 self.__telemetryfile, \
                                                 params.overwrite) and \
            self.__convert_telemetry_to_json(params.overwrite) and \
            self.__fetch_videoproperties() and \
            self.__parse_json()


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
            self.logger.error("Command failed, return code = " + str(e.returncode))
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
            self.logger.error("gopro2json not found")
        
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


    def __fetch_videoproperties(self):
        retval, self.__vp = self.__ffmpeg.get_video_properties(self.__params.filename)
        
        return retval


    def __parse_json(self):
        self.logger.log("Parsing telemetry json")

        retval = True
        try:
            with open(self.__telemetryjsonfile) as f:
                self.__jsondata = json.load(f)
                self.logger.log("Parsing succeeded")
        except json.decoder.JSONDecodeError as e:
            self.logger.error("Parsing failed, error = " + e.msg)
            retval = False
        
        return retval


    def __get_unit_conversion(self, pluginparams):
        conv_func = lambda x: x
        
        if "unit" in pluginparams.pluginparams:
            unit = pluginparams.pluginparams["unit"].lower()
            if unit == "metric_speed":
                conv_func = lambda x: x * 3.6
            elif unit == "imperial_speed":
                conv_func = lambda x: x * 2.236936
            elif unit == "temp_fahrenheit":
                conv_func = lambda x: x * 9/5 + 32
            
        return conv_func


    # description: returns a list of (value, duration) for a given tagname
    def get_jsondata(self, pluginparams):
        tagvalues = [ data[pluginparams.jsontag] for data in self.__jsondata['data'] \
                                                          if pluginparams.jsontag in data ]
        interval = self.__vp.duration / len(tagvalues)
        conv_func = self.__get_unit_conversion(pluginparams)
        retlist = [ (conv_func(value), interval) for value in tagvalues ]
        
        # TODO: optimize: if value doesn't change
        #       remove the element and modify duration of preceding element
        
        return retlist


    # description: call function in a given module with given arguments
    def __call_plugin(self, module_name, function_name, *args):
        try:
            mod=importlib.import_module(module_name)
        except:
            raise Exception("Can't import module '%s'" % module_name)
            
        try:
            fnc = getattr(mod, function_name)
        except:
            raise Exception("Module '%s' doesn't have a 'run' function" % mod)
        
        if not callable(fnc):
            raise Exception("Can't call 'run' function of callable '%S'" % module_name)
        
        return fnc(*args)


    def __get_xml_subtag_value(self, xmlnode, sublabelname, defaultvalue):
        elements = xmlnode.getElementsByTagName(sublabelname)
        return str(elements[0].firstChild.nodeValue) \
                      if elements and elements[0].childNodes \
                      else defaultvalue


    def __get_next_chain_filename(self, index):
        return self.__params.filename + ".filter_" + str(index) + ".mp4"


    def run_plugins(self):
        xmldoc = minidom.parse(self.__params.configfile)
        xmlgpt = xmldoc.getElementsByTagName('goprotelemetry')[0]
        
        xmlpluginlist = xmlgpt.getElementsByTagName('plugin')
        
        retval = True
        chain_index = 1
        chain_infilename = self.__params.filename
        chain_outfilename = self.__get_next_chain_filename(chain_index)
        for xmlplugin in xmlpluginlist:
            pluginlabel = self.__get_xml_subtag_value(xmlplugin, 'label', '[unnamed]')
            pluginenabled = self.__get_xml_subtag_value(xmlplugin, 'enabled', 'false')
            
            if pluginenabled.lower() == "true":
                self.logger.log("Found enabled plugin rendering " + pluginlabel)
                
                pluginparams = PluginParameters(self.logger)
                pluginparams.parse_plugin_parameters(xmlplugin)
                
                plugindata = self.get_jsondata(pluginparams)
                
                retval = self.__call_plugin(pluginparams.pluginlib, "render", \
                                            pluginparams, plugindata, self.__ffmpeg, \
                                            chain_infilename, chain_outfilename)
                
                if not retval:
                    break
                
                chain_index = chain_index + 1
                chain_infilename = chain_outfilename
                chain_outfilename = self.__get_next_chain_filename(chain_index)
            else:
                self.logger.log("Skipping disabled plugin rendering " + pluginlabel)
        
        if retval and chain_index > 1:
            os.rename(chain_infilename, self.__outputfile)

