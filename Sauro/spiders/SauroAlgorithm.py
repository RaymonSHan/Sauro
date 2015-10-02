# -*- coding:gbk -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
#
# Wrapping Column 132.

from SauroCommon import *

const.MIN_TEXT_LEN             = 180
const.MIN_EIGENVALUE_LEN       = 16

# if a kind of fingerprint is too few, omit it, althought it contain long text
# for my sample with 69626 page, if the kind number less 69626/500 = 139, omit it
# analysis my sample, the number less 47 should omit, greater 669 should remain, so SCALE can be 104 - 1481
# this value is associate with MIN_TEXT_LEN
const.OBVIOUS_PAGE_SCALE       = 500

const.HTML_STRUCT_TAG         = '//div[@*] | //table[@*] | //form[@*] | //script[@*] | //style[@*]'
#const.HTML_STRUCT_TAG          = '//div | //table | //form | //script | //style'
const.SCRIPT_STRUCT_TAG        = '//script | //style'

const.PAGE_HOME                = '/home/raymon/security/pages_0922-level2/'
const.LOG_FILE_L2              = '/home/raymon/security/Saurolog_0922-level2'
const.LOG_FILE_L2_1            = '/home/raymon/security/Saurolog_0930-level2'
const.LOG_FILE_L3              = '/home/raymon/security/Saurolog_0923-level3'

# C001V001 : Get obvious content page
# IN  : Selector object, such as Response
# OUT : List of <div> tag, which contain text longer than MIN_TEXT_LEN
def GetContentByLength(response):
    textdict = []
# the <script> and <style> and <a> tag are not useful
    for onetag in response.xpath('//*[not(name()="script") and not(name()="style") and not(name()="a")]'):
# the text not displayed is not useful, may add more exclude judge here
        if onetag.xpath('ancestor-or-self::*[@style="display:none"]'):
            continue
        for onetext in onetag.xpath('text()'):
            textlen = len(onetext.extract().strip())
            if textlen > const.MIN_TEXT_LEN:
                try:
# add most near <div> tag into return, and given default value
                    fulldiv = onetag.xpath('ancestor-or-self::div[1]').extract()[0]
                    onlydiv = fulldiv[0 : fulldiv.find('>')+1]
                except IndexError:
                    onlydiv = 'NoDiv'
                if onlydiv not in textdict:
                    textdict.append(onlydiv)
    return textdict

# C002V002 : Get fingerprint of given page
# IN  : Selector object, such as Response
# OUT : string of page fingerprint
#
# the sequence <script><div><div><div><table><table><div><script><script> return MSD2T1DS1M
def GetFingerprintByTagOrder(response, otherpara):
    lastname = ''
    thisname = ''
    lastnum = 0
    returnfinger = 'M'
    for onetag in response.xpath(const.HTML_STRUCT_TAG).extract():
# onetag start with '<', thisname is d,t,f,s
        thisname = onetag[1:2]
        if lastname == thisname:
            lastnum += 1
        else:
            returnfinger += lastname
            if lastnum != 0:
                returnfinger += str(lastnum)
                lastnum = 0
            lastname = thisname
    returnfinger += lastname
    if lastnum != 0:
        returnfinger += str(lastnum)
# the head and tail are 'M'
    returnfinger += 'M'
    return returnfinger

# C002V003 : Get fingerprint of given page
# IN  : Selector object, such as Response
# OUT : string of page fingerprint
#
# return the length for tag in SCRIPT_STRUCT_TAG
def GetFingerprintByScript(response, otherpara):
    returnfinger = 'L'
    for onetag in response.xpath(const.SCRIPT_STRUCT_TAG):
        returnfinger += str(len(onetag.extract().strip()))
    returnfinger += 'L'
    return returnfinger

# C003V001 : Get eigenvalue from fingerprint
# IN  : strlist[]   : List of fingerprint to generate eigenvalue
#       otherlist[] : List of fingerprint must not contain eigenvalue
# OUT : List of eigenvalue, should longer than MIN_EIGENVALUE_LEN
def GetEigenvalueInAll(strlist, otherlist = []):
    firststr = strlist[0]
    returnlist = []
    beginpos = 0
    endpos = const.MIN_EIGENVALUE_LEN
    lastpos = len(firststr)
    havechecked = 0
    misshit = 0
    while endpos <= lastpos + 1:
# the +1 in above while and following if, are smart condition for last match at end
        if endpos > lastpos:
            misshit = 1
        else:
            checkstr = firststr[beginpos:endpos]
            misshit = 0
            for descstr in strlist:
                if descstr.find(checkstr) == -1:
