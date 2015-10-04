# -*- coding:gbk -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
#
# Wrapping Column 132.

'''
ORIGIN:
Sauro is an abbreviation Sauropsida ("lizard faces"). A group of amniotes that includes all existing reptiles and birds and their fossil ancestors, in wiki.
Sauro use scarpy, a splider framework in python, see http://doc.scrapy.org/. Other prerequisites included XPath, python, lua.

VERSION:
V0.02  : Sept.28 '15 : first reorgnize, after verified major algorithm.
V0.01  : Sept. 1 '15 : This is my first python project, from empty

GOAL:
SPLIDER, Get TITLE and CONTENT from Industry Information

ALGORITHM:
C001   : Get obvious content page : GetObviousContent()
  V001 : GetContentByLength(response)
         Any page within continuous text longer than MIN_TEXT_LEN

C002   : Get fingerprint of given page : GetPageFingerprint()
  V001 : (obsoletes) by division of URL
  V002 : GetFingerprintByTagOrder(response)
         by structural tag in html page, as HTML_STRUCT_TAG
  V003 : GetFingerprintByScript(response)
         by text length in tag after strip, as SCRIPT_STRUCT_TAG

C003   : Get eigenvalue from fingerprint : GenerateEigenvalue()
  V001 : GetEigenvalueInAll(strlist, otherlist)
         For pages with same parent <div> tag of continuous text, get eigenvalues longer than MIN_EIGENVALUE_LEN from fingerprint for these pages, which given in strlist. All eigenvalues must in every strlist, but not in any otherlist.
  V002 : GetFuzzyEigenvalue(string)
         by common eigenvalues in all fingerprint
  V003 :
         mix C003V001 and C003V002

C004   : Get page items, from pages with eigenvalue in fingerprint
  V001 : GetPageItmes()
       : 

L001   : Get obvious list page
  V001 : Any page contain content page large than MIN_CONTENT_LEN

L002   : Get linked list page, via href in obvious list page

L003   : Get most frequency list page, by detect new content page appear

S001   : Output most frequency list page, by C001, C002, C003, L001, L002, L003
         This is a splider, only output list page, but not get CONTENT
         
S002   : Generate rules for sites from json
         This is a program, input and output are both json files
  V001 : GenerateRuleViaJson()
         use C003 and format it

S003   : Get TITLE and CONTENT by C004 from pages given by S001
         This is a splider, do major job
'''

from SauroAlgorithm import *

def GetTitle(response, otherpara):
    return ALGORITHM['GetTitle'](response, otherpara)

def GetContent(response, otherpara):
    return ALGORITHM['GetContent'](response, otherpara)
    
ALGORITHM = {
#	'GetURL'				            : GetURLinResponse,
#	'GetURL'				            : GetURLinJSONFile,
  'GetObviousContent'         : GetContentByLength, 
  'GetPageFingerprint'        : [GetFingerprintByTagOrder, GetFingerprintByScript],
  'GenerateEigenvalue'        : GetEigenvalueInAll,

  'GetPageItems'              : [GetTitle, GetContent],
  'GetTitle'                  : GetTitleByTag,
  'GetContent'                : GetContentByDiv,
}

# List of Cross-reference
'''
: IN  : SauroCommon.py
def GetMD5Filename(urlname):
def CreateSelectorbyFile(filename):
def CreateSelectorbyString(string):
def CreateSelectorbyURL(urlname):
    SauroCommon : CreateSelectorbyFile()
    SauroCommon : GetMD5Filename()
def InSubstring(checkstr, strlist):
def DivideByEigenvalue(eigenlist, totallist):
def IncreaseDictCount(resultdict, key, count = 1):
def IncreaseDictDictCount(resultdict, key1, key2, count = 1):
def SumDictCount(resultdict):
def RemoveDuplicateFromList(inputlist):
def FingerprintHaveEigenvalue(fingerprint, eigendictlist):
def GenerateDictByAlgorithmList(response, algorithmlist, otherpara=None):

: IN  : SauroXpath.py
def GetXpathfromTag(tag):
def GetTextInTag(response, tag, excludetaglist):
    SauroXpath : GetXpathfromTag()

: IN  : SauroAlgorithm.py
def GetContentByLength(response):
def GetFingerprintByTagOrder(response, otherpara):
def GetFingerprintByScript(response, otherpara):
def GetEigenvalueInAll(strlist, otherlist = []):
    SauroCommon : InSubstring()
def ReturnBestContent(stringlist):
def GetTitleByTag(response, otherpara):
def GetContentByDiv(response, otherpara):
    SauroAlgorithm : ReturnBestContent()

: IN  : SauroSplider.py
def GetPageFingerprint(response, algorithm = ALGORITHM):
    SauroCommon : GenerateDictByAlgorithmList()
def GenerateEigenvalueFromList(resultlist, fingerprint, algroithm):
    SauroCommon : RemoveDuplicateFromList()
    SauroCommon : IncreaseDictDictCount()
    SauroCommon : SumDictCount()
    SauroAlgorithm : GetEigenvalueInAll()
def GenerateRuleViaJson(jsonread, jsonwrite, algorithm = ALGORITHM):
    SauroSplider : GenerateEigenvalueFromList()
def IsContentPage(response, eigendict, algorithm = ALGORITHM):
    SauroSplider : GetPageFingerprint()
    SauroCommon : FingerprintHaveEigenvalue()
    SauroCommon : RemoveDuplicateFromList()
def GetPageItems(response, pagediv, algorithm = ALGORITHM):
    SauroCommon : GenerateDictByAlgorithmList()
'''

####################################################################################################################################

RULE = {
  'stock.sohu.com'            : {
  }
}

'''
def CollectPageFromEigenvalue(resultlist, eigendict, fingerprint):                  USED
    SauroCommon : IncreaseDictDictCount()
def GenerateEigenvalueFromJson(filename, fingerprint, algroithm):                   USED
    eigendict = GenerateEigenvalueFromList(totalresult, fingerprint, algroithm)
    pagedict = CollectPageFromEigenvalue(totalresult, eigendict, fingerprint)
        print onepage, len(pagedict[onepage]), SumDictCount(pagedict[onepage])
'''