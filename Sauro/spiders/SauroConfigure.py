# -*- coding:gbk -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
#
# Wrapping Column 132.

from SauroCommon import *

const.StartPage         = 'StartPage'
const.SiteName          = 'SiteName'
const.TestLevel         = 'TestLevel'
const.CrawlLevel        = 'CrawlLevel'
const.CrawledPath       = 'CrawledPath'
const.FingerprintPath   = 'FingerprintPath'
const.FingerprintFile   = 'FingerprintFile'

GlobalConfigure = {
    const.TestLevel          : 3,
    const.CrawlLevel         : 5,
    const.CrawledPath        : '/home/raymon/security/crawled/',
    const.FingerprintPath    : '/home/raymon/security/fingerprint/',
}

SiteConfigureList = [{
    const.StartPage          : 'http://stock.sohu.com/',
    const.SiteName           : 'stock.sohu.com',
    const.TestLevel          : 3,
    const.CrawlLevel         : 5,
    const.CrawledPath        : '/home/raymon/security/crawled/',
    const.FingerprintFile    : '/home/raymon/security/fingerprint/sohu',
},
{
    const.StartPage          : 'http://finance.sina.com.cn/stock/',
}]

const.CONFIGFILE_INIT_OK         = 0
const.CONFIGFILE_GLOBAL_MISS     = 1
const.CONFIGFILE_GLOBAL_TYPEERROR= 2
const.CONFIGFILE_GLOBAL_PATHERROR= 3
const.CONFIGFILE_NO_STARTPAGE    = 10
const.CONFIGFILE_NO_HTTPHEAD     = 11

const.HTTP                       = 'http://'
const.HTTPS                      = 'https://'

def InitGlobalConfigure(maybeallowed, maybestarted):
    if not const.TestLevel in GlobalConfigure.keys():
        return const.CONFIGFILE_GLOBAL_MISS
    globaltestlevel = GlobalConfigure[const.TestLevel]
    if not isinstance(globaltestlevel, int): 
        return const.CONFIGFILE_GLOBAL_TYPEERROR

    if not const.CrawlLevel in GlobalConfigure.keys():
        return const.CONFIGFILE_GLOBAL_MISS
    globalcrawllevel = GlobalConfigure[const.CrawlLevel]
    if not isinstance(globalcrawllevel, int):
        return const.CONFIGFILE_GLOBAL_TYPEERROR

    if not const.CrawledPath in GlobalConfigure.keys():
        return const.CONFIGFILE_GLOBAL_MISS
    globalcrawledpath = GlobalConfigure[const.CrawledPath]
    if not isinstance(globalcrawledpath, str):
        return const.CONFIGFILE_GLOBAL_TYPEERROR
    if not globalcrawledpath[-1:] == '/':
        return const.CONFIGFILE_GLOBAL_PATHERROR

    if not const.FingerprintPath in GlobalConfigure.keys():
        return const.CONFIGFILE_GLOBAL_MISS
    globalfingerprint = GlobalConfigure[const.FingerprintPath]
    if not isinstance(globalfingerprint, str):
        return const.CONFIGFILE_GLOBAL_TYPEERROR
    if not globalfingerprint[-1:] == '/':
        return const.CONFIGFILE_GLOBAL_PATHERROR
        
    for onesite in SiteConfigureList:
        if not const.StartPage in onesite.keys():
            return const.CONFIGFILE_NO_STARTPAGE
        nowstartpage = onesite[const.StartPage].lower()
        if not nowstartpage.startswith(const.HTTP) and not nowstartpage.startswith(const.HTTPS):
            return const.CONFIGFILE_NO_HTTPHEAD
        maybestarted.append(onesite[const.StartPage])

        if not const.SiteName in onesite.keys():
            onesite[const.SiteName] = nowstartpage.split('/')[2]
        maybeallowed.append(onesite[const.SiteName])

        if not const.TestLevel in onesite.keys():
            onesite[const.TestLevel] = globaltestlevel

        if not const.CrawlLevel in onesite.keys():
            onesite[const.CrawlLevel] = globalcrawllevel

        if not const.CrawledPath in onesite.keys():
            onesite[const.CrawledPath] = globalcrawledpath

        if not const.FingerprintFile in onesite.keys():
            onesite[const.FingerprintFile] = ''.join([onesite[const.CrawledPath], onesite[const.SiteName]])

    
    return const.CONFIGFILE_INIT_OK


        

if __name__ == '__main__':
    maybeallowed = []
    maybestarted = []
    InitGlobalConfigure(maybeallowed, maybestarted)
    print maybeallowed, maybestarted