# the eigenvalue must in ervery strlist, any miss will break check
                    misshit = 1
                    break
        if misshit == 1:
            if havechecked == 1:
# here means, had find shorter eigenvalue before, but now it miss. 
# So should add the shorter one as eigenvalue
                maybekey = firststr[beginpos:endpos-1]
# althought it not happened, returnlist have no duplicate
                if InSubstring(maybekey, otherlist) == -1 and InSubstring(maybekey, returnlist) == -1:
                    returnlist.append(maybekey)
                beginpos = endpos
                endpos = beginpos + const.MIN_EIGENVALUE_LEN
                havechecked = 0
            else:
# not found, goon step
                beginpos += 1
                endpos += 1
        else:
# this is eigenvalue, but may have longer, mark it and add later
# of course, endpos can increase more than one. may optimize later
            havechecked = 1
            endpos += 1
    return returnlist

# return title by <title> tag of response
def GetTitleByTag(response, otherpara):
    return response.xpath('//title/text()')[0].extract()

# otherpara is List of div part
# used Oct. 01 '15
def GetContentByDiv(response, otherpara):
    returnstring = ''
    rawhtml = response.xpath('//div[@itemprop="articleBody"]')[0].extract()
    rawhtml = rawhtml.replace('\n', '').replace('\r', '').replace('</p>', '').replace('<p>', '\r\n').replace('<br />', '\r\n')

    
    responseindiv = CreateSelectorbyString(rawhtml)
    print responseindiv.extract()
    return
    for onetext in responseindiv.xpath('text()'):
        returnstring += onetext.extract()
    print returnstring.encode('utf-8');       
    
    return
    
    
    
# this is ok #######################################################################################################################
    for onetext in response.xpath('//div[@itemprop="articleBody"]/text() | //div[@itemprop="articleBody"]/*[not(name()="div")]/descendant-or-self::text()'):
        returnstring += onetext.extract()
    print returnstring.encode('utf-8');
# this is ok #######################################################################################################################
    return onetext
    
    
#        for sel in response.xpath('//div[@class="muLink"]/parent::*'):
#            print sel.extract().encode('utf-8')
#            print ('-' * 20)
        #article = articleList.xpath('string(./p)')[0]
        #sel = articleList.xpath('string(//p)')
        #print article.extract().encode('utf-8')
        #for sel in articleList.xpath('string(//p)'):
        #    print sel.extract()
        #print articleList[0].extract()

#         for article in response.xpath('//div[@itemprop="articleBody"]/descendant-or-self::*[not(@class="muLink")]'):
# ancestor

#        for article in response.xpath('//div[@itemprop="articleBody"]//text()'):
#        for article in response.xpath('//div[@itemprop="articleBody"]/descendant-or-self::text()'):

#        articleList = response.xpath('//div[@itemprop="articleBody"]')
#        article = articleList.xpath('string(.)')[0].extract()
#        print article.encode('utf-8')

#        for article in response.xpath('//div[@itemprop="articleBody"]/*[not(name()="div")]/descendant-or-self::text()'):         // no direct, no div
#        for article in response.xpath('//div[@itemprop="articleBody"]/descendant-or-self::*[not(@class="muLink")]/text()'):      // all
#        for article in response.xpath('string(//div[@itemprop="articleBody"])'):                                                 // all
#        for article in response.xpath('//div[@itemprop="articleBody"]/text() | //div[@itemprop="articleBody"]/*[not(name()="div")]/descendant-or-self::text()'):    // OK\


#        for article in response.xpath('//div[@itemprop="articleBody"]/not(descendant-or-self::*(@class="muLink"))'):     *[@class="muLink"]
#        for article in response.xpath('string(//div[@itemprop="articleBody"]/p[2])'):
    
####################################################################################################################################
# select fingerprint with all eigenvalues
# test use, only in test result in list
def CollectPageFromEigenvalue(resultlist, eigendict, fingerprint):
    returndict = {}
    for onediv in eigendict.keys():
        returndict[onediv] = {}
        eigencount = len(eigendict[onediv])
        for oneresult in resultlist:
            hitcount = 0
            for oneeigen in eigendict[onediv]:
                if oneresult[fingerprint].find(oneeigen) != -1:
                    hitcount += 1
            if hitcount == eigencount:
                IncreaseDictDictCount(returndict, onediv, oneresult[fingerprint])
            elif hitcount != 0:
                pass
                #print 'PART match', onediv, oneresult['fingerprint'], oneeigen
    return returndict 

