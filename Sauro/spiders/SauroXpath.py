# -*- coding:gbk -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
#
# Wrapping Column 132.

from SauroCommon import *

# I will obliged to abandon xpath, and using my function. because of : 
# 1. text() & string() do not correct for <p> and <br> and \n.
# 2. if the original page is mix with gbk and unicode, all exist function report error. I should retrieve the right value
# 3. Selector fix tag error, but it fix <p> <div> </div> </p> to <p> </p> <div> </div> </p>, so fretfully.

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

# IN  : one tag
# OUT : text stirng
# for example <div class="sample"> inside </div>, return start of 'inside', start of '</div>', end of '<div>'
def GetTextInTag(response, tag, excludetaglist):
    excludetag = ''
    excludetagend = ''
    totalraw = ''
    toptag = True
    innest = 0
    
    usedtag = response.xpath(GetXpathfromTag(tag))
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
                    try: totalraw += splittagstring[1]
                    except: pass
# find exclude tag, begin nest loop for end match                        
                else:
                    innest += 1
                    excludetag = onlytag[0]
                    excludetagend = '/' + onlytag[0]
    return totalraw
# this is ok #######################################################################################################################
#    for onetext in response.xpath('//div[@itemprop="articleBody"]/text() | //div[@itemprop="articleBody"]/*[not(name()="div")]/descendant-or-self::text()'):
#        returnstring += onetext.extract()
#    print returnstring.encode('utf-8');
# this is ok #######################################################################################################################


####################################################################################################################################
# IN  : rawhtml, taglist:['div'] and so on
# OUT : longest tag, text pairs
def ReturnLeveledDivText(rawhtml):
    tagstack = []
    tagreturndict = {}
    nowdictkey = ''
    excludelist = ['script', 'style']
    innest = 0
    longesttextlen = 180
    returndictkey = ''

    rawhtml = rawhtml.replace('\n', '').replace('\r', '').replace('</p>', '').replace('<p>', '\n').replace('<br />', '\n').replace('<br>', '\n').replace('</th>', ',').replace('</td>', ',').replace('</tr>', '\n')
    tagwithstringlist = rawhtml.split('<')
    for onetagwithstring in tagwithstringlist:
        if onetagwithstring:
# useful value is onlytag[0] for tag name; splittagstring[1] for text
            splittagstring = onetagwithstring.split('>', 1)
            onlytag = splittagstring[0].split(' ', 1)
# should do stack for excludelist end
            if innest == 1:
# here means string with tag in script, or '<', '>' in script                
                if onlytag[0] != excludetagend:
                    # should do string reorgnize
                    continue
                innest = 0
            if onlytag[0] in excludelist:
                excludetagend = '/' + onlytag[0]
                innest = 1
                continue
# the tag name is div, change the tagstack, which is as key of returndict
            if onlytag[0] == 'div':
                tagstack.append(''.join(['<', splittagstring[0], '>']))
                nowdictkey = ''.join(tagstack)
                if not nowdictkey in tagreturndict.keys():
                    tagreturndict[nowdictkey] = {}
                    tagreturndict[nowdictkey]['text'] = []
                    tagreturndict[nowdictkey]['count'] = 0
                    tagreturndict[nowdictkey]['tagnum'] = 0
                    tagreturndict[nowdictkey]['longtext'] = 0
                    tagreturndict[nowdictkey]['alllength'] = 0
                    tagreturndict[nowdictkey]['textlength'] = 0
                IncreaseDictDictCount(tagreturndict, nowdictkey, 'count')
            if onlytag[0] == '/div':
                tagstack.pop()
                nowdictkey = ''.join(tagstack)
            try:
                tagreturndict[nowdictkey]['text'].append(splittagstring[1].strip(' \t'))
                IncreaseDictDictCount(tagreturndict, nowdictkey, 'tagnum')
                IncreaseDictDictCount(tagreturndict, nowdictkey, 'alllength', len(onetagwithstring))
                IncreaseDictDictCount(tagreturndict, nowdictkey, 'textlength', len(splittagstring[1].strip(' \t')))
                if len(splittagstring[1].strip(' \t')) > 50:
                    IncreaseDictDictCount(tagreturndict, nowdictkey, 'longtext')
            except:
                pass
                
    for tagreturn in tagreturndict.keys():
        tagvalue = tagreturndict[tagreturn]
        nowtext = ''.join(tagvalue['text'])
        nowlength = len(nowtext)
        if not tagvalue['longtext'] : #or tagvalue['alllength'] / nowlength > 3 or tagvalue['tagnum'] / tagvalue['longtext'] > 10 :
            continue
        print 'div : ', tagreturn
        print 'count : ', tagvalue['count']
        print 'tagnum : ', tagvalue['tagnum']
        print 'longtext : ', tagvalue['longtext']
        print 'alllength : ', tagvalue['alllength']
        print 'textlength : ',  tagvalue['textlength']
        print 'textlength-strip', nowlength
        print 'text : ', nowtext
        #print 'text : ', ''.join(tagreturndict[tagreturn['text']]).strip()
    return
    
    for tagreturn in tagreturndict.keys():
        nowtextlen = ReturnStringTotalLenght(tagreturndict[tagreturn]['text'])
        if nowtextlen > longesttextlen:
            longesttextlen = nowtextlen
            returndictkey = tagreturn
    return returndictkey, ''.join(tagreturndict[returndictkey['text']])

