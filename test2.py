#-------------------------------------------------------------------------------
# Name:         configInterface
# Purpose:
#
# Author:      hou
#
# Created:     19/11/2015
# Copyright:   (c) hou 2015
# Licence:     <your licence>
#------------------------------------------------------------------------------

import json
import logging
import threading
import time
import multiprocessing

import httpInterface
from configini import cfg_time
from configini import errordic


class Configure():
    config = None
    messagecomcfg = None
    messagebuscfg = None
    lookbackcfg = None

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.interface = httpInterface.HttpInterface()


    def get_serverconfigure(self,nodeid):
        message = self.interface.get_configure(nodeid).get("message")
        if message is not None:
            try:

                Configure.config = message
                if self.check_json() is True:
                    self.interface.post_mediaServer(Configure.config)
                    self.interface.post_indexServer(Configure.config.update(Configure.lookbackcfg))
                    self._logger.info("[Configure] configure message post Success")
                    return True
                else:
                    self._logger.info("[Configure] configure message post false")
                    return False
            except Exception, e:
                self._logger.info("[Configure]get message configure false:%s", str(e))
                return False
        else:
            return False

    def check_json(self):

        common = Configure.config.get("c")
        if common is None:
            self._logger.info("[check_json] get 'c' configure error [%s]",errordic[1])
            return False
        else:
            Configure.messagecomcfg = common

        if self.check_json_public() is False:
            return False

        serviceTypelist = Configure.messagecomcfg.get("serviceType")
        if serviceTypelist is None:
            self._logger.info("[check_json]'serviceType' error [%s]",errordic[1])
            return False
        elif type(serviceTypelist) != unicode and type(serviceTypelist) != str:
            self._logger.info("[check_json]'serviceType' error [%s]",errordic[2])
            return False
        elif 0 == len(serviceTypelist):
            self._logger.info("[check_json]'serviceType' error [%s]",errordic[3])
            return False

        servicelist = serviceTypelist.split('#')
        if len(servicelist) != 3:
            self._logger.info("[check_json]'serviceType' numbers error [%s]",errordic[4])
            return False

        for servicetype in servicelist:
            print servicetype
            common = Configure.config.get(servicetype)

            if common is None:
                self._logger.info("[check_json] '%s' error",servicetype)
                return False
            else:
                Configure.messagebuscfg = common

            if servicetype == "1":
                if self.check_json_liverecord() is False:
                    return False
            elif servicetype == "2":
                if self.check_json_livepull() is False:
                    return False
            elif servicetype == "3":
                if self.check_json_lookbackrecord() is False:
                    return False

        return True

    def check_json_public(self):

        redisServer = Configure.messagecomcfg.get("redisServer")
        if redisServer is None:
            self._logger.info("[check_json_public] 'redisServer' error [%s]",errordic[1])
            return False
        elif type(redisServer) != unicode and type(redisServer) != str:
            self._logger.info("[check_json_public] 'redisServer' error [%s]",errordic[2])
            return False
        elif 0 == len(redisServer):
            self._logger.info("[check_json_public] 'redisServer' error [%s]",errordic[3])
            return False

        listenPort = Configure.messagecomcfg.get("listenPort")
        if listenPort is None:
            self._logger.info("[check_json_public]'listenPort' error [%s]", errordic[1])
            return False
        elif type(listenPort) != int:
            self._logger.info("[check_json_public]'listenPort' error [%s]", errordic[2])
            return False
        return True

    def check_json_liverecord(self):

        recordType = Configure.messagebuscfg.get("recordType")
        if recordType is None:
            self._logger.info("[check_json_liverecord]'recordType' error [%s]", errordic[1])
            return False
        elif type(recordType) != int:
            self._logger.info("[check_json_liverecord]'recordType' error [%s]", errordic[2])
            Configure.messagebuscfg["recordType"] = 1
            return False

        mediaRootDir = Configure.messagebuscfg.get("mediaRootDir")
        if mediaRootDir is None:
            self._logger.info("[check_json_liverecord]'mediaRootDir' error [%s]", errordic[1])
            return False
        elif type(mediaRootDir) != unicode and type(mediaRootDir) != str:
            self._logger.info("[check_json_liverecord]'mediaRootDir' error [%s]", errordic[2])
            return False
        elif 0 == len(mediaRootDir):
            self._logger.info("[check_json_liverecord]'mediaRootDir' error [%s]", errordic[3])
            return False

        indexDownLoadInterval = Configure.messagebuscfg.get("indexDownLoadInterval")
        if indexDownLoadInterval is None:
            self._logger.info("[check_json_liverecord]'indexDownLoadInterval' error [%s]", errordic[1])
            return False
        elif type(indexDownLoadInterval) != int:
            self._logger.info("[check_json_liverecord]'indexDownLoadInterval' error [%s]", errordic[2])
            Configure.messagebuscfg["indexDownLoadInterval"] = 5
            return False

        storySegNum = Configure.messagebuscfg.get("storySegNum")
        if storySegNum is None:
            self._logger.info("[check_json_liverecord]'storySegNum' error [%s]", errordic[1])
            return False
        elif type(storySegNum) != int:
            self._logger.info("[check_json_liverecord]'storySegNum' error [%s]", errordic[2])
            Configure.messagebuscfg["storySegNum"] = 30
            return False

        indexSegNum = Configure.messagebuscfg.get("indexSegNum")
        if indexSegNum is None:
            self._logger.info("[check_json_liverecord]'indexSegNum' error [%s]", errordic[1])
            return False
        elif type(indexSegNum) != int:
            self._logger.info("[check_json_liverecord]'indexSegNum' error [%s]", errordic[2])
            Configure.messagebuscfg["indexSegNum"] = 3
        elif indexSegNum > storySegNum:
            self._logger.info("[check_json_liverecord]'indexSegNum' error [%s]", errordic[4])
            return False

        indexOffSet = Configure.messagebuscfg.get("indexOffSet")
        if indexOffSet is None:
            self._logger.info("[check_json_liverecord]'indexOffSet' error [%s]", errordic[1])
            return False
        elif type(indexOffSet) != int:
            self._logger.info("[check_json_liverecord]'indexOffSet' error [%s]", errordic[2])
            Configure.messagebuscfg["indexOffSet"] = 3
            return False
        elif indexOffSet > storySegNum:
            self._logger.info("[check_json_liverecord]'indexOffSet' error [%s]", errordic[4])
            return False

        channelSet = Configure.messagebuscfg.get("channelSet")

        if channelSet is None:
            self._logger.info("[check_json_liverecord]'channelSet' error [%s]", errordic[1])
            return False
        elif type(channelSet) != list:
            self._logger.info("[check_json_liverecord]'channelSet' error [%s]", errordic[2])
            return False
        elif len(channelSet) == 0:
            self._logger.info("[check_json_liverecord]'channelSet' error [%s]", errordic[3])
            return False
        for channel_json in channelSet:
            channel = channel_json.get("channel")
            if channel is None:
                self._logger.info("[check_json_liverecord]'channel' error [%s]", errordic[1])
                return False
            elif type(channel) != unicode and type(channel) != str:
                self._logger.info("[check_json_liverecord]'channel' error [%s]", errordic[2])
                return False
            elif 0 == len(channel):
                self._logger.info("[check_json_liverecord]'channel' error [%s]", errordic[3])
                return False

            url = channel_json.get("url")
            if url is None:
                self._logger.info("[check_json_liverecord]'url' error [%s]", errordic[1])
                return False
            elif type(url) != unicode and type(url) != str:
                self._logger.info("[check_json_liverecord]'url' error [%s]", errordic[2])
                return False
            elif 0 == len(url):
                self._logger.info("[check_json_liverecord]'url' error [%s]", errordic[3])
                return False
        return True

    def check_json_livepull(self):

        downLoadType = Configure.messagebuscfg.get("downLoadType")
        if downLoadType is None:
            self._logger.info("[check_json_livepull]'downLoadType' error [%s]", errordic[1])
            return False
        elif type(downLoadType) != int:
            self._logger.info("[check_json_livepull]'downLoadType' error [%s]", errordic[2])
            Configure.messagebuscfg["downLoadType"] = 1
            return False

        subRedisServer = Configure.messagebuscfg.get("subRedisServer")
        if downLoadType == 1:
            if subRedisServer is None:
                self._logger.info("[check_json_livepull]'subRedisServer' error [%s]", errordic[1])
                return False
            elif type(subRedisServer) != unicode and type(subRedisServer) != str:
                self._logger.info("[check_json_livepull]'subRedisServer' error [%s]", errordic[2])
                return False
            elif 0 == len(subRedisServer):
                self._logger.info("[check_json_livepull]'subRedisServer' error [%s]", errordic[3])
                return False

        mediaRootDir = Configure.messagebuscfg.get("mediaRootDir")
        if mediaRootDir is None:
            self._logger.info("[check_json_livepull]'mediaRootDir' error [%s]", errordic[1])
            return False
        elif type(mediaRootDir) != unicode and type(mediaRootDir) != str:
            self._logger.info("[check_json_livepull]'mediaRootDir' error [%s]", errordic[2])
            return False
        elif 0 == len(mediaRootDir):
            self._logger.info("[check_json_livepull]'mediaRootDir' error [%s]", errordic[3])
            return False

        indexDownLoadInterval = Configure.messagebuscfg.get("indexDownLoadInterval")
        if indexDownLoadInterval is None:
            self._logger.info("[check_json_livepull]'indexDownLoadInterval' error [%s]", errordic[1])
            return False
        elif type(indexDownLoadInterval) != int:
            self._logger.info("[check_json_livepull]'indexDownLoadInterval' error [%s]", errordic[2])
            Configure.messagebuscfg["indexDownLoadInterval"] = 5
            return False

        storySegNum = Configure.messagebuscfg.get("storySegNum")
        if storySegNum is None:
            self._logger.info("[check_json_livepull]'storySegNum' error [%s]", errordic[1])
            return False
        elif type(storySegNum) != int:
            self._logger.info("[check_json_livepull]'storySegNum' error [%s]", errordic[2])
            Configure.messagebuscfg["storySegNum"] = 30
            return False

        indexSegNum = Configure.messagebuscfg.get("indexSegNum")
        if indexSegNum is None:
            self._logger.info("[check_json_livepull]'indexSegNum' error [%s]", errordic[1])
            return False
        elif type(indexSegNum) != int:
            self._logger.info("[check_json_livepull]'indexSegNum' error [%s]", errordic[2])
            Configure.messagebuscfg["indexSegNum"] = 3
            return False
        elif indexSegNum > storySegNum:
            self._logger.info("[check_json_livepull]'indexSegNum' error [%s]", errordic[4])

        indexOffSet = Configure.messagebuscfg.get("indexOffSet")
        if indexOffSet is None:
            self._logger.info("[check_json_livepull]'indexOffSet' error [%s]", errordic[1])
            return False
        elif type(indexOffSet) != int:
            self._logger.info("[check_json_livepull]'indexOffSet' error [%s]", errordic[2])
            Configure.messagebuscfg["indexOffSet"] = 3
            return False
        elif indexOffSet > storySegNum:
            self._logger.info("[check_json_livepull]'indexOffSet' error [%s]", errordic[4])
            return False

        channelSet = Configure.messagebuscfg.get("channelSet")
        if downLoadType == 2:
            if channelSet is None:
                self._logger.info("[check_json_livepull]'channelSet' error [%s]", errordic[1])
                return False
            elif type(channelSet) != list:
                self._logger.info("[check_json_livepull]'channelSet' error [%s]", errordic[2])
                return False
            elif len(channelSet) == 0:
                self._logger.info("[check_json_livepull]'channelSet' error [%s]", errordic[3])
                return False

            for channel_json in channelSet:
                channel = channel_json.get("channel")
                if channel is None:
                    self._logger.info("[check_json_livepull]'channel' error [%s]", errordic[1])
                    return False
                elif type(channel) != unicode and type(channel) != str:
                    self._logger.info("[check_json_livepull]'channel' error [%s]", errordic[2])
                    return False
                elif 0 == len(channel):
                    self._logger.info("[check_json_livepull]'channel' error [%s]", errordic[3])
                    return False

                if downLoadType == 2:
                    url = channel_json.get("url")
                    if url is None:
                        self._logger.info("[check_json_livepull]'url' error [%s]", errordic[1])
                        return False
                    elif type(url) != unicode and type(url) != str:
                        self._logger.info("[check_json_livepull]'url' error [%s]", errordic[2])
                        return False
                    elif 0 == len(url):
                        self._logger.info("[check_json_livepull]'url' error [%s]", errordic[3])
                        return False
        return True

    def check_json_lookbackrecord(self):

        mediaRootDir = Configure.messagebuscfg.get("mediaRootDir")
        if mediaRootDir is None:
            self._logger.info("[check_json_lookbackrecord]'mediaRootDir' error [%s]", errordic[1])
            return False
        elif type(mediaRootDir) != unicode and type(mediaRootDir) != str:
            self._logger.info("[check_json_lookbackrecord]'mediaRootDir' error [%s]", errordic[2])
            return False
        elif 0 == len(mediaRootDir):
            self._logger.info("[check_json_lookbackrecord]'mediaRootDir' error [%s]", errordic[3])

        recordDays = Configure.messagebuscfg.get("recordDays")
        if recordDays is None:
            self._logger.info("[check_json_lookbackrecord]'recordDays' error [%s]", errordic[1])
            return False
        elif type(recordDays) != int:
            self._logger.info("[check_json_lookbackrecord]'recordDays' error [%s]", errordic[2])
            Configure.messagebuscfg["recordDays"] = 7
            return False
        Configure.lookbackcfg = Configure.messagebuscfg
        return True

def time_getconfig(nodeid):

    config = Configure()
    global t
    bgetcfg = Configure().get_serverconfigure(nodeid)
    if bgetcfg is False:
        print"[get_configure false]!"
    else:
        print"[get_configure success]!"

    t = threading.Timer(cfg_time,time_getconfig,[nodeid])
    t.start()


##def main():
##
##    t = threading.Timer(cfg_time,time_getconfig,["11"])
##    t.start()
##
##if __name__ == '__main__':
##    main()