# Generate eigenvalue from given json file, the 'fingerprint' may be others
# follow C001V001, C002V002, C003V001, only for test, no try except control
# IN  : json filename, format as following
# OUT : dict of eigenvalues stringlist, group by <div> tag
# test use, for test function via json file
'''
{
    "totalresult": [
        {
            "url": "http://q.stock.sohu.com/cn/601985/index.shtml",
            "fingerprint": "Ms1d2fd8tdtd2tdtd2tdtd5tdtdtd7t1d2td3td18sd2td14t2d4td10td1td19sd2td19td2td2td1t1sd3tdtd1s7M",
            "textdiv": []
        },
        {
            "url": "http://stock.sohu.com/20150922/n421792573.shtml",
            "fingerprint": "Ms9ds1ds3d2tds1d1s1d13sd17s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12dsM",
            "textdiv": [
                "<div itemprop=\"articleBody\">",
                "<div itemprop=\"articleBody\">"
            ]
        },
        {
            "url": "http://stock.sohu.com/20150922/n421792716.shtml",
            "fingerprint": "Ms9ds1ds3d2tds1d1s1d13sd17s2d3sd1s10ds2d10s1d2fds1dtds2d2tds1d2sds1d10s1d2tdsd18sdsd4s3d2s12dsM",
            "textdiv": [
                "<div itemprop=\"articleBody\">"
            ]
        },
        {
            "url": "",
            "fingerprint": "",
            "textdiv": []
        }
    ]
}
'''
# NOT use now, use GenerateRuleViaJson
def GenerateEigenvalueFromJson(filename, fingerprint, algroithm):
    with open(filename, 'rb') as f:
        totalresult = JSONDecoder().decode(f.read())[pTOTALRESULT]
    eigendict = GenerateEigenvalueFromList(totalresult, fingerprint, algroithm)
#    print eigendict
    pagedict = CollectPageFromEigenvalue(totalresult, eigendict, fingerprint)
    for onepage in pagedict.keys():
        print onepage, len(pagedict[onepage]), SumDictCount(pagedict[onepage])
    return 0



# ReturnTextDiv -> GetContentByLength
# ReturnStamp -> GetFingerprintByTagOrder
# MINSTAMP -> MIN_EIGENVALUE_LEN
# ReturnStampKey


const.FILE_HOME = '/home/raymon/security/pages/00/'




def ReturnExpr(responseurl):
    spliturl = responseurl.split('/')
    retstr = 'S'
    for onesp in spliturl:
        splen = len(onesp)
        if splen > 9:
            retstr += '-'
        if splen > 0:
            retstr += str(splen)
    return retstr



def GetSingleDiv(onediv):           # not pass yet
    alllength = len(onediv.extract())

    for alldiv in onediv.xpath('div'):
        alllength -= len(alldiv.extract())
    for alltext in onediv.xpath('text() | *[not(name()="div")]/descendant-or-self::text()'):
        exttext = alltext.extract()
        textlen = len(exttext)
    return alllength, textlen, exttext

def OpenPathFile(filename, retry=0, rw='wb'):        # create dirs and file
    if retry >= 2:
        return False
    try:
        opfile = open(filename, rw)
    except IOError as exc:
        if exc.errno == errno.ENOENT:       # 2 : No such file or directory
            try:
                os.makedirs(os.path.split(filename)[0])
            except OSError:
                return False
            return OpenPathFile(filename, retry+1, rw)
    return opfile
    
def SaveResponse(response):
    returnval = True
    savefile = OpenMD5File(response.url)
    if savefile == False:
        return False
    try:
        savefile.write(response.url)
        savefile.write('\n\n')
        savefile.write(response.body)
    except:
        returnval = False
    savefile.close()
    return returnval

# find in files with subpath
def iterfindfiles(path, fnexp):
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, fnexp):
            yield os.path.join(root, filename)

# union two dict and add value for same key
def UnionAddDict(origin, added):
    for k in added.keys():
        if k in origin.keys():
            origin[k] += added[k]
        else:
            origin[k] = added[k]

