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
                IncreaseDictDictCount(tagreturndict, nowdictkey, 'count')
            if onlytag[0] == '/div':
                tagstack.pop()
                nowdictkey = ''.join(tagstack)
                #print ''.join(tagstack)
            try:
                tagreturndict[nowdictkey]['text'].append(splittagstring[1].strip(' \t'))
                IncreaseDictDictCount(tagreturndict, nowdictkey, 'tagnum')
                IncreaseDictDictCount(tagreturndict, nowdictkey, 'alllength', len(onetagwithstring))
                IncreaseDictDictCount(tagreturndict, nowdictkey, 'textlength', len(splittagstring[1]))
            except:
                pass
    for tagreturn in tagreturndict.keys():
        nowtext = ''.join(tagreturndict[tagreturn]['text'])
        if not nowtext:
            continue
        print 'div : ', tagreturn
        print 'count : ', tagreturndict[tagreturn]['count']
        print 'tagnum : ', tagreturndict[tagreturn]['tagnum']
        print 'alllength : ', tagreturndict[tagreturn]['alllength']
        print 'textlength : ',  tagreturndict[tagreturn]['textlength']
        print 'textlength-strip', len(nowtext)
        print 'text : ', nowtext
        #print 'text : ', ''.join(tagreturndict[tagreturn['text']]).strip()
    return
    
    for tagreturn in tagreturndict.keys():
        nowtextlen = ReturnStringTotalLenght(tagreturndict[tagreturn]['text'])
        if nowtextlen > longesttextlen:
            longesttextlen = nowtextlen
            returndictkey = tagreturn
    return returndictkey, ''.join(tagreturndict[returndictkey['text']])