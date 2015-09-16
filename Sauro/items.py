# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SauroDownItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    content = scrapy.Field()

class SauroScriptItem(scrapy.Item):
    pageURL = scrapy.Field()
    pageTitle = scrapy.Field()
    pageRefer = scrapy.Field()
    pageMethod = scrapy.Field()
    levelFromHome = scrapy.Field()
    stampLink = scrapy.Field()
    stampPage = scrapy.Field()
    pageContent = scrapy.Field()
    pageLinks = scrapy.Field()


    


#    <SauroPage url="stock.sohu.com/onepage.html" title="some title" level=1>    # This is Scrapy.Item, level for crawl deep
#      <SauroRefer from="stock.sohu.com" method="javascript:go(next_page)" />
#      <SauroStamp signlist="Daaabbb" urlmap="S5-xx" />
#      <SauroText mark="base64 of <div class='xx'>" value=3>
#        <SauroFragment>
#          base64 of content in it
#        </SauroFragment>
#      </SauroText>
#      <SauroText mark="base64 of <div class='yy'>" value=1>
#        <SauroFragment>
#          base64 of content in it
#        </SauroFragment>
#      </SauroText>
#      <SauroLinks value=10>   # link to text page
#        <SauroLink href="link" /> ...
#      </SauroLinks>
#    </SauroPage>


