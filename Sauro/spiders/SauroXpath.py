# I will obliged to abandon xpath, and using my function. because of : 
# 1. text() & string() do not correct for <p> and <br> and \n.
# 2. if the original page is mix with gbk and unicode, all exist function report error. I should retrieve the right value
# 3. Selector fix tag error, but it fix <p> <div> </div> </p> to <p> </p> <div> </div> </p>, so fretfully.

# IN  : one tag
# OUT : begin tag, inside tag, end tag
# for example <div class="sample"> inside </div>, return start of 'inside', start of '</div>', end of '<div>'
def GetTextInTag(response, excludetaglist):
    rawhtml = response.xpath('//div[@itemprop="articleBody"]')[0].extract()
    rawhtml = rawhtml.replace('\n', '').replace('\r', '').replace('</p>', '').replace('<p>', '\r\n').replace('<br />', '\r\n')
    
    excludetag = ''
    excludetagend = ''
    totalraw = ''
    toptag = True
    innest = 0
    
# this split should be replaced by own writen, for <script> str='</script>' if str < (or) > str1 ...  </script>
    stringlist = rawhtml.split('<')
    for onetagwithstring in stringlist:
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
    print totalraw
    return
# this is ok #######################################################################################################################
#    for onetext in response.xpath('//div[@itemprop="articleBody"]/text() | //div[@itemprop="articleBody"]/*[not(name()="div")]/descendant-or-self::text()'):
#        returnstring += onetext.extract()
#    print returnstring.encode('utf-8');
# this is ok #######################################################################################################################
    return onetext