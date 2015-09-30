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
C001   : Get obvious content page 
  V001 : GetContentByLength(response)
         Any page within continuous text longer than MIN_TEXT_LEN

C002   : Get fingerprint of given page
  V001 : (obsoletes) by division of URL
  V002 : GetFingerprintByTagOrder(response)
         by structural tag in html page, as HTML_STRUCT_TAG
  V003 : GetFingerprintByScript(response)
         by text length in tag after strip, as SCRIPT_STRUCT_TAG

C003   : Get eigenvalue from fingerprint
  V001 : GetEigenvalueInAll(strlist, otherlist)
         For pages with same parent <div> tag of continuous text, get eigenvalues longer than MIN_EIGENVALUE_LEN from fingerprint for these pages, which given in strlist. All eigenvalues must in every strlist, but not in any otherlist.
  V002 : GetFuzzyEigenvalue(string)
         by common eigenvalues in all fingerprint
  V003 :
         mix C003V001 and C003V002

C004   : Get TITLE and CONTENT and URL, from pages with eigenvalue in fingerprint

L001   : Get obvious list page
  V001 : Any page contain content page large than MIN_CONTENT_LEN

L002   : Get linked list page, via href in obvious list page

L003   : Get most frequency list page, by detect new content page appear

S001   : Output most frequency list page, by C001, C002, C003, L001, L002, L003
         This is a splider, only output list page, but not get CONTENT

S002   : Get TITLE and CONTENT by C004 from pages given by S001
         This is a splider, do major job
'''
from SauroAlgorithm import *

ALGORITHM = {
#	'GetURL'				       : [GetURLinResponse],
#	'GetURL'				      : GetURLinJSONFile,
	'GetObviousContent'		: GetContentByLength, 
	'GetPageFingerprint'	: [GetFingerprintByTagOrder, GetFingerprintByScript]
}