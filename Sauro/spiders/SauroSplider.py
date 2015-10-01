# -*- coding:gbk -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
#
# Wrapping Column 132.

from SauroCommon import *
from SauroAlgorithm import *
from SauroSetting import *

# use algorithm in GetPageFingerprint
# return dict of all kinds of fingerprint
def GetPageFingerprint(response, algorithm = ALGORITHM):
	returndict = {}
	if response:
		for onealgo in algorithm['GetPageFingerprint']:
			returndict[onealgo.__name__] = onealgo(response)
	else:
		for onealgo in algorithm['GetPageFingerprint']:
			returndict[onealgo.__name__] = ''
	return returndict

# part of S002V001
def GenerateEigenvalueFromList(resultlist, fingerprint, algroithm):
    eigendictdict = {}
    returndict = {}
    for oneresult in resultlist:
        divnumber = len(oneresult[pTEXTDIV])
# in json format, there are multi div with same value, but only one need 
        if divnumber > 1:
            nodup = RemoveDuplicateFromList(oneresult[pTEXTDIV])
            for onenodup in nodup:
                IncreaseDictDictCount(eigendictdict, onenodup, oneresult[fingerprint])
# only one div exist, use it directly
        elif divnumber == 1:
            IncreaseDictDictCount(eigendictdict, oneresult[pTEXTDIV][0], oneresult[fingerprint])
# now eigendictdict counted the obvious content page group by div and fingerprint
    resultnuber = len(resultlist)
    for eigendict in eigendictdict.keys():
        if resultnuber / SumDictCount(eigendictdict[eigendict]) < const.OBVIOUS_PAGE_SCALE:
            #onelist = GetEigenvalueInAll(eigendictdict[eigendict].keys())
            onelist = algroithm(eigendictdict[eigendict].keys())        # change to function pointer
            if onelist:
                returndict[eigendict] = onelist
    return returndict

# S002V001 : Generate rules for sites from json
# IN  : JSON file for every page with url and fingerprint in one site
# OUT : JSON (maybe file) for rule of this site, nwo fnish eigenvalue
def GenerateRuleViaJson(jsonread, jsonwrite, algorithm = ALGORITHM):
    returndict = {}
    with open(jsonread, 'rb') as f:
	    alljson = JSONDecoder().decode(f.read())
    totalresult = alljson[pTOTALRESULT]
    siteurl = 'stock.sohu.com'							# = alljson[pSITENAME/*'sitename'*/]
    returndict[rSITENAME] = siteurl
    for onealgo in algorithm['GetPageFingerprint']:
        returndict[onealgo.__name__] = GenerateEigenvalueFromList(totalresult, onealgo.__name__, algorithm['GenerateEigenvalue'])
    return returndict

# part of S003V001
# IN  : response : input page
#     : eigendict : Return by GenerateRuleViaJson, check eigenvalue both in dict and ALGORITHM
def IsContentPage(response, eigendict, algorithm = ALGORITHM):
    usedalgo = {}
    usedeigen = []
    usedalgo['GetPageFingerprint'] = usedeigen
# return result use the algorithm both in dict and ALGORITHM    
    for oneeigen in algorithm['GetPageFingerprint']:
        if oneeigen.__name__ in eigendict:
            usedeigen.append(oneeigen)
    returnfinger = GetPageFingerprint(response, usedalgo)
    
    for oneeigen in usedeigen:
        allreturn = FingerprintHaveEigenvalue(returnfinger[oneeigen.__name__], eigendict[oneeigen.__name__])
        
    print RemoveDuplicateFromList(allreturn)

# test function, generate script fingerprint
# not use now
def GenerateMoreFingerprint(fileread, filewrite):
    with open(fileread, 'rb') as f:
        totalresult = JSONDecoder().decode(f.read())
	for oneresult in totalresult[pTOTALRESULT]:
		del oneresult['fingerprint']
		if oneresult['url'] != '':
			oneresult.update(GetPageFingerprint(CreateSelectorbyURL(oneresult['url'])))
		else:
			oneresult.update(GetPageFingerprint(''))
	with open(filewrite, 'wb') as f:
		f.write(JSONEncoder().encode(totalresult))

testlist = '''Ms9ds1ds3d2tds1d1s1d12s2d7sd2td9s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d12s2d7sd2td5s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd18s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd18s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd15s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd8sd4s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd13s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd9td4s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd14s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd10sd4s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd10td4s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms8ds1ds3d2tds1d1s1d13sd9tdtd5s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd9td6s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd15s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd17s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd12sd4s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd17s2d1sd1s10ds2d9s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12ds
Ms9ds1ds3d2tds1d1s1d13sd13s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sd7sd61tdsd18sdsd4s3d2s12ds
srgtryy6uiyuiyuopopp980987iouyiyl
dtwer346ti
rdtgtu7iigjhgjy
s1d2fds1dtds2d2tds1d2sdadsragdgtdsd18sdsd4s3d2s12ds'''

otherlist = ['afdsatdsd18sdsd4s3s1d2fds1dtds2d2tds1d2sdd2s12dsafdsrewr','aserghgfhthtr']
eigen = ['ds1ds3d2tds1d1s1d1', 's1d2fds1dtds2d2tds1d2sd', 'tdsd18sdsd4s3d2s12ds']

if __name__ == '__main__':
#    print GetContentByLength(CreateSelectorbyURL('http://q.stock.sohu.com/cn/000025/yjyg.shtml'))
#    print GetFingerprintByTagOrder(CreateSelectorbyURL('http://stock.sohu.com/20150910/n420784690.shtml'))
#    print GetEigenvalueInAll(testlist.split('\n'), otherlist)
#    print DivideByEigenvalue(eigen, testlist.split('\n'))
#    print GenerateEigenvalueFromJson(const.LOG_FILE_L2)
#    print GetPageFingerprint(CreateSelectorbyURL('http://stock.sohu.com/20150910/n420784690.shtml'))
#	 GenerateMoreFingerprint('/home/raymon/security/Saurolog_0922-level2', '/home/raymon/security/Saurolog_0930-level2')
#    GenerateMoreFingerprint('/home/raymon/security/SauroTest', '/home/raymon/security/SauroWrite')
#	print GenerateEigenvalueFromJson(const.LOG_FILE_L2_1, 'GetFingerprintByScript', GetEigenvalueInAll)
#	print GenerateRuleViaJson(const.LOG_FILE_L2_1, None)		# now for eigenvalue
    returndict = GenerateRuleViaJson(const.LOG_FILE_L2_1, None)
    IsContentPage(CreateSelectorbyURL('http://stock.sohu.com/20150910/n420784690.shtml'), returndict)