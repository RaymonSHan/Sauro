# -*- coding:utf-8 -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
# here have a chinese char to detect, should move to another file
#
# Wrapping Column 132.

from SauroCommon import *

# I will obliged to abandon xpath, and using my function. because of : 
# 1. text() & string() do not correct for <p> and <br> and \n.
# 2. do not found the corrent </script> matched for <script>, such as "</script>"
# 3. if the original page is mix with gbk and unicode, all exist function report error. I should retrieve the right value
# 4. Selector fix tag error, but it fix <p> <div> </div> </p> to <p> </p> <div> </div> </p>, so fretfully.

# IN  : one tag
# OUT : xpath string for locate the tag, if error return ''
# for example '<div itemprop="articleBody">' translate to '//div[@itemprop="articleBody"]'
# this is used for part of xpath from scarpy, while use some from myself
def GetXpathfromTag(tag):
    returnstring = ''
# the start and end of the tag must be '<' and '>'    
    if tag[0] != '<': return returnstring
    if tag[-1] != '>': return returnstring
# tag name is end by SPACE, if not found all tag is tagname    
    tagnameend = tag.find(' ')
    if tagnameend == -1:
        return '//' + tag[1:-1]
    tagname = tag[1:tagnameend]
# split by SPACE is more easy to understand, but attribute value may contain SPACE        
    attrlist = tag[tagnameend + 1:-1].split('"')
# '"' must be close, count of '"' must be even, len of list must be odd
# THIS IS NO "\"" IN SIDE TAGS, I SUPPOSE
    if len(attrlist) % 2 != 1: return returnstring
    order = 0
    returnstring = '//' + tagname + '['
    for oneattr in attrlist[:-1]:
        if order % 2 == 0:
            if order == 0: returnstring += '@'
            else: returnstring += ' and @'
            returnstring += oneattr.strip()
        else:
            returnstring += '"' + oneattr + '"'
        order += 1
    returnstring += ']'
    return returnstring

def GetMultiXpathfromTag(tag):
    returnlist = []
    taglist = tag.split('>')
    for onetag in taglist:
        returnlist.append(GetXpathfromTag(onetag.strip() + '>'))
    return ''.join(returnlist)


# IN  : one tag
# OUT : text stirng
# for example <div class="sample"> inside </div>, return 'inside'
def GetTextInTag(response, tag, excludetaglist):
    excludetag = ''
    excludetagend = ''
    totalraw = []
    toptag = True
    innest = 0
    
    usedtag = response.xpath(GetMultiXpathfromTag(tag))
# although the eigen is match, do not found the tag it marked, return null    
    if not usedtag:
        return ''
    rawhtml = usedtag[0].extract()
    rawhtml = rawhtml.replace('\n', '').replace('\r', '').replace('</p>', '').replace('<p>', '\n').replace('<br />', '\n').replace('<br>', '\n').replace('</th>', ',').replace('</td>', ',').replace('</tr>', '\n')
# this split should be replaced by own writen, for <script> str='</script>' if str < (or) > str1 ...  </script>
    tagwithstringlist = rawhtml.split('<')
    for onetagwithstring in tagwithstringlist:
        if onetagwithstring:
# useful value is onlytag[0] for tag name; splittagstring[1] for text
            splittagstring = onetagwithstring.split('>', 1)
            onlytag = splittagstring[0].split(' ', 1)
            if innest != 0:
                if onlytag[0] == excludetag: innest += 1
                elif onlytag[0] == excludetagend: innest -= 1
            if innest == 0:
# must process top level tag even it in exclude list            
                if toptag or not onlytag[0] in excludetaglist:
                    toptag = False
                    try: totalraw.append(splittagstring[1])
                    except: pass
# find exclude tag, begin nest loop for end match                        
                else:
                    innest += 1
                    excludetag = onlytag[0]
                    excludetagend = '/' + onlytag[0]
    return ''.join(totalraw)
# this is ok #######################################################################################################################
#    for onetext in response.xpath('//div[@itemprop="articleBody"]/text() | //div[@itemprop="articleBody"]/*[not(name()="div")]/descendant-or-self::text()'):
#        returnstring += onetext.extract()
#    print returnstring.encode('utf-8');
# this is ok #######################################################################################################################

