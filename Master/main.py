import redis
import pymongo
import json

def main():
    r = redis.Redis(host='localhost',port=6379,db=0)
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.movies
    collection = db.douban
    while True:
        source, data = r.blpop(["douban_redis:items"])
        item = json.loads(data)
        print(item)
        collection.replace_one(filter={"rank":item["rank"]},replacement=item,upsert=True)

if __name__ == '__main__':
    main()