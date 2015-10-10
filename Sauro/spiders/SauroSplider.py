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
    return GenerateDictByAlgorithmList(response, algorithm['GetPageFingerprint'])

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
	    alljson = json.JSONDecoder().decode(f.read())
    totalresult = alljson[pTOTALRESULT]
    siteurl = 'stock.sohu.com'							# = alljson[pSITENAME/*'sitename'*/]
    returndict[rSITENAME] = siteurl
    for onealgo in algorithm['GetPageFingerprint']:
        returndict[onealgo.__name__] = GenerateEigenvalueFromList(totalresult, onealgo.__name__, algorithm['GenerateEigenvalue'])
# should write rule to json, have not do it yet
    return returndict

# part of S003V001
# IN  : response : input page
#     : eigenlist : Return by GenerateRuleViaJson, check eigenvalue both in dict and ALGORITHM
# OUT : return the div tag for GetGageItem, if not return []
def IsContentPage(response, eigenlist, algorithm = ALGORITHM):
    usedalgo = {}
    usedeigen = []
    usedalgo['GetPageFingerprint'] = usedeigen
# return result use the algorithm both in dict and ALGORITHM
    allreturn = []  
    for oneeigen in algorithm['GetPageFingerprint']:
        if oneeigen.__name__ in eigenlist:
            usedeigen.append(oneeigen)
    returnfinger = GetPageFingerprint(response, usedalgo)
    for oneeigen in usedeigen:
        onereturn = FingerprintHaveEigenvalue(returnfinger[oneeigen.__name__], eigenlist[oneeigen.__name__])
        for one in onereturn:
            if not one in allreturn:
                allreturn.append(one)
#    return RemoveDuplicateFromList(allreturn)
    return allreturn

# C004V001 : Get page items, from pages with eigenvalue in fingerprint
def GetPageItems(response, pagediv, algorithm = ALGORITHM):
    return GenerateDictByAlgorithmList(response, algorithm['GetPageItems'], pagediv)
    
####################################################################################################################################
# test function, generate script fingerprint
# not use now
def GenerateMoreFingerprint(fileread, filewrite):
    with open(fileread, 'rb') as f:
        totalresult = json.JSONDecoder().decode(f.read())
	for oneresult in totalresult[pTOTALRESULT]:
		del oneresult['fingerprint']
		if oneresult['url'] != '':
			oneresult.update(GetPageFingerprint(CreateSelectorbyURL(oneresult['url'])))
		else:
			oneresult.update(GetPageFingerprint(''))
	with open(filewrite, 'wb') as f:
		f.write(json.JSONEncoder().encode(totalresult))

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

notusedict = {
    "url": "http://stock.sohu.com/20150921/n421671505.shtml", "textdiv": ["<div itemprop=\"articleBody\">"], "GetFingerprintByScript": "L10772144819311255366710321310263112107771077573149112177115325492998456194148295117536657731531101541476491591321308081402115102892482611771831091511230160347121671434973552570261932471513713621041047518386832573242380255104897143133981036219159L", "GetFingerprintByTagOrder": "Ms9ds1ds3d2tds1d1s1d13sd13s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12dsM"
}
# pageattr as notusedict
def IsContentPageViaFingerprint(pageattr, eigendict, algorithm = ALGORITHM):
    allreturn = []
    for fingerprint in algorithm['GetPageFingerprint']:
        onereturn = FingerprintHaveEigenvalue(pageattr[fingerprint.__name__], eigendict[fingerprint.__name__])
        for one in onereturn:
            if not one in allreturn:
                allreturn.append(one)
    return allreturn
    
def IsContentPageViaFingerprint_2(pageattr, eigendict, algorithm = ALGORITHM):
#    tagreturn = FingerprintHaveEigenvalue(pageattr['GetFingerprintByTagOrder'], eigendict['GetFingerprintByTagOrder'])
    scriptreturn = FingerprintHaveEigenvalue(pageattr['GetFingerprintByScript'], eigendict['GetFingerprintByScript'])
    return scriptreturn    

def TestEigenViaJson(jsonread, jsonwrite, eigenlist, algorithm = ALGORITHM):
    returnpage = []
    with open(jsonread, 'rb') as f:
	    alljson = json.JSONDecoder().decode(f.read())
    totalresult = alljson[pTOTALRESULT]
    with open(jsonwrite, 'wb') as f:
        for onepageattr in totalresult:
            divlist = IsContentPageViaFingerprint_2(onepageattr, eigenlist, algorithm)
            if divlist:
                response = CreateSelectorbyURL(onepageattr['url'])
                pageitems = GetPageItems(response, divlist)
            #if not pageitems['GetContent']:
                f.write('URL:' + onepageattr['url'] + '\n')
                f.write('Title:' + pageitems['GetTitle'].encode('utf-8') + '\n')
                f.write('Content:' + pageitems['GetContent'].encode('utf-8') + '\n\n')
    return
    
def ReGenerateTextDiv(jsonread, jsonwrite):
    with open(jsonread, 'rb') as f:
	    alljson = json.JSONDecoder().decode(f.read())
    totalresult = alljson[pTOTALRESULT]
    for onepageattr in totalresult:
        if onepageattr['textdiv']:
            response = CreateSelectorbyURL(onepageattr['url'])
            onepageattr['textdiv'] = GetContentByLength(response)
    with open(jsonwrite, 'wb') as f:
        f.write(json.JSONEncoder().encode(alljson))