# define the state fo State Machine
const.TAG_NORMAL                = 0
const.TAG_HTML_COMMENT          = 1                 # <!--
const.TAG_STYLE                 = 2                 # <style>
const.TAG_SCRIPT                = 128               # <script>
const.TAG_SCRIPT_COMMENT_DIV    = 129               # <script>  //
const.TAG_SCRIPT_COMMENT_STAR   = 130               # <script>  /*
const.TAG_SCRIPT_STRING_SINGLE  = 131               # <script>  '
const.TAG_SCRIPT_STRING_DOUBLE  = 132               # <script>  "
const.TAG_ONE_DIV               = 133               # <script>  /
const.TAG_ONE_STAR              = 134               # <script>  /* *
const.TAG_STRING_ESCAPE_SINGLE  = 135               # <script>  ' \
const.TAG_STRING_ESCAPE_DOUBLE  = 136               # <script>  " \
const.TAG_SCRIPT_MAX            = 255

def InitTagDict(tagreturndict,nowdictkey):
    tagreturndict[nowdictkey] = {}
    tagvalue = tagreturndict[nowdictkey]
    tagvalue['text'] = []
    tagvalue['count'] = 0
    tagvalue['havep'] = 0
    return

StringSizeRecord = [-1, 0, 5, 10, 20, 30, 50, 70, 100, 140, 180, 250]
# example in http://www.zhihu.com/question/20395431    
StirngSizeRecordMark = [ 'txt' + str(k) for k in StringSizeRecord ]
StringSizeRecordLength = len(StringSizeRecord)

def ProcessTagDict(tagreturndict, nowdictkey, nowtext, allstring):
    nowlength = len(nowtext)
    alllength = len(allstring)
    tagvalue = tagreturndict[nowdictkey]
    tagvalue['text'].append(nowtext)
    
    for nowrange in xrange(StringSizeRecordLength):
        nowsize = StringSizeRecord[nowrange]
        nowstr = StirngSizeRecordMark[nowrange]
        if nowlength > nowsize:
            IncreaseDictDictCount(tagvalue, nowstr, 'count')
            IncreaseDictDictCount(tagvalue, nowstr, 'textlen', nowlength)
            IncreaseDictDictCount(tagvalue, nowstr, 'alllen', alllength)
    return  

def ReturnTagDict(tagvalue, splitkey = ','):
    returnlist = []
    for nowstr in StirngSizeRecordMark:
        try:
            count = tagvalue[nowstr]['count']
            textlen = tagvalue[nowstr]['textlen']
            alllen = tagvalue[nowstr]['alllen']
        except:
            count = 0
            textlen = 0
            alllen = 0
        returnlist.append(splitkey.join([nowstr, str(count), str(textlen), str(alllen)]))
    return splitkey.join(returnlist)

def ProcessScriptStatemachine(nowin, processstring):
    for onechar in processstring:
        if nowin == const.TAG_STRING_ESCAPE_SINGLE:
            nowin = const.TAG_SCRIPT_STRING_SINGLE
        elif nowin == const.TAG_STRING_ESCAPE_DOUBLE:
            nowin = const.TAG_SCRIPT_STRING_DOUBLE
        elif nowin == const.TAG_SCRIPT and onechar == "'":
            nowin = const.TAG_SCRIPT_STRING_SINGLE
        elif nowin == const.TAG_SCRIPT and onechar == '"':
            nowin = const.TAG_SCRIPT_STRING_DOUBLE
        elif nowin == const.TAG_SCRIPT_STRING_SINGLE and onechar == "'":
            nowin = const.TAG_SCRIPT
        elif nowin == const.TAG_SCRIPT_STRING_DOUBLE and onechar == '"':
            nowin = const.TAG_SCRIPT
        elif nowin == const.TAG_SCRIPT_STRING_SINGLE and onechar == '\\':
            nowin = const.TAG_STRING_ESCAPE_SINGLE
        elif nowin == const.TAG_SCRIPT_STRING_DOUBLE and onechar == '\\':
            nowin = const.TAG_STRING_ESCAPE_DOUBLE
        elif nowin == const.TAG_SCRIPT and onechar == '/':
            nowin = const.TAG_ONE_DIV
        elif nowin == const.TAG_ONE_DIV:
            if onechar == '/':
                nowin = const.TAG_SCRIPT_COMMENT_DIV
            elif onechar == '*':
                nowin = const.TAG_SCRIPT_COMMENT_STAR
            else:
                nowin = const.TAG_SCRIPT
        elif nowin == const.TAG_SCRIPT_COMMENT_DIV and onechar == '\n':
            nowin = const.TAG_SCRIPT
        elif nowin == const.TAG_SCRIPT_COMMENT_STAR and onechar == '*':
            nowin = const.TAG_ONE_STAR
        elif nowin == const.TAG_ONE_STAR:
            if onechar == '*':
                nowin = const.TAG_ONE_STAR
            elif onechar == '/':
                nowin = const.TAG_SCRIPT
            else:
                nowin = const.TAG_SCRIPT_COMMENT_STAR
    return nowin

