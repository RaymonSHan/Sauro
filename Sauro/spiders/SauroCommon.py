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
import json                                    # for json process

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

# const for python from http://www.jb51.net/article/60434.htm
class const: 
    class ConstError(TypeError):pass 
    def __setattr__(self, name, value): 
        if self.__dict__.has_key(name): 
            raise self.ConstError, "Can't rebind const (%s)" %name 
        self.__dict__[name]=value

const.NOT_FOUND = -1

# create filename by md5 for url, with subdir
def GetMD5Filename(urlname):
    md5val = hashlib.md5()
    md5val.update(urlname)
    filename = md5val.hexdigest()
    return const.PAGE_HOME + filename[0:2]+'/'+filename[2:4]+'/'+filename

def CreateRawbyFile(filename):
    sel = None
    with open(filename, 'rb') as f:
        filebody = f.read()
# gbk -> unicode # should remove later
# should change later        
# see https://docs.python.org/2/howto/unicode.html#the-unicode-type
    return filebody.decode('gbk', 'ignore')
        
def CreateRawbyURL(urlname):
    return CreateRawbyFile(GetMD5Filename(urlname))

def CreateSelectorbyString(string):
    return Selector(text=string, type="html")

def CreateSelectorbyFile(filename):
    return Selector(text=CreateRawbyFile(filename), type="html")

# not means get response from web, get it from cache file by Sauro
# ahead with http:// in my project
def CreateSelectorbyURL(urlname):
    return CreateSelectorbyFile(GetMD5Filename(urlname))

# whether the checkstr is substring of one of string in strlist
# return sequence in strlist for first found, or return -1 for not found
def InSubString(checkstr, strlist):
    order = 0
    for onelist in strlist:
        if onelist.find(checkstr) != const.NOT_FOUND:
            return order
        order += 1
    return -1
    
# whether the one of string in strlist is substring of checkstr 
# return sequence in strlist for first found, or return -1 for not found
def InSuperString(checkstr, strlist):
    order = 0
    for onelist in strlist:
        if checkstr.find(onelist) != const.NOT_FOUND:
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
            if onelist.find(oneeigen) == const.NOT_FOUND:
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

def ReadFromJson(filename):
    with open(filename, 'rb') as f:
        alljson = json.loads(f.read())
    return alljson

def WriteToJson(filename, alljson):
    with open(filename, 'wb') as f:
        f.write(json.dumps(alljson, ensure_ascii=False))

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
            if fingerprint.find(oneeigen) == const.NOT_FOUND:
                hitall = False
                break
        if hitall:
            returnlist.append(eigenkey)
    return returnlist

# generate dict by run each algorithm in list, with the name as the algorithm name
# if otherpara is [], means it is not content page
def GenerateDictByAlgorithmList(response, algorithmlist, otherpara=[]):
    returndict = {}
    if response:
        for onealgo in algorithmlist:
            returndict[onealgo.__name__] = onealgo(response, otherpara)
    else:
        for onealgo in algorithmlist:
    	    returndict[onealgo.__name__] = ''
    return returndict

def ReturnStringTotalLenght(totalstring):                   # totalstring is []
    totallength = 0
    for onestring in totalstring:
        totallength += len(onestring)
    return totallength   
####################################################################################################################################
