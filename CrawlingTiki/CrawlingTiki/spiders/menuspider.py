import scrapy
import json
import re
import datetime
import logging

from ..items import MenuTiki

Logger = logging.getLogger()

class MenuspiderSpider(scrapy.Spider):
    name = "menuspider"
    allowed_domains = ["api.tiki.vn"]
    start_urls = ["https://api.tiki.vn/raiden/v2/menu-config"]

    # Phân tích response từ API trả về 
    def parse(self, response):
        # Lấy response sản phẩm từ API 
        resp = json.loads(response.body)
        
        menu_block = resp.get('menu_block')
        # title = menu_block.get('title')
        
        # Lấy toàn bộ các danh mục gốc 
        menu_items = menu_block.get('items')
        
        # Lặp qua toàn bộ các danh mục gốc 
        for menu_item in menu_items: 
            next_page = menu_item.get('link')
            url = next_page.split("/")
            categoryid = re.sub('[a-z]', '', url[4])
            urlKey = url[3]
            name = menu_item.get('text')  
                
            # Chuyển qua những trang trong danh mục để lấy thông tin của danh mục con     
            yield scrapy.Request(
                next_page,
                callback=self.parse_category,
                errback=self.errback_httpbin,
                dont_filter=True,
                meta={'categoryid': categoryid, 'urlKey': urlKey, 'name': name}
            )    
                   

    # Lưu thông tin danh mục sản phẩm gốc
    def parse_category(self, response):
        
        items = MenuTiki()
                    
        items['categoryParentId'] = response.request.meta['categoryid']
        items['categoryName'] =  response.request.meta['urlKey']
        items['urlKey'] = response.request.meta['name'] 
        items['link'] =  response.request.url
        items['checkpoint'] = False
        items['createdDate'] = datetime.datetime.utcnow()
        items['updatedDate'] = datetime.datetime.utcnow()
           
        yield items
        
    def errback_httpbin(self, failure):
        Logger.error('EEEEEEEEEERRRRRRRRRRRRRRRROOOOOOOOOORRRRRR')
            
