import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.movies
collection = db.douban

query = {}
projection = {}

projection["rank"] = u"$rank"
projection["page_url"] = u"$page_url"
projection["title"] = u"$title"
projection["score"] = u"$score"
projection["comment_num"] = u"$comment_num"
projection["directedBy"] = u"$directedBy"
projection["actors"] = u"$actors"
projection["comment"] = u"$comment"
projection["year"] = u"$year"
projection["_id"] = 0

cursor = collection.find(query, projection = projection)
movies = []
for doc in cursor:
    movies.append({
        'rank':int(doc['rank']),
        'link':doc['page_url'],
        'title':doc['title'],
        'score':doc['score'],
        'comment_num':doc['comment_num'],
        'directed_by':doc['directedBy'],
        'actors':doc['actors'],
        'comment': doc['comment'],
        'year':doc['year'],
    })
    print(doc)
movies.sort(key=lambda x: x['rank'], reverse=False)
print(movies)

a = ''
a.replace('\n','')

# for i in a.values()