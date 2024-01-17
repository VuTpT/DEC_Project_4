from typing import Any
import scrapy
import json
from pymongo import MongoClient
from itemloaders import ItemLoader
from scrapy.loader import ItemLoader
from ..items import ProductDetailTiki

import logging

Logger = logging.getLogger()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
collection = client['menuTiki']

# Storing data into a database
def insertProductDetail(productDetail):
    productList = collection['productDetail1']
    # inserted = productList.insert_one(dict(productDetail))
    inserted = productList.insert_many(productDetail)
    return inserted

class ProductdetailSpider(scrapy.Spider):
    name = "productdetail"
    allowed_domains = ["tiki.vn"]
    start_urls = []
    documents = []
    
    def __init__(self):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            mydb = client["menuTiki"]
            collection = mydb["products1"]

            # Count Operation
            count = collection.count_documents({'isCheck': False})

            # Check if there are documents with 'isCheck' equal to 'false'
            if count > 0:
                # Aggregation Operation
                result_cursor = collection.aggregate([
                    {'$match': {'isCheck': False}},
                    {'$project': {'_id': 'null', 'url': '$url'}}
                ])

                # Iterate over the cursor to access the results
                result_list = list(result_cursor)
                
                for i in range(0, count):
                    self.start_urls.append(str(result_list[i]['url'])) 
                    
            else:
                Logger.info("No documents with 'isCheck' equal to 'false' found, skipping aggregation")

        except Exception as e:
            Logger.error(f'Error: {e}')

        finally:
            client.close()
            
    def store_documents(self, object):
        
        self.documents.append(dict(object))
        
        if len(self.documents) == 100:
            insertProductDetail(self.documents)           
            self.documents.clear()
        
    
    def parse(self, response):
        # Lấy response từ API 
        resp = json.loads(response.body)
        
        item_loader = ItemLoader(item=ProductDetailTiki(), selector=resp)
        
        item_loader.add_value("productId", resp.get('id'))
        item_loader.add_value("productName", resp.get('name'))
        item_loader.add_value("short_description", resp.get('short_description'))
        item_loader.add_value("price", resp.get('price'))
        item_loader.add_value("list_price", resp.get('list_price'))
        item_loader.add_value("original_price", resp.get('original_price'))
        item_loader.add_value("discount", resp.get('discount'))
        item_loader.add_value("discount_rate", resp.get('discount_rate'))
        item_loader.add_value("rating_average", resp.get('rating_average'))
        item_loader.add_value("review_count", resp.get('review_count'))
        item_loader.add_value("review_text", resp.get('review_text'))
        item_loader.add_value("favourite_count", resp.get('favourite_count'))
        item_loader.add_value("thumbnail_url", resp.get('thumbnail_url'))
        item_loader.add_value("has_ebook", resp.get('has_ebook'))
        item_loader.add_value("inventory_status", resp.get('inventory_status'))
        item_loader.add_value("inventory_type", resp.get('inventory_type'))
        item_loader.add_value("day_ago_created", resp.get('day_ago_created'))
        item_loader.add_value("all_time_quantity_sold", resp.get('all_time_quantity_sold'))
        item_loader.add_value("meta_title", resp.get('meta_title'))
        item_loader.add_value("meta_description", resp.get('meta_description'))
        item_loader.add_value("meta_keywords", resp.get('meta_keywords'))
        item_loader.add_value("description", resp.get('description'))
        item_loader.add_value("images", resp.get('images'))
        item_loader.add_value("brand", resp.get('brand'))
        item_loader.add_value("current_seller", resp.get('current_seller'))
        item_loader.add_value("specifications", resp.get('specifications'))
        item_loader.add_value("gift_item_title", resp.get('gift_item_title'))
        item_loader.add_value("highlight", resp.get('highlight'))
        item_loader.add_value("stock_item", resp.get('stock_item'))
        item_loader.add_value("quantity_sold", resp.get('quantity_sold'))
        item_loader.add_value("categories", resp.get('categories'))
        item_loader.add_value("breadcrumbs", resp.get('breadcrumbs'))
        item_loader.add_value("return_and_exchange_policy", resp.get('return_and_exchange_policy'))
        
        # insertProductDetail(productDetail=item_loader.load_item())
        self.store_documents(object=item_loader.load_item())

    
        