# nowin = 0: top, 1: in html comment <-- -->, 2: in script, 3: in script comment //, 4: in script comment /* */, 5: in script string ' ', 6: in script string " ", 7: in style
const.TAG_NORMAL                = 0
const.TAG_HTML_COMMENT          = 1
const.TAG_STYLE                 = 2
const.TAG_SCRIPT                = 128
const.TAG_SCRIPT_COMMENT_DIV    = 129
const.TAG_SCRIPT_COMMENT_STAR   = 130
const.TAG_SCRIPT_STRING_SINGLE  = 131
const.TAG_SCRIPT_STRING_DOUBLE  = 132
const.TAG_ONE_DIV               = 133
const.TAG_ONE_STAR              = 134
const.TAG_STRING_ESCAPE         = 135
const.TAG_SCRIPT_MAX            = 255

def TestLeveledDivText(rawhtml, filehandle):
    tagstack = []
    tagreturndict = {}
    nowdictkey = ''
    tagreturndict[nowdictkey] = {}
    tagreturndict[nowdictkey]['text'] = []
    excludelist = ['script', 'style']
    nowin = 0
    returndictkey = ''
    
# another hard work to do CR
#    rawhtml = rawhtml.replace('\n', '').replace('\r', '').replace('</p>', '').replace('<p>', '\n').replace('<br />', '\n').replace('<br>', '\n').replace('</th>', ',').replace('</td>', ',').replace('</tr>', '\n')
    tagwithstringlist = rawhtml.split('<')
# example in http://www.zhihu.com/question/20395431 useful but not efficient
#    tagwithstringlist = [ key + '<' for key in rawhtml.split('<')]
    for onetagwithstring in tagwithstringlist:
        print 'one', onetagwithstring
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
                elif tagname == 'div':
                    tagstack.append(''.join(['<', splittagstring[0], '>']))
                    nowdictkey = ''.join(tagstack)
                    if not nowdictkey in tagreturndict.keys():
                        tagreturndict[nowdictkey] = {}
                        tagvalue = tagreturndict[nowdictkey]
                        tagvalue['text'] = []
                        # and other init
                    IncreaseDictCount(tagvalue, 'count')
                elif tagname == '/div':
                    tagstack.pop()
                    nowdictkey = ''.join(tagstack)
            if nowin == const.TAG_HTML_COMMENT:
                if len(onlytag) <= 1:
                    tagattr = ''
                else:
                    tagattr = onlytag[1]
                tagattrlen = len(tagattr)
                if tagattrlen >= 2 and tagattr[-2:] == '--':
                    nowin = const.TAG_NORMAL
                elif tagattrlen == 0 and len(tagname) >=5 and tagname[-2:] == '--':  # <!--> is not end
                    nowin = const.TAG_NORMAL
                else:
                    if len(splittagstring) <= 1:
                        commentend = -1
                    else:
                        commentend = splittagstring[1].find('-->')
                    if commentend != -1:
                        splittagstring[1] = splittagstring[1][commentend + 3:]
                        nowin = const.TAG_NORMAL
            if nowin == const.TAG_STYLE:
                if tagname == '/style':
                    nowin = const.TAG_NORMAL
            if nowin == const.TAG_SCRIPT and tagname == '/script':
#                print '/script', nowin, onetagwithstring
                nowin = const.TAG_NORMAL             
            if nowin >= const.TAG_SCRIPT and nowin < const.TAG_SCRIPT_MAX:   # should attention the range
                for onechar in onetagwithstring:
