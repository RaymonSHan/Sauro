# -*- coding:gbk -*-
#
# Althought I do not input any Chinese in my project, I still insert this progma before any codes.
# Recommen GBK instead of Unicode or UTF-8 in any case.
#
# Wrapping Column 132.

GlobalConfigureDict = {
    'TestLevel'          : 3,
    'CrawlLevel'         : 5,
    'CrawledPath'        : '/home/raymon/security/crawled/',
    'FingerprintPath'    : '/home/raymon/security/fingerprint/',
}

SiteConfigureList = [
    {
        'StartPage'          : 'stock.sohu.com',
        'SiteName'           : 'stock.sohu.com',
        'TestLevel'          : 3,
        'CrawlLevel'         : 5,
        'CrawledPath'        : '/home/raymon/security/crawled/',
        'FingerprintFile'    : '/home/raymon/security/fingerprint/sohu',
    },
    {
        'StartPage'          : 'http://finance.sina.com.cn/stock/',
    }
]