# remove given substr, and return remain list
# length of remain list must larger or equal minlen
# may not use yet
def RemoveSubstr(origin, sublist, minlen = const.MIN_EIGENVALUE_LEN):
    outputstr = []
    originlen = len(origin) + 1
    remainstr = dict.fromkeys(range(originlen), 1)
    remainstr[originlen-1] = 0                      # mark end for finish
    for onesub in sublist:
        findstart = origin.find(onesub)
        while findstart != -1:
            findend = findstart + len(onesub)
            for fkey in range(findstart, findend):
                remainstr[fkey] = 0
            findstart = origin.find(onesub, findend)
           
    remainstart = 0
    remainend = 0
    inremain = 0
    for remainkey in range(originlen):       
        if inremain == 0 and remainstr[remainkey] != 0:       # begin record
            remainstart = remainkey
            inremain = 1
        if inremain != 0 and remainstr[remainkey] == 0:       # record end, output
            remainend = remainkey
            inremain = 0
            if remainend - remainstart > minlen:
                outputstr.append(origin[remainstart:remainend])
    return outputstr
    
def MatchKeys(origin, returnlist):
    originlen = len(origin)
    remainstr = dict.fromkeys(range(originlen), 1)
    for onekey in returnlist:
        findstart = origin.find(onekey)
        while findstart != -1:
            findend = findstart + len(onekey)
            for fkey in range(findstart, findend):
                remainstr[fkey] = 0
            findstart = origin.find(onekey, findend)
    returnval = 0
    for oneremain in remainstr:
        if remainstr[oneremain] == 1:
            returnval += 1
    return returnval
    
def ReturnProbabilityStampKey(dictstr):
    returnlist = {}
    notFirstSearch = False
    for searchstr in dictstr.keys():
        beginpos = 0
        lastpos = len(searchstr)
        havechecked = 0
        endpos = const.MINSTAMP
        endhit = dict.fromkeys(range(len(searchstr) + 1), 1)        # record the max size
        
        while beginpos <= lastpos - const.MINSTAMP:
            endpos = beginpos + const.MINSTAMP
            lasthit = 0
            while endpos <= lastpos:
                checkstr = searchstr[beginpos:endpos]
                if notFirstSearch and inSubstring(checkstr, returnlist) == 0:
                    endpos += 1
                    continue                                        # this substring have checked, may be changed later
                    
                #print 'checkstr in mainloop =', checkstr
                checkhit = 0
                for descstr in dictstr.keys():
                    if descstr.find(checkstr) != -1:
                        checkhit += dictstr[descstr]

                if lasthit == checkhit:                             # 1234x is found, 1234 can be delete
                    del returnlist[checkstr[:-1]]
                lasthit = checkhit
                                    
                if checkhit > endhit[endpos]:
                    endhit[endpos] = checkhit
                    if checkhit == 1:                       # only found in itself, no more necessary
                        endpos = lastpos + 1
                    else:
                        returnlist[checkstr] = checkhit
                        endpos += 1
                else:                                       # string with more ahead have checked
                    endpos = lastpos + 1
            beginpos += 1
        notFirstSearch = True
    return returnlist

def ReturnStringWithSub(substring, totalstring):            # totalstring is {}
    returnstring = []
    returnnumber = 0
    for onestring in totalstring.keys():
        if onestring.find(substring) != -1:
            returnstring.append(onestring)
            returnnumber += totalstring[onestring]
    return returnstring, returnnumber
            
def ReturnStringMaxLenght(totalstring):                     # totalstring is []
    maxlength = 0
    for onestring in totalstring:
        onelen = len(onestring)
        if onelen > maxlength:
            maxlength = onelen
    return maxlength
    
def ReturnStringMinLenght(totalstring):                     # totalstring is []
    minlength = 999999
    for onestring in totalstring:
        onelen = len(onestring)
        if onelen < minlength:
            minlength = onelen
    return minlength
    
def ReturnStringTotalLenght(totalstring):                   # totalstring is []
    totallength = 0
    for onestring in totalstring:
        totallength += len(onestring)
    return totallength    


const.JAVAFUNC = 'javafunc'
const.HREFFUNC = 'hreffunc'
const.FUNCHEAD = 'function main(splash) '
const.MAX_CRAWL_LEVEL = 2
const.HOST = 'http://stock.sohu.com/'
const.ALLOW = 'stock.sohu.com'

def DefineStart():
    return const.FUNCHEAD

def DefineFunction(fname, fscript):
    return 'local ' + fname + ' = splash:jsfunc([[ function (){' + fscript + '} ]]) '

def DefineJavaScript(script):
    return DefineFunction(const.JAVAFUNC, script)

def DefineLocation():
    script = 'var ishref = document.location.href; return ishref;'
    return DefineFunction(const.HREFFUNC, script)

def DefineSplashGo(script):
    return 'splash:go(\"' + script + '\") '

