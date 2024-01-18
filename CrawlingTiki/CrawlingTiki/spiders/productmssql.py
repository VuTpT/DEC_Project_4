from typing import Any
import scrapy
import json
import pyodbc
from pymongo import MongoClient, errors
from itemloaders import ItemLoader
from scrapy.loader import ItemLoader
from ..items import ProductDetailTiki

import logging

Logger = logging.getLogger()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
collection = client['menuTiki']

# Connect to the database
connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=27.3.1.103;DATABASE=ETL;UID=sa;PWD=123456'


# Storing data into a database
def insertProductDetail(object):
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    try:
        SQL_STATEMENT = """ INSERT INTO [ETL].[dbo].[ProductDetail]([productId],[productName],[short_description],[price],[list_price],[original_price],[discount],[discount_rate],[rating_average],[review_count],[review_text],[favourite_count],[thumbnail_url],
        [has_ebook],[inventory_status],[inventory_type],[day_ago_created],[all_time_quantity_sold],
        [meta_title],[meta_description],[meta_keywords],[description],
        [images],[brand],[current_seller],[specifications],[gift_item_title],
        [highlight],[stock_item],[quantity_sold],[categories],[breadcrumbs],[return_and_exchange_policy]) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
        # Execute the query
        cursor.execute(SQL_STATEMENT, object['productId'], object['productName'], object['short_description'], object['price'], object['list_price'], object['original_price'], object['discount'], object['discount_rate'], object['rating_average'], object['review_count'], object['review_text'], object['favourite_count'], object['thumbnail_url'], 
                       object['has_ebook'], object['inventory_status'], object['inventory_type'], object['day_ago_created'], object['all_time_quantity_sold'], 
                       object['meta_title'], object['meta_description'], object['meta_keywords'], object['description'], 
                       object['images'], object['brand'], object['current_seller'], object['specifications'], object['gift_item_title'], 
                       object['highlight'], object['stock_item'], object['quantity_sold'], object['categories'], 
                       object['breadcrumbs'], object['return_and_exchange_policy'])

        # Commit the transaction
        connection.commit()
    except:
        Logger.info("ERRRRRRRRRROORRR")
    finally:    
        # Close the connection
        cursor.close()
        connection.close()



# class SavingMSSQL(object):
#     def __init__(self):
#         self.conn = None
#         self.curr = None
#         self.create_connection()
#         Logger.info("Connect database successfully!")

#     ## Create connection string with database
#     def create_connection(self):
#         server = 'localhost'
#         database = 'ETL'
#         username = 'sa'
#         password = '123456'
#         conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
#         self.conn = pyodbc.connect(conn_str)
#         self.curr = self.conn.cursor()

#     ## Storing item into database
#     def store_db(self, item):

#         try:
#             SQL_STATEMENT = """ INSERT INTO [ETL].[dbo].[ProductDetail]([productId],[productName],[short_description],[price],[list_price],[original_price],[discount],[discount_rate],[rating_average],[review_count],[review_text],[favourite_count],[thumbnail_url],[has_ebook],[inventory_status],[inventory_type],[day_ago_created],[all_time_quantity_sold],[meta_title],[meta_description],[meta_keywords],[description],[images],[brand],[current_seller],[specifications],[gift_item_title],[highlight],[stock_item],[quantity_sold],[categories],[breadcrumbs],[return_and_exchange_policy]) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
#             self.curr.execute(SQL_STATEMENT)
#             self.conn.commit()
#         except pyodbc.Error as e:
#             error_message = str(e)
#             Logger.error("Error occurred:", error_message)
#             Logger.error("SQL State:", e.args[0])
#             Logger.error("Error Message:", e.args[1])


#     ## Close cursor & connection to database 
#     def close_spider(self, spider):    
#         self.curr.close()
#         self.conn.close()



class ProductmssqlSpider(scrapy.Spider):
    name = "productmssql"
    allowed_domains = ["tiki.vn"]
    start_urls = []
    documents = []
    
    def __init__(self):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            mydb = client["menuTiki"]
            collection = mydb["products5"]

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
        # self.store_documents(object=item_loader.load_item())
        insertProductDetail(object=dict(item_loader.load_item()))
