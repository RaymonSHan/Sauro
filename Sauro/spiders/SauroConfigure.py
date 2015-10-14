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