def DefineAssign(vname, fname=None):
    if fname == None:
        return vname + '=' + vname + '() '
    else:
        return vname + '=' + fname + '() '

def DefineWait(waittime):
    return 'splash:wait(' + str(waittime) + ') '

def DefineProcess(waittime):
    return DefineWait(waittime) + DefineAssign(const.JAVAFUNC) + DefineWait(waittime) + DefineAssign(const.HREFFUNC)

def DefineEnd():
    return 'return {getreturn=' + const.HREFFUNC + '} end '

def DefineMeta(func):
    return {
        'splash': {
            'args': {'lua_source': func},
            'endpoint': 'execute'
        }
    }

#from Sauro.items import SauroScriptItem

# total number : 7955, with textdiv : 1206
# total stamp : 623, with textdiv : 145, without 534, while 56 in both condition

class SauroReadSpider(scrapy.Spider):
    name = 'SauroRead'
    allowed_domains = [const.ALLOW]
    start_urls = [const.HOST]
    jsoncontent = None
    logfile = None
    
    def parse(self, response):
        allrule = {}
        allrule['stock.sohu.com'] = []
        self.logfile = open(const.LOG_FILE, 'rb')
        urllist = JSONDecoder().decode(self.logfile.read())['totalresult']
        self.logfile.close()   

        stamphave = {}
        stampnothave = {}
        minrate = 0.0
        maxrate = 0.0
        
        for oneurl in urllist:
            if len(oneurl['textdiv']) != 0:
                try:
                    stamphave[oneurl['stamp']] = 1
                except KeyError:
                    stamphave[oneurl['stamp']] = 1
            else:
                try:
                    stampnothave[oneurl['stamp']] = 1
                except KeyError:
                    stampnothave[oneurl['stamp']] = 1
                    
        for loops in range(20):
            subkey = ReturnProbabilityStampKey(stamphave)
            if len(subkey) < 1:
                break
            sortkey = sorted(subkey.items(), key=lambda d: len(d[0])*d[1]*d[1], reverse=True)
            onekey, number = sortkey[0]                 # get the most subkey
        
            simstring, returnnumber = ReturnStringWithSub(onekey, stamphave)
            realkey = ReturnStampKey(simstring, None)
            allrule['stock.sohu.com'].append(realkey)
            
            
            
            
            print realkey, returnnumber
            for onestr in simstring:
                del stamphave[onestr]
                
        return
        print allrule['stock.sohu.com']
        
        totalnumber = 0
        for oneurl in urllist:
            if IsContentPage(oneurl['stamp'], allrule['stock.sohu.com']):
                totalnumber += 1
                print oneurl['url'], oneurl['stamp']
        print totalnumber
        return           
            
            
        maxlength = ReturnStringMaxLenght(simstring)
        minlength = ReturnStringMinLenght(simstring)
        totallength = ReturnStringTotalLenght(realkey)
        print 'maxlength=', maxlength
        print 'minlength=', minlength
        print 'totallength=', totallength
        maxrate = float(totallength) / maxlength
        minrate = float(totallength) / minlength
        print minrate, maxrate
        print realkey
        

        
        for (onekey, number) in sortkey:
            print onekey, number, len(onekey)*number*number
        return                   
                    
        for oneurl in urllist:
            textdivlist = oneurl['textdiv']
            if len(textdivlist) != 0:
                textdiv = textdivlist[0]
                if not (textdiv in stamphave.keys()):
                    stamphave[textdiv] = []
                if not (oneurl['stamp'] in stamphave[textdiv]):
                    stamphave[textdiv].append(oneurl['stamp'])

        subkey = ReturnProbabilityStampKey(stamphave)
        sortkey = sorted(subkey.items(), key=lambda d: len(d[0])*d[1], reverse=False)
        for (onekey, number) in sortkey:
            print onekey, number
        return
                    
       
        
        
        
        
        
        
        for oneurl in urllist:
            if len(oneurl['textdiv']) != 0:
                try:
                    stamphave[oneurl['stamp']] = 1
                except KeyError:
                    stamphave[oneurl['stamp']] = 1
            else:
                try:
                    stampnothave[oneurl['stamp']] = 1
                except KeyError:
                    stampnothave[oneurl['stamp']] = 1
        sortstamp = sorted(stamphave.items(), key=lambda d: d[0], reverse=False)
        for (onekey, number) in sortstamp:
            print onekey, number
        return     
                

        
        for onediv in stamphave:
            sortdiv = sorted(stamphave[onediv], key=lambda d: d[0], reverse=False)
            print onediv
            for onestamp in sortdiv:
                print onestamp
        return
    
