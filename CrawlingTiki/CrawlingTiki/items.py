# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from w3lib.html import remove_tags
from itemloaders.processors import TakeFirst, MapCompose


def remove_html_tags(value):
    # # Remove HTML tags and replace them with spaces
    # return remove_tags(value).strip().replace('\r', ' ')

      # Define a regular expression to match HTML tags
    html_tags = re.compile('<.*?>')
    
    # Remove HTML tags and replace them with spaces
    clean_string = re.sub(html_tags, ' ', value)
    
    # Replace multiple spaces with a single space
    clean_string = re.sub(' +', ' ', clean_string)
    
    # Remove leading and trailing spaces
    clean_string = clean_string.strip()
    
    return clean_string


class MenuTiki(scrapy.Item):
    categoryParentId = scrapy.Field()
    categoryName = scrapy.Field()
    urlKey = scrapy.Field() 
    link = scrapy.Field() 
    checkpoint = scrapy.Field()
    createdDate = scrapy.Field()
    updatedDate = scrapy.Field()


class CategorySubTiki(scrapy.Item):
    categoryParentId = scrapy.Field(default=None, output_processor=TakeFirst())
    urlKeyParent = scrapy.Field(default=None, output_processor=TakeFirst())
    subCategoryId = scrapy.Field(default=None, output_processor=TakeFirst())
    subCategoryName = scrapy.Field(default=None, output_processor=TakeFirst())
    urlKey = scrapy.Field(default=None, output_processor=TakeFirst()) 
    urlPath = scrapy.Field(default=None, output_processor=TakeFirst())
    totalItem = scrapy.Field(default=None, output_processor=TakeFirst()) 
    lastPage = scrapy.Field(default=None, output_processor=TakeFirst())
    numOfLastPage = scrapy.Field(default=None, output_processor=TakeFirst())
    isCheck = scrapy.Field(default=None, output_processor=TakeFirst())
    createdDate = scrapy.Field(default=None, output_processor=TakeFirst())
    updatedDate = scrapy.Field(default=None, output_processor=TakeFirst())
   
class ProductTiki(scrapy.Item):
    productId = scrapy.Field(default=None, output_processor=TakeFirst())
    url_path = scrapy.Field(default=None, output_processor=TakeFirst())
    seller_product_id = scrapy.Field(default=None, output_processor=TakeFirst())
    url = scrapy.Field(default=None, output_processor=TakeFirst())
    category_l1_name = scrapy.Field(default=None, output_processor=TakeFirst())
    category_l2_name = scrapy.Field(default=None, output_processor=TakeFirst()) 
    primary_category_name = scrapy.Field(default=None, output_processor=TakeFirst())
    isCheck = scrapy.Field(default=None, output_processor=TakeFirst())
    createdDate = scrapy.Field(default=None, output_processor=TakeFirst())
    updatedDate = scrapy.Field(default=None, output_processor=TakeFirst())

    
class ProductDetailTiki(scrapy.Item):
    productId =scrapy.Field(default=None, output_processor=TakeFirst())
    productName =scrapy.Field(default=None, output_processor=TakeFirst())
    short_description =scrapy.Field(default=None, output_processor=TakeFirst())
    price =scrapy.Field(default=None, output_processor=TakeFirst())
    list_price =scrapy.Field(default=None, output_processor=TakeFirst())
    original_price =scrapy.Field(default=None, output_processor=TakeFirst())
    discount =scrapy.Field(default=None, output_processor=TakeFirst())
    discount_rate =scrapy.Field(default=None, output_processor=TakeFirst())
    rating_average =scrapy.Field(default=None, output_processor=TakeFirst())
    review_count =scrapy.Field(default=None, output_processor=TakeFirst())
    review_text =scrapy.Field(default=None, output_processor=TakeFirst())
    favourite_count =scrapy.Field(default=None, output_processor=TakeFirst())
    thumbnail_url =scrapy.Field(default=None, output_processor=TakeFirst())
    has_ebook =scrapy.Field(default=None, output_processor=TakeFirst())
    inventory_status =scrapy.Field(default=None, output_processor=TakeFirst())
    inventory_type =scrapy.Field(default=None, output_processor=TakeFirst())
    day_ago_created =scrapy.Field(default=None, output_processor=TakeFirst())
    all_time_quantity_sold =scrapy.Field(default=None, output_processor=TakeFirst())
    meta_title =scrapy.Field(default=None, output_processor=TakeFirst())
    meta_description =scrapy.Field(default=None, output_processor=TakeFirst())
    meta_keywords =scrapy.Field(default=None, output_processor=TakeFirst())
    description = scrapy.Field(default=None, input_processor = MapCompose(remove_html_tags), output_processor=TakeFirst())
    images =scrapy.Field(default=None, output_processor=TakeFirst())
    brand =scrapy.Field(default=None, output_processor=TakeFirst())
    current_seller =scrapy.Field(default=None, output_processor=TakeFirst())
    specifications =scrapy.Field(default=None, output_processor=TakeFirst())
    gift_item_title =scrapy.Field(default=None, output_processor=TakeFirst())
    highlight =scrapy.Field(default=None, output_processor=TakeFirst())
    stock_item =scrapy.Field(default=None, output_processor=TakeFirst())
    quantity_sold =scrapy.Field(default=None, output_processor=TakeFirst())
    categories =scrapy.Field(default=None, output_processor=TakeFirst())
    breadcrumbs =scrapy.Field(default=None, output_processor=TakeFirst())
    return_and_exchange_policy = scrapy.Field(default=None, input_processor = MapCompose(remove_html_tags), output_processor=TakeFirst())

class CrawlingtikiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
