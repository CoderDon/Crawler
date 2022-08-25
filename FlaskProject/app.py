from flask import Flask, render_template, make_response,jsonify
import pymongo

app = Flask(__name__)

def myCollection():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.movies
    collection = db.douban
    return collection

@app.route('/')
def home():
    return index()

@app.route('/index')
def index():
    #电影 评分 词汇 团队成员
    movies_num = 0
    votes_num = 0
    words_num = 11655
    team_num = 8
    for item in myCollection().find():
        movies_num += 1
        votes_num += int(item['comment_num'])
    votes_num = int(votes_num / 10000)
    return render_template("index.html",movies_num=movies_num,votes_num=votes_num,words_num=words_num,team_num=team_num)

@app.route('/movie')
def movie():
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

    cursor = myCollection().find(query, projection=projection)
    movies = []
    for doc in cursor:
        movies.append({
            'rank': int(doc['rank']),
            'link': doc['page_url'],
            'title': doc['title'],
            'score': doc['score'],
            'comment_num': doc['comment_num'],
            'directed_by': doc['directedBy'],
            # 'actors': doc['actors'],
            'comment': doc['comment'],
            'year': doc['year'],
        })
    movies.sort(key=lambda x: x['rank'], reverse=False)

    return render_template("movie.html",movies = movies)


@app.route('/word')
def word():
    return render_template("word.html")

@app.route('/score')
def score():
    # sql = "select score,count(score) from movie250 group by score"
    pipeline = [
        {
            u"$group": {
                u"_id": {
                    u"score": u"$score"
                },
                u"COUNT(score)": {
                    u"$sum": 1
                }
            }
        },
        {
            u"$project": {
                u"score": u"$_id.score",
                u"COUNT(score)": u"$COUNT(score)",
                u"_id": 0
            }
        }
    ]
    cursor = myCollection().aggregate(pipeline, allowDiskUse=True)
    score = []  # 评分
    num = []  # 每个评分统计出的电影数量
    score_num = {}
    for doc in cursor:
        score.append(doc['score'])
        score_num[doc['score']] = doc['COUNT(score)']
    score.sort()
    for count in range(len(score_num)):
        num.append(score_num[score[count]])
        count += 1

    return render_template("score.html",score=score,num=num)

if __name__ == '__main__':
    app.run(debug=True)