class SauroScriptSpider(scrapy.Spider):
    name = 'SauroSite'
    allowed_domains = [const.ALLOW]
    start_urls = [const.HOST]
    #start_urls = ["http://stock.sohu.com/stock_scrollnews_152.shtml"]
    #start_urls = ["http://stock.sohu.com/20150914/n421098148.shtml"]
    #start_urls = ["http://stock.sohu.com/20150915/n421130868.shtml"]

    mydict = {}
    alltextdict = {}
    loghandle = None
        
    #def parse_stampkey(self, response):
    #    strlist = sttry.split()
    #    print ReturnStampKey(strlist, None)

    def __init__(self):
        dispatcher.connect(self.initialize, signals.engine_started)
        dispatcher.connect(self.finalize, signals.engine_stopped)

    def parse_readfile(self, response):
        for pathfilename in iterfindfiles(const.FILE_HOME, '*'):
            #filesize = os.path.getsize(pathfilename)
            handle = open(pathfilename, 'rb')
            sel = Selector(text=handle.read(), type="html")
            handle.close()
            filename = os.path.split(pathfilename)[1]
            returl = ReturnStamp(sel)
            try:
                self.mydict[returl].append(filename)
            except KeyError:
                self.mydict[returl] = []
                self.mydict[returl].append(filename)
                
            textdict = ReturnTextDiv(sel)
            for onlydiv in textdict:
                divnum = textdict[onlydiv]
                try:
                    self.alltextdict[onlydiv][returl] += divnum
                    self.alltextdict[onlydiv]['TOTAL'] += divnum
                except KeyError:
                    try:
                        self.alltextdict[onlydiv][returl] = divnum
                        self.alltextdict[onlydiv]['TOTAL'] += divnum
                    except KeyError:
                        self.alltextdict[onlydiv] = {}
                        self.alltextdict[onlydiv][returl] = divnum
                        self.alltextdict[onlydiv]['TOTAL'] = divnum

    def initialize(self):
        self.logfile = open(const.LOG_FILE, 'wb')
        self.logfile.write('{\"totalresult\":[\n')
 
    def finalize(self):
        self.logfile.write('{"url":"", "stamp":"", "textdiv":[]}]}')
        self.logfile.close()
 
    def parse(self, response):
        jsoncontent = json.loads(self.logfile.read())
        print jsoncontent["totalresult"]
        
    def finalize_notuse_3(self):
        handle = open(const.LOG_FILE, 'wb')
        sortdict = sorted(self.alltextdict.items(), key=lambda d: d[1]['TOTAL'], reverse=True)
        for (pdiv, urlmap) in sortdict:
            handle.write(pdiv)
            handle.write(' ')
            handle.write(str(urlmap['TOTAL']))
            handle.write('\n')
            for onemap in urlmap:
                if onemap != 'TOTAL':
                    handle.write(onemap)
                    handle.write(' ')
                    handle.write(str(urlmap[onemap]))
                    handle.write(' ')
                    handle.write(str(len(self.mydict[onemap])))
                    handle.write(' ')
                    handle.write(self.mydict[onemap][0])
                    handle.write('\n')
                    #print onemap, urlmap[onemap], len(self.mydict[onemap]), self.mydict[onemap][0]
        #sorturl = sorted(self.mydict.items(), key=lambda d: len(d[1]), reverse=True)
        #for (purl, urls) in sorturl:
        #    print purl, urls[0]
        #handle.close()

    def finalize_notuse_2(self):
        for pdiv in self.alltextdict:
            for urlmap in self.alltextdict[pdiv]:
                print pdiv, urlmap, self.alltextdict[pdiv][urlmap]
    
    def finalize_notuse_1(self):
        sortdict = sorted(self.mydict.items(), key=lambda d: len(d[1]), reverse=True)
        for (urlmap, urllist) in sortdict:
            try:
                urldictlen = len(self.alltextdict[urlmap])
            except KeyError:
                urldictlen = 0
            if urldictlen > 0:
                print urlmap + '  ' + str(len(urllist))
                for pdiv in self.alltextdict[urlmap]:
                    print "Mydict[%s] =" % pdiv, self.alltextdict[urlmap][pdiv]
                print '-' * 60

    def parse_text(self, response, crawllevel, order, loopstr):
        #SaveResponse(response)
        nowlevel = crawllevel + 1
        nowloopstr = loopstr + str(crawllevel) + ' ' + str(order) + ':   ' 
        print nowloopstr
        returl = ReturnStamp(response)
        textdict = ReturnTextDiv(response)
        result = {"url":response.url, "stamp":returl, "textdiv":textdict}
        self.logfile.write(json.dumps(result))
        self.logfile.write(',\n')

        if crawllevel <= const.MAX_CRAWL_LEVEL:
            lx = SgmlLinkExtractor()
            urls = lx.extract_links(response)
            noworder = 0
            for oneurl in urls:
                noworder += 1
                yield scrapy.Request(oneurl.url, callback=lambda response, crawllevel=nowlevel, order=noworder, loopstr=nowloopstr: self.parse_text(response, crawllevel, order, loopstr))
                # in lambda is val para, in call() is ref para, VERY IMPORTANT !!!
                
    def parse_testfile(self, response):
        lx = SgmlLinkExtractor()
        urls = lx.extract_links(response)
        readed = 0
        notreaded = 0
        for oneurl in urls:
            handle = OpenMD5File(oneurl.url, 'rb')
            if handle == False:
                notreaded += 1
            else:
                readed += 1
                handle.close()
        print readed, notreaded

    def parse(self, response):    # changed to parse to crawl all home page
        lx = SgmlLinkExtractor()
        urls = lx.extract_links(response)
        noworder = 0
        for oneurl in urls:
            noworder += 1
            yield scrapy.Request(oneurl.url, callback=lambda response, crawllevel=1, order=noworder, loopstr='': self.parse_text(response, crawllevel, order, loopstr))

    def parse_href(self, response):
        hrefList = response.xpath('//a[starts-with(@onclick,"javascript:")]')
        for onehref in hrefList:
            for onescript in onehref.xpath('@onclick').extract():
                onefunc = DefineStart()
                onefunc += DefineFunction(const.JAVAFUNC, onescript[11:])
                hrefval = onehref.xpath('@href')[0].extract()
                if hrefval == '#':
                    onefunc += DefineLocation()
                elif hrefval == '###':
                    onefunc += DefineLocation()
                else:
                    onefunc += DefineLocation()
                onefunc += DefineSplashGo(response.url)
                onefunc += DefineProcess(2)
                onefunc += DefineEnd()

                yield scrapy.Request(response.url, self.parse_script, meta=DefineMeta(onefunc))

    def parse_script(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        scripturl = response.urljoin(jsonresponse['getreturn'])
        yield scrapy.Request(scripturl, self.parse)

class SauroDownSpider(scrapy.Spider):
    name = "SauroDown"
    allowed_domains = ["stock.sohu.com"]
    #start_urls = [ "http://stock.sohu.com/stock_scrollnews.shtml" ]
    start_urls = [ "http://stock.sohu.com/20150907/n420528997.shtml" ]
    download_delay = 2
    request_depth_max = 2
    cookie_enable = True
    cookie_debug = True

    def get_parse(self, response):
        for href in response.xpath('//div[@class="main area"]/descendant::div[@class="f14list"]/descendant::a[position() mod 30 = 0]/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_contents)

    def parse_contents(self, response):
        for sel in response.xpath('//div[@itemprop="articleBody"]/text()'):
            itemcontent = sel.extract()
            print itemcontent.encode('utf-8')

#         for article in response.xpath('//div[@itemprop="articleBody"]/descendant-or-self::*[not(@class="muLink")]'):
# ancestor

#        for article in response.xpath('//div[@itemprop="articleBody"]//text()'):
#        for article in response.xpath('//div[@itemprop="articleBody"]/descendant-or-self::text()'):

#        articleList = response.xpath('//div[@itemprop="articleBody"]')
#        article = articleList.xpath('string(.)')[0].extract()
#        print article.encode('utf-8')

#        for article in response.xpath('//div[@itemprop="articleBody"]/*[not(name()="div")]/descendant-or-self::text()'):         // no direct, no div
#        for article in response.xpath('//div[@itemprop="articleBody"]/descendant-or-self::*[not(@class="muLink")]/text()'):      // all
#        for article in response.xpath('string(//div[@itemprop="articleBody"])'):                                                 // all
#        for article in response.xpath('//div[@itemprop="articleBody"]/text() | //div[@itemprop="articleBody"]/*[not(name()="div")]/descendant-or-self::text()'):    // OK\


#        for article in response.xpath('//div[@itemprop="articleBody"]/not(descendant-or-self::*(@class="muLink"))'):     *[@class="muLink"]
#        for article in response.xpath('string(//div[@itemprop="articleBody"]/p[2])'):


# sel = Selector(text=doc, type="html")

    def parse(self, response):
        artList = response.xpath('//div[@itemprop="articleBody"]')
        for article in artList:#.xpath('string(.)'):
            print article.extract().encode('utf-8')
            print ('-' * 40)


#        print article.extract().encode('utf-8')
#        for perp in article.xpath('//p'):
#            print perp.extract().encode('utf-8')
#            print ('-' * 20)


#        for sel in response.xpath('//div[@class="muLink"]/parent::*'):
#            print sel.extract().encode('utf-8')
#            print ('-' * 20)
        #article = articleList.xpath('string(./p)')[0]
        #sel = articleList.xpath('string(//p)')
        #print article.extract().encode('utf-8')
        #for sel in articleList.xpath('string(//p)'):
        #    print sel.extract()
        #print articleList[0].extract()


#        for sel in response.xpath('//div[@itemprop="articleBody"]/descendant-or-self::text()'):
#            itemcontent = sel.extract()
#            print itemcontent.encode('utf-8');

    def old_parse_contents(self, response):
        for sel in response.xpath('//ul/li'):
            item = SauroDownItem()
            item['title'] = sel.xpath('a/text()').extract()
            item['link'] = sel.xpath('a/@href').extract()
            item['content'] = sel.xpath('text()').extract()
            yield item

    def old_parse(self, response):
        for href in response.css("ul.directory.dir-col > li > a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

            item = SauroDownItem()
            item['link'] = sel.xpath('descendant::a[position() mod 30 = 0]/@href').extract()
            yield item


#        print response.xpath('//div[@class="main area"]/descendant::div[@class="f14list"]/descendant::a[position() mod 20 = 0]/@href')


    #settings.overrides['COOKIES_ENABLE'] = False
    #custom_settings['COOKIES_ENABLED'] = False
 
# position() mod 20 = 0

    #settings = crawler.settings
    #    if settings['LOG_ENABLED']:
    #        print "log is enabled!"

#    def parse(self, response):
#        print response.xpath('//title').extract();
#        for sel in response.xpath('//div[@class="main area"]/descendant::div[@class="f14list"]'):
#            #print sel.xpath('descendant::a/text()').extract()
#            item = SauroDownItem()
#            item['title'] = sel.xpath('descendant::a/text()').extract()
#            item['link'] = sel.xpath('descendant::a/@href').extract()
#            item['content'] = sel.xpath('descendant::text()').extract()
#            yield item
#        print item


#sel.xpath('//li[re:test(@class, "item-\d$")]//@href').extract()
        
#        for sel in response.xpath('//ul/li'):
#            item = DmozItem()
#            item['title'] = sel.xpath('a/text()').extract()
#            item['link'] = sel.xpath('a/@href').extract()
#            item['desc'] = sel.xpath('text()').extract()
#            yield item
    def notuse(self, notuse):
        article = ' '.join(articleList)
        article = article.replace('<p>', '')
        article = article.replace('</p>', '')

class MySpider(scrapy.Spider):
    name = "MySpider"
    allowed_domains = ["stock.sohu.com"]
    start_urls = [ "http://stock.sohu.com/stock_scrollnews_125.shtml" ]

    def parse(self, response):
        signList = response.xpath('/html/body//div')
        for onetag in signList:
            try:
                item['price'] = site.xpath('ul/li/div/a/span/text()').extract()[0]
            except IndexError:
                item['price'] = site.xpath('ul/li/a/span/text()').extract()[0]

            print string('onetag.xpath("@id")')[0].extract();
            print onetag.xpath('@class')[0].extract()
            print onetag
            print ('-' * 48)

    def parse_script(self, response):
        print response.xpath('//title').extract()

    def parse_old(self, response):
        script = """
        function main(splash) 
            local sohufunc = splash:jsfunc([[ function (){ go(curPage+1); return false; } ]]) 
            local getfunc = splash:jsfunc([[ function (){ var ishref = document.location.href; return ishref;} ]]) 
            splash:go(\"http://stock.sohu.com/stock_scrollnews_125.shtml\") 
            sohuf=sohufunc() 
            splash:wait(2) 
            getf=getfunc() 
            return {sohuf=sohuf, getfc=getf} 
        end
        """
        yield scrapy.Request('http://m/', self.parse_script, meta={
            'splash': {
                'args': {'lua_source': script},
                'endpoint': 'execute'
            }
        })



###
# http://edu.sse.com.cn/eduact/inact/popup_index.shtml?includPage=/eduact/edu/c/68007.html
#
# $(document).ready(function(){
###