def IsMainText(tagvalue):
    nowlength = ReturnStringTotalLenght(tagvalue['text'])
######## for txt1010-180.csv ###################################################################################################### 
    try:
        number = tagvalue['txt180']['count']
    except:
        number = 0
    if number != 0:
######## for txt1010.csv ########################################################################################################## 
#    try:
#        number = tagvalue['txt30']['count']
#    except:
#        number = 0
#    nowtext = ''.join(tagvalue['text'])
#    charcount = nowtext.count(u'，', 0, 200)
#    charcount += nowtext.count(u'。', 0, 200)
#    if number != 0 and charcount != 0 and tagvalue['count'] == 1:
######## for txt1009.csv ########################################################################################################## 
#    probability = tagvalue['long180text'] * 500 + tagvalue['long100text'] * 100 + tagvalue['long50text'] * 50 + tagvalue['long30text'] * 20 + nowlength * 4 - tagvalue['alllength']
#    if probability > 100:
    
#    if tagvalue['long50text'] and tagvalue['alllength'] / nowlength < 3 and tagvalue['tagnum'] / tagvalue['long50text'] < 10:
        return True
    else:
        return False
            
def OutputMainText(tagvalue, textlen = 200):
    nowtext = ''.join(tagvalue['text'])
    nowlength = len(nowtext)
    usedtext = nowtext[:textlen].replace('\n', '<br>').replace('\t', '').replace('\r', '')
    usedtitle = tagvalue['title'].replace('\n', '<br>').replace('\t', '').replace('\r', '')
######## for txt1010.csv & txt1010-180.csv ######################################################################################## 
    resultstring = '\t'.join([tagvalue['url'], usedtitle, tagvalue['tagorder'], str(tagvalue['count']), str(nowlength), ReturnTagDict(tagvalue, '\t'), usedtext])  
######## for txt1009.csv ########################################################################################################## 
#    resultstring = ''.join(['url\t', tagvalue['url'], '\ttitle\t', usedtitle, '\tdiv\t', tagreturn, '\tcount\t', str(tagvalue['count']), '\ttagnum\t', str(tagvalue['tagnum']), '\tall\t', str(tagvalue['alllength']), '\ttext\t', str(tagvalue['textlength']), '\tstrip\t', str(nowlength), '\ttxt30\t', str(tagvalue['long30text']), '\ttxt50\t', str(tagvalue['long50text']), '\ttxt100\t', str(tagvalue['long100text']), '\ttxt180\t', str(tagvalue['long180text']), '\ttext\t', usedtext, '\t'])    
#    resultstring = ''.join(['url : ', tagvalue['url'], ', title : ', tagvalue['title'], '\ndiv : ', tagreturn, '\ncount : ', str(tagvalue['count']), ', tagnum : ', str(tagvalue['tagnum']), ', all : ', str(tagvalue['alllength']), ', text : ', str(tagvalue['textlength']), ', strip : ', str(nowlength), '\ntxt30 : ', str(tagvalue['long30text']), ', txt50 : ', str(tagvalue['long50text']), ', txt100 : ', str(tagvalue['long100text']), ', txt180 : ', str(tagvalue['long180text']), '\ntext : ', nowtext[:textlen], '...\n'])
    return resultstring

