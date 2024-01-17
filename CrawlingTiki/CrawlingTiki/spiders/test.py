import scrapy
import json
import re

class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["api.tiki.vn"]
    start_urls = ["https://api.tiki.vn/raiden/v2/menu-config"]


    # Lấy danh mục sản phẩm từ API 
    def parse(self, response):
        resp = json.loads(response.body)
        menu_block = resp.get('menu_block')
        # title = menu_block.get('title')
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
                   
    # 
    def parse_category(self, response):
             
        categoryid = response.request.meta['categoryid']
        urlKey = response.request.meta['urlKey']
        name = response.request.meta['name']
        link = response.request.url
                
        category_list = [categoryid]
        urlKeys = [urlKey]
        
        for i in range(0, len(category_list)):
            list_url = f'https://tiki.vn/api/personalish/v1/blocks/listings?include=advertisement&aggregations=2&category={category_list[i]}&page=1&urlKey={urlKeys[i]}'  
            
            yield scrapy.Request(
                    list_url,
                    callback=self.parse_init,
                    errback=self.errback_httpbin,
                    dont_filter=True
            )            
     
            
    def parse_init(self, response):
        resp = json.loads(response.body)
        
        filters = resp.get('filters')
        
        subcategorys = filters[0].get('values')
        
        for subcategory in subcategorys:
            
            subcategoryid = subcategory.get('query_value')
            name_subcategory = subcategory.get('display_value')
            url_key = subcategory.get('url_key')
            url_path = subcategory.get('url_path')
            total_item = subcategory.get('count')
            
            yield scrapy.Request(
                url=f'https://tiki.vn/api/personalish/v1/blocks/listings?include=advertisement&aggregations=2&category={subcategoryid}&page=1&urlKey={url_key}',
                callback=self.parse_subcategory,
                errback=self.errback_httpbin,
                dont_filter=True
            )  
        
            
    def parse_subcategory(self, response):
        
        resp = json.loads(response.body)
        filters = resp.get('filters')
        check_category = filters[0].get('display_name')
        
        if check_category.strip() == 'Danh Mục Sản Phẩm'.strip():
            print(check_category)
            
            subcategorys = filters[0].get('values')
            
            for subcategory in subcategorys:
            
                subcategoryid = subcategory.get('query_value')
                name_subcategory = subcategory.get('display_value')
                url_key = subcategory.get('url_key')
                url_path = subcategory.get('url_path')
                total_item = subcategory.get('count')

                yield scrapy.Request(
                    url=f'https://tiki.vn/api/personalish/v1/blocks/listings?include=advertisement&aggregations=2&category={subcategoryid}&page=1&urlKey={url_key}',
                    callback=self.parse_subcategory,
                    errback=self.errback_httpbin,
                    dont_filter=True
                    # ,
                    # meta={'categoryid': categoryid, 'urlKey': urlKey, 'name': name}
                ) 
                
        else:
            # print(check_category)
            print('EEEEEEEEEEELLLLLLLLLLSSSSSSSSSSEEEEEEEEEEE')
        
    # Xử lý sử kiện khi gặp lỗi trong quá trình chuyển trang           
    def errback_httpbin(self, failure):
        print('EEEEEEEEEERRRRRRRRRRRRRRRROOOOOOOOOORRRRRR')            
            