#                    print 'before', onechar, nowin, onetagwithstring
                    if nowin == const.TAG_STRING_ESCAPE:
                        nowin = oldstringmode
                    elif nowin == const.TAG_SCRIPT and onechar == "'":
                        nowin = const.TAG_SCRIPT_STRING_SINGLE
                    elif nowin == const.TAG_SCRIPT and onechar == '"':
                        nowin = const.TAG_SCRIPT_STRING_DOUBLE
                    elif nowin == const.TAG_SCRIPT_STRING_SINGLE and onechar == "'":
                        nowin = const.TAG_SCRIPT
                    elif nowin == const.TAG_SCRIPT_STRING_DOUBLE and onechar == '"':
                        nowin = const.TAG_SCRIPT
                    elif nowin == const.TAG_SCRIPT_STRING_SINGLE or nowin == const.TAG_SCRIPT_STRING_DOUBLE:
                        print 'in choice', onechar
                        if onechar == '\\':
                            print 'in esc'
                            oldstringmode = nowin
                            nowin = const.TAG_STRING_ESCAPE
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
                        print 'is CR'
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
                            
                        
                    
            if nowin == const.TAG_NORMAL and len(splittagstring) > 1:
                tagvalue = tagreturndict[nowdictkey]
                nowtext = splittagstring[1].strip(' \t')
                print 'tag', nowdictkey, 'and', tagvalue, nowtext
                tagvalue['text'].append(nowtext)
                # add nowtext

    for tagreturn in tagreturndict.keys():
        tagvalue = tagreturndict[tagreturn]
        nowtext = ''.join(tagvalue['text'])
        print nowtext
    return
    
    for xx in yy:
        for zz in xx: 
# should do stack for excludelist end
            if innest == 1:
# here means string with tag in script, or '<', '>' in script                
                if onlytag[0] != excludetagend:
                    # should do string reorgnize
                    continue
                innest = 0
            if onlytag[0] in excludelist:
                excludetagend = '/' + onlytag[0]
                innest = 1
                continue
# the tag name is div, change the tagstack, which is as key of returndict
            if onlytag[0] == 'div':
                tagstack.append(''.join(['<', splittagstring[0], '>']))
                nowdictkey = ''.join(tagstack)
                if not nowdictkey in tagreturndict.keys():
                    tagreturndict[nowdictkey] = {}
                    tagvalue = tagreturndict[nowdictkey]
                    tagvalue['text'] = []
                    tagvalue['count'] = 0
                    tagvalue['tagnum'] = 0
                    tagvalue['long30text'] = 0
                    tagvalue['long50text'] = 0
                    tagvalue['long100text'] = 0
                    tagvalue['long180text'] = 0
                    tagvalue['alllength'] = 0
                    tagvalue['textlength'] = 0
                IncreaseDictCount(tagvalue, 'count')
            if onlytag[0] == '/div':
                tagstack.pop()
                nowdictkey = ''.join(tagstack)
            try:
                nowtext = splittagstring[1].strip(' \t')
                nowlength = len(nowtext)
                tagvalue = tagreturndict[nowdictkey]
                tagvalue['text'].append(nowtext)
                IncreaseDictCount(tagvalue, 'tagnum')
                IncreaseDictCount(tagvalue, 'alllength', len(onetagwithstring))
                IncreaseDictCount(tagvalue, 'textlength', nowlength)
                if nowlength > 30:
                    IncreaseDictCount(tagvalue, 'long30text')
                if nowlength > 50:
                    IncreaseDictCount(tagvalue, 'long50text')
                if nowlength > 100:
                    IncreaseDictCount(tagvalue, 'long100text')
                if nowlength > 180:
                    IncreaseDictCount(tagvalue, 'long180text')
            except:
                pass
    return
                
    for tagreturn in tagreturndict.keys():
        tagvalue = tagreturndict[tagreturn]
        nowtext = ''.join(tagvalue['text'])
        nowlength = len(nowtext)
        if not tagvalue['long50text'] or tagvalue['alllength'] / nowlength > 3 or tagvalue['tagnum'] / tagvalue['long50text'] > 10:
            continue
        filehandle.write('div : ' + tagreturn + '\n')
        filehandle.write('count : ' + str(tagvalue['count']))
        filehandle.write(', tagnum : ' + str(tagvalue['tagnum']))
        filehandle.write(', long30text : ' + str(tagvalue['long30text']))
        filehandle.write(', long50text : ' + str(tagvalue['long50text']))
        filehandle.write(', long100text : ' + str(tagvalue['long100text']))
        filehandle.write(', long180text : ' + str(tagvalue['long180text']))
        filehandle.write(', alllength : ' + str(tagvalue['alllength']))
        filehandle.write(', textlength : ' + str(tagvalue['textlength']))
        filehandle.write(', textlength-strip : ' + str(nowlength) + '\n')
        if nowlength > 200:
            nowlength = 200
        filehandle.write('text : ' + nowtext[:nowlength].encode('utf-8') + '\n')
        #print 'text : ', ''.join(tagreturndict[tagreturn['text']]).strip()
    filehandle.write('\n')
    return