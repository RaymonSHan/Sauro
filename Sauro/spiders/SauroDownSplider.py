import scrapy
import json
import string
import os                                   # for findfile & error in open
import hashlib                              # for md5
import fnmatch                              # for findfile
import errno                                # for error in open

###
# http://edu.sse.com.cn/eduact/inact/popup_index.shtml?includPage=/eduact/edu/c/68007.html
#
# $(document).ready(function(){
###


from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

#from Sauro.items import SauroScriptItem

class const: 
    class ConstError(TypeError):pass 
    def __setattr__(self, name, value): 
        if self.__dict__.has_key(name): 
            raise self.ConstError, "Can't rebind const (%s)" %name 
        self.__dict__[name]=value

const.JAVAFUNC = 'javafunc'
const.HREFFUNC = 'hreffunc'
const.FUNCHEAD = 'function main(splash) '
const.TEXTLEN = 180
const.MINSTAMP = 6
const.MAX_CRAWL_LEVEL = 1
const.PAGE_HOME = '/home/raymon/security/pages/'
const.FILE_HOME = '/home/raymon/security/pages/00/'
const.LOG_FILE = '/home/raymon/security/Saurolog'

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

def ReturnStamp(response):
    lastname = ''
    lastnum = 0
    totalname = 'M'
    for onesign in response.xpath('//div[@*] | //table[@*] | //form[@*] | //script[@*] | //style[@*]').extract():
        onlysign = onesign[0 : onesign.find('>')+1]
        thisname = onesign[1:2]
        if lastname == thisname:
            lastnum += 1
        else:
            totalname += lastname
            if lastnum != 0:
                totalname += str(lastnum)
                lastnum = 0
            lastname = thisname
    totalname += lastname
    if lastnum != 0:
        totalname += str(lastnum)
    totalname += 'M'
    return totalname

def ReturnTextDiv(response):
    textdict = []
    for onesign in response.xpath('//*[not(name()="script") and not(name()="style") and not(name()="a")]'):
        shouldnotuse = False

        for nonedisplay in onesign.xpath('ancestor-or-self::*[@style="display:none"]'):
            shouldnotuse = True
            break
        if shouldnotuse:
            continue
        signlen = len(onesign.extract())
        for onetext in onesign.xpath('text()'):
            textlen = len(onetext.extract().strip())
            if textlen > const.TEXTLEN:
                onlydiv = 'NoDiv'
                for fulldiv in onesign.xpath('ancestor-or-self::div[1]').extract():
                    onlydiv = fulldiv[0 : fulldiv.find('>')+1]
                textdict.append(onlydiv)
    return textdict

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
        
def OpenMD5File(urlname, rw='wb'):
    md5val = hashlib.md5()   
    md5val.update(urlname)   
    filename = md5val.hexdigest()   
    return OpenPathFile(const.PAGE_HOME + filename[0:2]+'/'+filename[2:4]+'/'+filename, 0, rw)
    
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

def iterfindfiles(path, fnexp):
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, fnexp):
            yield os.path.join(root, filename)

def ReturnStampKey(strlist, otherlist):
    firststr = strlist[0]
    returnlist = []
    beginpos = 0
    endpos = const.MINSTAMP
    lastpos = len(firststr)
    havechecked = 0     
    while endpos <= lastpos + 1:
        if endpos > lastpos:                        # for add last match
            checknothit = 1
        else:
            checkstr = firststr[beginpos:endpos]
            print 'checkstr in mainloop =', checkstr
            checkhit = 0
            checknothit = 0
            for descstr in strlist:
                if descstr.find(checkstr) == -1:
                    checknothit = 1
                    break
        if checknothit == 1:
            if havechecked == 1:
                returnlist.append(firststr[beginpos:endpos-1])
                beginpos = endpos
                endpos = beginpos + const.MINSTAMP
                havechecked = 0
            else:
                beginpos += 1
                endpos += 1
        else:
            havechecked = 1
            endpos += 1
    return returnlist

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
        for onesign in signList:
            try:
                item['price'] = site.xpath('ul/li/div/a/span/text()').extract()[0]
            except IndexError:
                item['price'] = site.xpath('ul/li/a/span/text()').extract()[0]

            print string('onesign.xpath("@id")')[0].extract();
            print onesign.xpath('@class')[0].extract()
            print onesign
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
