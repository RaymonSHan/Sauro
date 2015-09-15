import scrapy
import json
import string


from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor


from Sauro.items import SauroDownItem

class const: 
    class ConstError(TypeError):pass 
    def __setattr__(self, name, value): 
        if self.__dict__.has_key(name): 
            raise self.ConstError, "Can't rebind const (%s)" %name 
        self.__dict__[name]=value

const.JAVAFUNC = 'javafunc'
const.HREFFUNC = 'hreffunc'
const.FUNCHEAD = 'function main(splash) '
const.TEXTLEN = 50

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

def GetSingleDiv(onediv):
    alllength = len(onediv.extract())

    for alldiv in onediv.xpath('div'):
        alllength -= len(alldiv.extract())
    for alltext in onediv.xpath('text() | *[not(name()="div")]/descendant-or-self::text()'):
        exttext = alltext.extract()
        textlen = len(exttext)
    return alllength, textlen, exttext

class SauroScriptSpider(scrapy.Spider):
    name = "SauroScript"
    allowed_domains = ["stock.sohu.com"]
#    start_urls = [ "http://stock.sohu.com/" ]
#    start_urls = [ "http://stock.sohu.com/stock_scrollnews_152.shtml" ]
#    start_urls = [ "http://stock.sohu.com/20150914/n421098148.shtml" ]
    start_urls = [ "http://stock.sohu.com/20150915/n421130868.shtml" ]
    mydict = {}

    def __init__(self):
        dispatcher.connect(self.finalize,signals.engine_stopped)

    def finalize(self):
        sortdict = sorted(self.mydict.items(), key=lambda d: len(d[1]), reverse=True)
        for (k, v) in sortdict:
            print k;
            print len(v);
            print v
#        for (k, v) in self.mydict.items():
#            print "dict[%s] =" % k, len(v)

    def parse(self, response):
        textdict = {}
        rate = 0.00
        for onesign in response.xpath('//*[not(name()="script") and not(name()="style") and not(name()="a")]'):
            signlen = len(onesign.extract())
            for onetext in onesign.xpath('text()'):
                textlen = len(onetext.extract().strip())
                if textlen > const.TEXTLEN and textlen * 4 > signlen:
                    fulldiv = onesign.xpath('parent::div')[0].extract()
                    onlydiv = fulldiv[0:fulldiv.find('>')+1]
                    print onlydiv
                    
#                    for oneance in onesign.xpath('ancestor::div'):
#                        alllength, textlen, alltext = GetSingleDiv(oneance)
#                        print alllength, textlen, alltext


                        


    def parse_dict(self, response):
        lx = SgmlLinkExtractor()
        urls = lx.extract_links(response)
        for oneurl in urls:
            returl = ReturnExpr(oneurl.url)

            try:
                self.mydict[returl].append(oneurl)
#                self.mydict[returl] += 1
            except KeyError:
                self.mydict[returl] = []
                self.mydict[returl].append(oneurl)
#                self.mydict[returl] = 1
#
#            print self.mydict[returl];
#            print oneurl.url + ' ' + oneurl.text.encode('utf-8')
            
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