MainTagList = ['div', 'form', 'table']          # should move to global
MainTagEndList = ['/'+key for key in MainTagList]

const.OUTPUT_FORMAT_STRING      = 0
const.OUTPUT_FORMAT_DICT        = 1
const.OUTPUT_FORMAT_JSON        = 2

# IN  : rawhtml, taglist:['div'] and so on
# OUT : all tag, text pairs
# ATTENTION any text before first tag will be omitted !!!
def GetAllLeveledText(rawhtml):
    tagreturndict = {}
    nowin = const.TAG_NORMAL
    returndictkey = ''
    tagstack = []
    nowdictkey = ''.join(tagstack)

# init dict for empty key    
    InitTagDict(tagreturndict,nowdictkey)
#    rawhtml = rawhtml.replace('\n', '').replace('\r', '').replace('</p>', '').replace('<p>', '\n').replace('<br />', '\n').replace('<br>', '\n').replace('</th>', ',').replace('</td>', ',').replace('</tr>', '\n')
    tagwithstringlist = rawhtml.split('<')
# in normal html, all '<' is start of tag. but in <script> <style> <!-- -->, there are maybe '<' for other
    for onetagwithstring in tagwithstringlist:
        if onetagwithstring:
# useful value is onlytag[0] for tag name; splittagstring[1] for text
            splittagstring = onetagwithstring.split('>', 1)
            onlytag = splittagstring[0].split(' ', 1)
            tagname = onlytag[0].lower()
# do process in different condition
            if nowin == const.TAG_NORMAL:
                if tagname == 'script':
                    nowin = const.TAG_SCRIPT
                elif tagname == 'style':
                    nowin = const.TAG_STYLE
                elif tagname.startswith('!--'):
                    nowin = const.TAG_HTML_COMMENT
# with title tag, and have text after this tag
                elif tagname == 'title' and len(splittagstring) >= 2:
                    pagetitle = splittagstring[1]
                elif tagname in MainTagList:
                    tagstack.append(''.join(['<', splittagstring[0], '>']))
                    nowdictkey = ''.join(tagstack)
                    if not nowdictkey in tagreturndict.keys():
                        InitTagDict(tagreturndict, nowdictkey)
                    IncreaseDictDictCount(tagreturndict, nowdictkey, 'count')
                elif tagname in MainTagEndList:
                    if tagstack:
# open tag can be anywhere, but close tag have its order.                      
                        nowstarttag = tagstack.pop()
                        nowstartname = nowstarttag.split(' ', 1)[0]
                        if nowstartname.lower().strip('<>/') != tagname.strip('<>/'):
# in http://q.stock.sohu.com/app2/mpssTrade.up?code=300168&ed=&sd= , and other page with same url format to fix the mistake
# <th style="text-align:center;width:8%"  rowspan="2" class="e2 ">标的证券代码</div></th>                             
                            tagstack.append(nowstarttag)
# if pop the wrong tag, push it again
                    else:
# in http://stock.sohu.com/s2014/voice/ , http://stock.sohu.com/s2014/amnews/ , http://stock.sohu.com/s2014/tmt/, http://stock.sohu.com/s2014/amnews/index.shtml to fix the mistake# <div id="banner" ><div class="linka"...> </div></div></div>
# in http://stock.sohu.com/s2013/jrbk02/, to fix <DIV class="top"><div class="topnum">002</div><div class="toptitle">新股网上配售申购方法详解/div></div></DIV>
# in http://stock.sohu.com/20150915/n421131352.shtml to fix <div class="content-footer"></div></div>, there maybe another error in this page, for the number of <div> and </div> is same
                        pass
                    nowdictkey = ''.join(tagstack)
                elif tagname == 'p' or tagname == 'br':
# should remove CR in text, and add CR for <p> & <br>
                    tagreturndict[nowdictkey]['text'].append('\n')
                    tagreturndict[nowdictkey]['havep'] += 1
            if nowin == const.TAG_HTML_COMMENT:
                if len(onlytag) <= 1:
                    tagattr = ''
                else:
                    tagattr = onlytag[1]
                tagattrlen = len(tagattr)
                if tagattrlen >= 2 and tagattr[-2:] == '--':
