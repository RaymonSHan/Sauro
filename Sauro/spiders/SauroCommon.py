# -*- coding:gbk -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
#
# Wrapping Column 132.

import scrapy
import string
import os                                      # for findfile & error in open
import hashlib                                 # for md5
import fnmatch                                 # for findfile
import errno                                   # for error in open

# for signals in scarpy, such as dispatcher.connect(self.initialize, signals.engine_started) 
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

# for href iteration
from scrapy.linkextractors.sgml import SgmlLinkExtractor
# (deprecated) from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

# for create Selector from read html file, instead of response
# useful in test, but may not in real work
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

# for json process
from json import *

# const for python from http://www.jb51.net/article/60434.htm
class const: 
    class ConstError(TypeError):pass 
    def __setattr__(self, name, value): 
        if self.__dict__.has_key(name): 
            raise self.ConstError, "Can't rebind const (%s)" %name 
        self.__dict__[name]=value

# create filename by md5 for url, with subdir
def GetMD5Filename(urlname):
    md5val = hashlib.md5()
    md5val.update(urlname)
    filename = md5val.hexdigest()
    return const.PAGE_HOME + filename[0:2]+'/'+filename[2:4]+'/'+filename

def CreateSelectorbyFile(filename):
    sel = None
    with open(filename, 'rb') as f:
        filebody = f.read()
        # gbk -> unicode # should remove later
        try:
            sel = Selector(text=filebody.decode('gbk'), type="html")
        except UnicodeDecodeError:
            sel = Selector(text=filebody, type="html")
    return sel
    
def CreateSelectorbyString(string):
    return Selector(text=string, type="html")

# not means get response from web, get it from cache file by Sauro
# ahead with http:// in my project
def CreateSelectorbyURL(urlname):
    return CreateSelectorbyFile(GetMD5Filename(urlname))

# whether the checkstr is substring of one of string in strlist
# return sequence in strlist for first found, or return -1 for not found
def InSubstring(checkstr, strlist):
    order = 0
    for onelist in strlist:
        if onelist.find(checkstr) != -1:
            return order
        order += 1
    return -1

# Divide given stringlist into two part. One list have all eigenvalue, other list have none or part.
def DivideByEigenvalue(eigenlist, totallist):
    withlist = []
    withoutlist = []
    for onelist in totallist:
        hitall = True
        for oneeigen in eigenlist:
            if onelist.find(oneeigen) == -1:
                hitall = False
                break
        if hitall:
            withlist.append(onelist)
        else:
            withoutlist.append(onelist)
    return withlist, withoutlist

# dict { key : ++count }
def IncreaseDictCount(resultdict, key, count = 1):
    try:
        resultdict[key] += count
    except KeyError:
        resultdict[key] = count

def IncreaseDictDictCount(resultdict, key1, key2, count = 1):
    try:
        resultdict[key1][key2] += count
    except KeyError:
        try:
            resultdict[key1][key2] = count
        except KeyError:
            resultdict[key1] = {}
            resultdict[key1][key2] = count

def SumDictCount(resultdict):
    resultsum = 0
    for onedict in resultdict.keys():
        resultsum += resultdict[onedict]
    return resultsum
   
# remove dup in list
def RemoveDuplicateFromList(inputlist):
    returnlist = []
    for onelist in inputlist:
        if not onelist in returnlist:
            returnlist.append(onelist)
    return returnlist

# whether the given fingerprint have a list of eigen in eigendict
# used in IsContentPage
# IN  : fingerprint
#     : eigendictlist
# OUT : the match list, maybe multi result, maybe empty
def FingerprintHaveEigenvalue(fingerprint, eigendictlist):
    returnlist = []
    for eigenkey in eigendictlist.keys():
        hitall = True
        for oneeigen in eigendictlist[eigenkey]:
            if fingerprint.find(oneeigen) == -1:
                hitall = False
                break
        if hitall:
            returnlist.append(eigenkey)
    return returnlist

# generate dict by run each algorithm in list, with the name as the algorithm name
def GenerateDictByAlgorithmList(response, algorithmlist, otherpara=None):
    returndict = {}
    if response:
        for onealgo in algorithmlist:
            returndict[onealgo.__name__] = onealgo(response, otherpara)
    else:
        for onealgo in algorithmlist:
			returndict[onealgo.__name__] = ''
    return returndict

####################################################################################################################################
