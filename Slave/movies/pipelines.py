# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from pymysql import connect
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from scrapy.exceptions import DropItem

class MongoMoviesPipeline:
    def open_spider(self,spider):
        self.client = pymongo.MongoClient()

    def process_item(self, item, spider):
        # self.client.movies.douban.replace_one(filter={"page_url":item["page_url"]},replacement=item,upsert=True)
        return item

    def close_spider(self,spider):
        self.client.close()

class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['image_urls'], meta={"image_name": item['image_name']})

    def file_path(self, request, response=None, info=None, *, item=None):
        file_name = request.meta['image_name'] + ".jpg"
        return file_name

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item

# class MysqlMoviesPipeline:
#     def open_spider(self,spider):
#         self.client = connect(host='localhost',port='3306',user='root',password='123456',db='movies',charset='utf8')
#         self.cursor = self.client.cursor()
#
#     def process_item(self, item, spider):
#         self.client.movies.douban.insert_one(item)
#         return item
#
#     def close_spider(self,spider):
#         self.cursor.close()
#         self.client.close()
