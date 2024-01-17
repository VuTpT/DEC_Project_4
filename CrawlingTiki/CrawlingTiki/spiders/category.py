import scrapy
import urllib.parse
import json
from pymongo import MongoClient
from itemloaders import ItemLoader
from scrapy.loader import ItemLoader
from ..items import CategorySubTiki

import logging

Logger = logging.getLogger()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
collection = client['menuTiki']


# Storing data into a database
# def insertCategory(categoryParentId, urlKeyParent, subCategoryId, subCategoryName, urlKey, urlPath, totalItem, lastPage, numOfLastPage, isCheck):
        
#     categories = collection['category']
    
#     category = {'categoryParentId': categoryParentId, 'urlKeyParent': urlKeyParent, 'subCategoryId': subCategoryId, 'subCategoryName': subCategoryName, 'urlKey': urlKey, 'urlPath': urlPath,
#                    'totalItem': totalItem, 'lastPage': lastPage, 'numOfLastPage': numOfLastPage, 'isCheck': isCheck}
    

def insertCategory(documents):
        categories = collection['category1']
        inserted = categories.insert_many(documents)
    
        return inserted


class CategorySpider(scrapy.Spider):
    name = "category"
    allowed_domains = ["tiki.vn"]
    start_urls = []
    
    category_list = []
    urlKeys = []
    checkPoint = []
    documents = []
    
    def __init__(self):

        try:
            client = MongoClient("mongodb://localhost:27017/")
            mydb = client["menuTiki"]
            collection = mydb["Menu"]
            result = collection.find({}, {'categoryParentId': 1, 'urlKey': 2, 'checkpoint': 3})
            
            for x in result:
                self.category_list.append(x['categoryParentId'])
                self.urlKeys.append(x['urlKey'])
                self.checkPoint.append(x['checkpoint'])
            
            
            for i in range(0, len(self.category_list)):
                list_url = f'https://tiki.vn/api/personalish/v1/blocks/listings?limit=40&include=advertisement&aggregations=2&category={self.category_list[i]}&page=1&urlKey={self.urlKeys[i]}'
                self.start_urls.append(list_url)
            
        except:     
            Logger.error('EEEEEEEEEERRRRRRRRROOOOOORRRRRRRR')
        finally: 
            client.close()    
     
    def store_documents(self, object):
        
        self.documents.append(dict(object))
        
        if len(self.documents) == 100:
            insertCategory(self.documents)      
            self.documents.clear()
            

    def parse(self, response):
        # Lấy response từ API 
        resp = json.loads(response.body)
        
        url = response.request.url
        
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)

        # Extract query parameters
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Get the value associated with the key "category"
        categoryParentId = query_params.get('category', [None])[0]
        urlKeyParent = query_params.get('urlKey', [None])[0]

        numOfLastPage = resp.get('paging').get('last_page')
        
        
        filters = resp.get('filters')
        category = filters[0].get('query_name')
        
        # Kiểm tra mảng lấy về có phải là danh mục con hay không?
        if category == 'category':   
            subcategorys = filters[0].get('values')
        
            for subcategory in subcategorys:
                
                subcategoryid = subcategory.get('query_value')
                url_key = subcategory.get('url_key')
                
                item_loader = ItemLoader(item=CategorySubTiki())                
        
                item_loader.add_value("categoryParentId", categoryParentId)
                item_loader.add_value("urlKeyParent", urlKeyParent)
                item_loader.add_value("subCategoryId", str(subcategoryid))
                item_loader.add_value("subCategoryName", subcategory.get('display_value'))
                item_loader.add_value("urlKey",  url_key)
                item_loader.add_value("urlPath", subcategory.get('url_path'))
                item_loader.add_value("totalItem", subcategory.get('count'))
                item_loader.add_value("lastPage", False)
                item_loader.add_value("numOfLastPage", int(numOfLastPage))
                item_loader.add_value("isCheck", False)
                               
                # Load the item and append it to the list
                self.store_documents(object=item_loader.load_item())    

                yield scrapy.Request(
                    url=f'https://tiki.vn/api/personalish/v1/blocks/listings?limit=40&include=advertisement&aggregations=2&category={subcategoryid}&page=1&urlKey={url_key}',
                    callback=self.parse_init,
                    errback=self.errback_httpbin,
                    dont_filter=True
                )              
        else: 
            Logger.info('There are no subcategories 1 !')   
            
            # total_item = resp.get('paging').get('total') 
                      
            item_loader = ItemLoader(item=CategorySubTiki())
        
            item_loader.add_value("categoryParentId", categoryParentId)
            item_loader.add_value("urlKeyParent", urlKeyParent)
            item_loader.add_value("subCategoryId", str('0'))
            item_loader.add_value("subCategoryName", 'unidentified')
            item_loader.add_value("urlKey",  'unidentified')
            item_loader.add_value("urlPath", 'unidentified')
            item_loader.add_value("totalItem", resp.get('paging').get('total'))
            item_loader.add_value("lastPage", True)
            item_loader.add_value("numOfLastPage", int(numOfLastPage))
            item_loader.add_value("isCheck", False)

            # Load the item and append it to the list
            self.store_documents(object=item_loader.load_item())    
                
    def parse_init(self, response):
        # Lấy response từ API
        resp = json.loads(response.body)
        
        numOfLastPage = resp.get('paging').get('last_page')
        
        filters = resp.get('filters')
        subcategorys = filters[0].get('values')
        
        for subcategory in subcategorys:
            
            subcategoryid = subcategory.get('query_value')
            url_key = subcategory.get('url_key')
            
            yield scrapy.Request(
                url=f'https://tiki.vn/api/personalish/v1/blocks/listings?limit=40&include=advertisement&aggregations=2&category={subcategoryid}&page=1&urlKey={url_key}',
                callback=self.parse_subcategory,
                errback=self.errback_httpbin,
                dont_filter=True
            ) 
    
    def parse_subcategory(self, response):
        # Lấy response từ API
        resp = json.loads(response.body)
        
        url = response.request.url
        
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)

        # Extract query parameters
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Get the value associated with the key "category"
        categoryCurrentId = query_params.get('category', [None])[0]
        urlKeyCurrent = query_params.get('urlKey', [None])[0]
        
        numOfLastPage = resp.get('paging').get('last_page')
        # print(numOfLastPage)
        
        filters = resp.get('filters')
        check_category = filters[0].get('query_name')
        
        if check_category == 'category': 
                        
            subcategorys = filters[0].get('values')
            
            for subcategory in subcategorys:
                
                subcategoryid = subcategory.get('query_value')
                url_key = subcategory.get('url_key')
            
                item_loader = ItemLoader(item=CategorySubTiki())
        
                item_loader.add_value("categoryParentId", categoryCurrentId)
                item_loader.add_value("urlKeyParent", urlKeyCurrent)
                item_loader.add_value("subCategoryId", str(subcategoryid))
                item_loader.add_value("subCategoryName", subcategory.get('display_value'))
                item_loader.add_value("urlKey",  url_key)
                item_loader.add_value("urlPath", subcategory.get('url_path'))
                item_loader.add_value("totalItem", subcategory.get('count'))
                item_loader.add_value("lastPage", False)
                item_loader.add_value("numOfLastPage", int(numOfLastPage))
                item_loader.add_value("isCheck", False)
                               
                # Load the item and append it to the list
                self.store_documents(object=item_loader.load_item())     
                
                yield scrapy.Request(
                    url=f'https://tiki.vn/api/personalish/v1/blocks/listings?limit=40&include=advertisement&aggregations=2&category={subcategoryid}&page=1&urlKey={url_key}',
                    callback=self.parse_subcategory,
                    errback=self.errback_httpbin,
                    dont_filter=True
                ) 
                
        else:
            Logger.info('There are no subcategories 2!')     
                
            # total_item = resp.get('paging').get('total')
                
            item_loader = ItemLoader(item=CategorySubTiki())
        
            item_loader.add_value("categoryParentId", categoryCurrentId)
            item_loader.add_value("urlKeyParent", urlKeyCurrent)
            item_loader.add_value("subCategoryId", str('0'))
            item_loader.add_value("subCategoryName", 'unidentified')
            item_loader.add_value("urlKey",  'unidentified')
            item_loader.add_value("urlPath", 'unidentified')
            item_loader.add_value("totalItem", resp.get('paging').get('total'))
            item_loader.add_value("lastPage", True)
            item_loader.add_value("numOfLastPage", int(numOfLastPage))
            item_loader.add_value("isCheck", False)
                
            # Load the item and append it to the list
            self.store_documents(object=item_loader.load_item())      
                               
            
    # Xử lý sử kiện khi gặp lỗi trong quá trình chuyển trang        
    def errback_httpbin(self, failure):
        Logger.error('EEEEEEEEEERRRRRRRRRRRRRRRROOOOOOOOOORRRRRR')    
        
        
        