# there are SPACE between '<!--' and '-->' and the last chars are '-->'
                    nowin = const.TAG_NORMAL
                elif tagattrlen == 0 and len(tagname) >=5 and tagname[-2:] == '--':
# there are NO SPACE, and the '--' should long enough, <!--> is not end
                    nowin = const.TAG_NORMAL
                else:
                    if len(splittagstring) <= 1:
# there are no '>' between '<!--' and next '<'                    
                        commentend = -1
                    else:
# the first '>' is not '-->', but there are more chars after '>', 
                        commentend = splittagstring[1].find('-->')
                    if commentend != -1:
# found the real '-->' end, only the text after it is real text
                        splittagstring[1] = splittagstring[1][commentend + 3:]
                        nowin = const.TAG_NORMAL
            if nowin == const.TAG_STYLE:
# maybe style should do more 
                if tagname == '/style':
                    nowin = const.TAG_NORMAL
            if nowin == const.TAG_SCRIPT and tagname == '/script':
                nowin = const.TAG_NORMAL             
            if nowin >= const.TAG_SCRIPT and nowin < const.TAG_SCRIPT_MAX:
# <script> is most hard, do char step state machine for it.
# After split, the '<' is lost, add it so on.
                nowin = ProcessScriptStatemachine(nowin, '<')
                nowin = ProcessScriptStatemachine(nowin, onetagwithstring)

            if nowin == const.TAG_NORMAL and len(splittagstring) > 1:
# remove \t\r\n for these text
                nowtext = splittagstring[1].strip(' \t\r\n')
                ProcessTagDict(tagreturndict, nowdictkey, nowtext, onetagwithstring)
    return tagreturndict

def ReturnLeveledTagText(rawhtml, url, output = const.OUTPUT_FORMAT_STRING):
    returnlist = []
    pagetitle = ''
    tagreturndict = GetAllLeveledText(rawhtml)
# here have record all text in any tag level, check and output
    for tagreturn in tagreturndict.keys():
# if any tag have marked none display, ignore it.
        displaynone = tagreturn.find('display:none')
        if displaynone != -1:
            continue
        tagvalue = tagreturndict[tagreturn]
        if IsMainText(tagvalue):
            tagvalue['title'] = pagetitle
            tagvalue['url'] = url
            tagvalue['tagorder'] = tagreturn
            if output == const.OUTPUT_FORMAT_STRING:
                returnlist.append(OutputMainText(tagvalue))
            elif output == const.OUTPUT_FORMAT_DICT:
                returnlist.append(tagvalue)
    return returnlist

def HavePunctuation(nowtext):
    charcount = nowtext.count(u'，', 0, 200)
    charcount += nowtext.count(u'。', 0, 200)
    if charcount > 3:
        return True
    else:
        return False
   
####################################################################################################################################

# otherpara is list of tag, which match it's fingerprint
# ATTENTION !!! the order of text in multi tag maybe miss order, should change dict struct to fix it
def GetContentByLevelDiv(response, otherpara):
    returnlist = []
    if isinstance(response, scrapy.selector.unified.Selector):
        rawhtml = response.extract()
    else:
        rawhtml = response
    tagreturndict = GetAllLeveledText(rawhtml)
    selflevel = 0
    maxselflevel = 0
    for tagreturn in tagreturndict.keys():
        if tagreturn in otherpara:
            nowtext = ''.join(tagreturndict[tagreturn]['text'])
            selflevel = len(nowtext)
            if maxselflevel < selflevel:
                maxselflevel = selflevel
            returnlist.append(nowtext)
            
    for tagreturn in tagreturndict.keys():            
        if InSuperString(tagreturn, otherpara) != -1:
            nowtext = ''.join(tagreturndict[tagreturn]['text'])
            if HavePunctuation(nowtext) and selflevel < len(nowtext):
                returnlist.append(nowtext)
                continue
    return ''.join(returnlist)
            
        
    