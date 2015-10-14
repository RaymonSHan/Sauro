# -*- coding:gbk -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
#
# Wrapping Column 132.

from SauroCommon import *
from SauroAlgorithm import *
from SauroSetting import *
from SauroProcess import *

from SauroConfigure import *

if __name__ == '__main__':
    print const.ALLOW

const.JAVAFUNC = 'javafunc'
const.HREFFUNC = 'hreffunc'
const.FUNCHEAD = 'function main(splash) '
const.MAX_CRAWL_LEVEL = 2
const.HOST = 'http://stock.sohu.com/'
const.ALLOW = 'stock.sohu.com'

const.CONFIGFILE_INIT_OK         = 0
const.CONFIGFILE_NO_STARTPAGE    = 1
const.CONFIGFILE_NO_HTTPHEAD     = 2

const.HTTP                       = 'http://'
const.HTTPS                      = 'https://'

class notuse1_SauroCreateSpider(scrapy.Spider):
    name = 'SauroCreate'
    allowed_domains = []
    start_urls = []

    def start_requests(self):
        maybeallowed = []
        maybestarted = []
        okconfigured = const.CONFIGFILE_INIT_OK

        if not const.TestLevel in GlobalConfigure:
        
        for onesite in SiteConfigureList:

            if not const.StartPage in onesite.keys():
                okconfigured = const.CONFIGFILE_NO_STARTPAGE
                break
            nowstartpage = onesite[const.StartPage]
            if not nowstartpage.startswith(const.HTTP) and nowstartpage.startswith(const.HTTPS):
                okconfigured = const.CONFIGFILE_NO_HTTPHEAD
                break
            if not const.StartPage in onesite.keys():
                
                print nowstartpage
#            if 

        if okconfigured:
            self.allowed_domains = maybeallowed
            self.start_urls = maybestarted

        yield scrapy.Request('http://www.example.com/1.html', self.parse)
        yield scrapy.Request('http://www.example.com/2.html', self.parse)
        yield scrapy.Request('http://www.example.com/3.html', self.parse)

    def parse(self, response):
        print response.url
            
class notuse_SauroCreateSpider(scrapy.Spider):
    #start_urls = ["http://stock.sohu.com/stock_scrollnews_152.shtml"]
    #start_urls = ["http://stock.sohu.com/20150914/n421098148.shtml"]
    #start_urls = ["http://stock.sohu.com/20150915/n421130868.shtml"]


        
    #def parse_stampkey(self, response):
    #    strlist = sttry.split()
    #    print ReturnStampKey(strlist, None)

#    def __init__(self):
#        dispatcher.connect(self.initialize, signals.engine_started)
#        dispatcher.connect(self.finalize, signals.engine_stopped)

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


# http://ergoemacs.org/emacs/emacs_copy_cut_current_line.html emacs use