def DisplayTextDiv(jsonread):
    alltextdiv = {}
    with open(jsonread, 'rb') as f:
	    alljson = json.JSONDecoder().decode(f.read())
    totalresult = alljson[pTOTALRESULT]
    for onepageattr in totalresult:
        for onetextdiv in onepageattr['textdiv']:
            if not onetextdiv in alltextdiv:
                alltextdiv[onetextdiv] = 1
            else:
                alltextdiv[onetextdiv] += 1
    sorttextdiv = sorted(alltextdiv.items(), key=lambda d: d[0])
    for onediv in sorttextdiv:
        print onediv
        print '*' * 80
       
urllist = '''http://stock.sohu.com/20150910/n420784690.shtml
http://q.stock.sohu.com/news/cn/169/601169/4514377.shtml
http://stock.sohu.com/20141024/n405416109.shtml
http://q.stock.sohu.com/cn,gg,300237,2075096544.shtml
http://stock.sohu.com/
http://q.stock.sohu.com/jlp/analyst/info.up?analystCode=303005722
http://q.stock.sohu.com/app2/mpssTrade.up?code=300168&ed=&sd='''   # div miss match

testhtml = '''<script type="text/javascript">
var i='this is "<script> and \\' and </script + ">"and '
if (i < '<script //>') i = "<!-- /* & *//"
// this is comment </script>
/*  **
</script too> '.* 
//   //****/  (this will end)
else i = '</script>'
</script>this ok
<script some /></script>
<!---->asdf<!--->adsf-->
<!------ this is > < '-->' -->'''

testhtmlcomment = '''aaaa<script>
"this\ </script> \\' \\" </script> >' ** " cc
//c</script> adsf
</script>
bbbb'''

testagain = '''<script asdf>
i = "asdf <\\<" </script> right 
</script>" ok
'''

if __name__ == '__main__':
    filehandle = open('/home/raymon/security/Saurotest_1007-level2','wb')
    with open(const.LOG_FILE_L2_2, 'rb') as f:
	    alljson = json.JSONDecoder().decode(f.read())
    totalresult = alljson[pTOTALRESULT]
    for oneurl in totalresult:#[:30]:
#        raw = CreateRawbyURL('http://stock.sohu.com/20141024/n405416109.shtml')
        if oneurl['url']:
            raw = CreateRawbyURL(oneurl['url'])
            for onetext in ReturnLeveledDivText(raw, oneurl['url']):
                print onetext.encode('utf-8')
    print 'OK'
    
#    print GetContentByLength(CreateSelectorbyURL('http://q.stock.sohu.com/cn/000025/yjyg.shtml'))
#    print GetFingerprintByTagOrder(CreateSelectorbyURL('http://stock.sohu.com/20150910/n420784690.shtml'))
#    print GetEigenvalueInAll(testlist.split('\n'), otherlist)

#    print DivideByEigenvalue(eigen, testlist.split('\n'))
#    print GenerateEigenvalueFromJson(const.LOG_FILE_L2)
#    print GetPageFingerprint(CreateSelectorbyURL('http://q.stock.sohu.com/cn/300108/xjll.shtml'))

#    GenerateMoreFingerprint('/home/raymon/security/Saurolog_0922-level2', '/home/raymon/security/Saurolog_1004-level2')
    #GenerateMoreFingerprint('/home/raymon/security/SauroTest', '/home/raymon/security/SauroWrite')

#	 print GenerateEigenvalueFromJson(const.LOG_FILE_L2_1, 'GetFingerprintByScript', GetEigenvalueInAll)
#	 print GenerateRuleViaJson(const.LOG_FILE_L2_1, None)		# now for eigenvalue

#    print GenerateEigenvalueFromJson(const.LOG_FILE_L2_1, 'GetFingerprintByScript', GetEigenvalueInAll)
#    print GetTextInTag(CreateSelectorbyURL('http://stock.sohu.com/20150910/n420784690.shtml'), eigenlist, excludetaglist)
    
#    title = GetTitleByTag(CreateSelectorbyURL('http://stock.sohu.com/20150910/n420784690.shtml'), None)
#    print title.encode('utf-8')
#    GetContentByDiv(CreateSelectorbyURL('http://stock.sohu.com/20150910/n420784690.shtml'),['<div itemprop="articleBody">'])

#    ReGenerateTextDiv(const.LOG_FILE_L2_2, const.FINGER_FILE_L2)
#    DisplayTextDiv(const.FINGER_FILE_L2)

##    returndict = GenerateRuleViaJson(const.LOG_FILE_L2_1, None)
##    response = CreateSelectorbyURL('http://stock.sohu.com/20150910/n420784690.shtml')
##    pagediv = IsContentPage(response, returndict)
##    if pagediv:
##        pageitems = GetPageItems(response, pagediv)
##        for oneitem in pageitems.keys():
##            print oneitem, pageitems[oneitem].encode('utf-8')

##    eigenlist = GenerateRuleViaJson(const.LOG_FILE_L2_2, None)
##    returndict = TestEigenViaJson(const.LOG_FILE_L2_2, const.TEST_FILE_L2_2, eigenlist)

def notuse():
    filehandle = open('/home/raymon/security/Saurotest_1007-level2','wb')
    with open(const.LOG_FILE_L2_2, 'rb') as f:
	    alljson = json.JSONDecoder().decode(f.read())
    totalresult = alljson[pTOTALRESULT]
    filehandle.close()
    print 'OK'

    raw = CreateRawbyURL('http://stock.sohu.com/20150910/n420784690.shtml')
    with open('/home/raymon/security/raw', 'wb') as f:
        f.write(raw.encode('utf-8'))
    response = CreateSelectorbyString(raw)
    raw2 = response.extract()
    with open('/home/raymon/security/raw2', 'wb') as f:
        f.write(raw2.encode('utf-8'))    