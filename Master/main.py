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

def test():
    r = redis.Redis(host='localhost', port=6379, db=0)
    # 取出所有键值
    r.hkeys('use_proxy')
    # 删除指定键值对
    # r.hdel('use_proxy', '183.250.163.175:9091')
    # 先通过key拿到value
    # r.hget('use_proxy', '222.138.64.93:9091')
    [i.decode('utf-8') for i in r.hkeys('use_proxy') if json.loads(r.hget('use_proxy', i.decode('utf-8')).decode('utf-8'))['https'] == True]
    value = json.loads(r.hget('use_proxy', '222.138.64.93:9091').decode('utf-8'))
    value['fail_count'] += 1
    new_value = str(value).replace("'", '"')
    new_value = new_value.replace('True', 'true')
    new_value = new_value.replace('False', 'false')
    # 然后根据key value修改值
    r.hset('use_proxy', '222.138.64.93:9091', str(value).replace("'",'"').replace('False', 'false').replace('True', 'true'))
    # 删除指定键值对

if __name__ == '__main__':
    # main()
    test()