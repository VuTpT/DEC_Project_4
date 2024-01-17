import scrapy
import json
import datetime

from pymongo import MongoClient, errors

from itemloaders import ItemLoader
from scrapy.loader import ItemLoader
from ..items import ProductTiki

import logging

Logger = logging.getLogger()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
collection = client['menuTiki']

# Storing data into a database
def insertProduct(documents):
        products = collection['products5']
        try:
            inserted = products.insert_many(documents)
        except errors.BulkWriteError as e:
            for error in e.details["writeErrors"]:
                print(f"Error: {error}")
        
        return inserted

class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["tiki.vn"]
    start_urls = []

    category_list = []
    urlKeys = []
    numOfLastPage = []
    documents = []
     
    def __init__(self):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            mydb = client["menuTiki"]
            collection = mydb["subCategories2"]

            # Count Operation
            count = collection.count_documents({'lastPage': True, 'urlKeyParent': {'$ne': "None"} })

            # Check if there are documents with 'lastPage' equal to 'True' and  'urlKeyParent' not equal 'None'
            if count > 0:
                # Aggregation Operation
                result_cursor = collection.aggregate([
                    {'$match': {'lastPage': True, 'urlKeyParent': {'$ne': "None"}}},
                    {'$project': {'_id': 'null', 'categoryParentId': '$categoryParentId', 'urlKeyParent': '$urlKeyParent', 'numOfLastPage': '$numOfLastPage'}}
                ])

                # Iterate over the cursor to access the results
                result_list = list(result_cursor)
                
                for result in result_list:
                    self.category_list.append(result['categoryParentId'])
                    self.urlKeys.append(result['urlKeyParent'])
                    self.numOfLastPage.append(result['numOfLastPage'])
                            
                for i in range(0, len(self.category_list)):
                    for page in range(0, int(self.numOfLastPage[i])):
                        list_url = f'https://tiki.vn/api/personalish/v1/blocks/listings?limit=40&include=advertisement&aggregations=2&category={self.category_list[i]}&page={str(page + 1)}&urlKey={self.urlKeys[i]}'
                        self.start_urls.append(list_url)
                    
            else:
                Logger.info("EEEEEEEEERRRRRRRRRRROOOOOORRRRRRRRR")

        except Exception as e:
            Logger.error(f'Error: {e}')

        finally:
            client.close()       

    def store_documents(self, object):
        
        self.documents.append(dict(object))
        if len(self.documents) == 100:
            insertProduct(self.documents)      
            self.documents.clear()

    def parse(self, response):
        # Lấy response từ API 
        resp = json.loads(response.body)
        
        dataList = resp.get('data')
        
        for data in dataList:
            
            productId = data.get('id')
            seller_product_id = data.get('seller_product_id')
            amplitude =  data.get('visible_impression_info').get('amplitude')
            
            item_loader = ItemLoader(item=ProductTiki())                
        
            item_loader.add_value("productId", productId)
            item_loader.add_value("url_path", data.get('url_path'))
            item_loader.add_value("seller_product_id", seller_product_id)
            item_loader.add_value("url", f'https://tiki.vn/api/v2/products/{productId}?spid={seller_product_id}')
            item_loader.add_value("category_l1_name", amplitude.get('category_l1_name'))
            item_loader.add_value("category_l2_name", amplitude.get('category_l2_name'))
            item_loader.add_value("primary_category_name", amplitude.get('primary_category_name'))
            item_loader.add_value("isCheck", False)
            item_loader.add_value("createdDate", datetime.datetime.utcnow())
            item_loader.add_value("updatedDate", datetime.datetime.utcnow())
                               
            # Load the item and append it to the list
            self.store_documents(object=item_loader.load_item())
            # insertProduct(documents=item_loader.load_item())
            
            # insertProduct(productId, url_path, url, category_l1_name, category_l2_name, primary_category_name, seller_product_id, isCheck, createdDate, updatedDate)
            