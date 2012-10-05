#! /usr/bin/env python
# Copyright (C) 2010 Brad Kozlek
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version as published by
# the Free Software Foundation. http://www.gnu.org/licenses/gpl.html

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import urllib2
import time
import re
from xml.dom import minidom
import sys

#Change this to be your posterous hostname without the .posterous.com at the end.
MY_POSTEROUS_HOSTNAME = "transatlantical"
#Change this to the path where you would like to store your backup.
BACKUP_DIR_PATH = "backup"

#Probably don't want to to touch these. Having standard names will help if anyone ever makes something to take the data and import it.
BACKUP_XML_DIR_NAME ="xml"
BACKUP_FILES_DIR_NAME = "files"

def message(string):
    print string

def xmlStringForURL(URL):
    response = urllib2.urlopen(URL)
    xmlString = response.read()
    return xmlString
    
def saveStringToFile(myString, filePathString):
    f = open(filePathString, 'w')
    f.write(myString)
    f.close()

def xmlBackupDirName():
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    return os.path.join(BACKUP_DIR_PATH,BACKUP_XML_DIR_NAME,timestamp)
    
def xmlStringHasPosts(xmlString):
    hasPosts = False
    dom = minidom.parseString(xmlString)
    posts = dom.getElementsByTagName("post")
    if len(posts) > 0:
        hasPosts = True
    return hasPosts

def xmlOkay(xmlString):
    responseOkay = False
    dom = minidom.parseString(xmlString)
    rsplist = dom.getElementsByTagName("rsp")
    rsp = rsplist[0]
    status = rsp.attributes["stat"].value
    if status == "ok":
        responseOkay = True
    return responseOkay

def saveXMLFilesToDirectory(dirname):
    os.makedirs(dirname)
    page = 1
    while(1):
        URL = "http://posterous.com/api/readposts?hostname=%s&num_posts=50&page=%s" % (MY_POSTEROUS_HOSTNAME, page)
        xml = xmlStringForURL(URL)
        if not xmlStringHasPosts(xml):
            #If the return has no posts, then I assume the previous page was the last. We can just stop here.
            break
        filename = os.path.join(dirname,"page%s.xml" % page)
        message("saving xml for page %s\n" % page)
        saveStringToFile(xml, filename)
        page = page + 1
        if not xmlOkay(xml):
            message("Backup Failed. Posterous returned an error")
            sys.exit()
        

def listOfPosterousFilesMentionedInXmlDir(dirname):
    files = os.listdir(dirname)
    returnUrlList = []
    for file in files:
        f= open(dirname+"/"+file, 'r')
        xml =  f.read()
        urlList = re.findall(r'http://getfile.*?\.posterous\.com/getfile/.*?[<\'\"]',xml)
        for url in urlList:
            returnUrlList.append(url[:-1]) 
    return returnUrlList

def listOfOriginalPosterousFiles(urlList):
    returnOrigUrlList = []

    scaledRe = re.compile(r'.*\.(thumb|scaled[0-9]*)', re.I)
    origRe = re.compile(r'(?P<origurl>.*)\.(thumb|scaled[0-9]*)', re.I)

    for url in urlList:
        if scaledRe.match(url):
            origUrl = origRe.search(url).group('origurl')
            if origUrl not in returnOrigUrlList:
                print "orig file: %s" % origUrl
                returnOrigUrlList.append(origUrl)
    return returnOrigUrlList
        
def getPosterousFile(url):
    urlDir = re.sub(r'http://getfile.*?\.posterous\.com/getfile/', '', url)
    dirList = urlDir.split("/")
    fileName = dirList.pop()
    fileBackupDir = os.path.join(BACKUP_DIR_PATH, BACKUP_FILES_DIR_NAME)
    for dir in dirList:
        fileBackupDir = os.path.join(fileBackupDir, dir)
    if not os.path.isdir(fileBackupDir):
        os.makedirs(fileBackupDir)
    backupFilePath = os.path.join(fileBackupDir, fileName)
    
    if not os.path.isfile(backupFilePath):
        message("getting ready to download %s to %s" % (url, backupFilePath))
        try:
            f = urllib2.urlopen(url)
            lf = open(backupFilePath, 'w')
            lf.write(f.read())
            lf.close()
            message("done")
        except urllib2.HTTPError as httperror:
            print "Download failed: %s" % (httperror)
    else:
        message("file exists, skipping %s" % backupFilePath)
                
def main():
    if MY_POSTEROUS_HOSTNAME == "put hostname here":
        print "You need to edit the script to configure it with your posterous hostname"
        sys.exit()
    
    dirName = xmlBackupDirName()
    saveXMLFilesToDirectory(dirName)
    urlList = listOfPosterousFilesMentionedInXmlDir(dirName)
    urlList.extend(listOfOriginalPosterousFiles(urlList))
    for url in urlList:
        getPosterousFile(url)

main()