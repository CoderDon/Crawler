from wordcloud import WordCloud         #词云
import jieba                            #分词
from matplotlib import pyplot as plt    #绘图 数据可视化
from PIL import Image                   #图片处理
import numpy as np                      #矩阵运算
import pymongo                          #数据库

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.movies
collection = db.douban
query = {}
projection = {}

projection["title"] = u"$title"
projection["movie_type"] = u"$movie_type"
projection["directedBy"] = u"$directedBy"
projection["_id"] = 0

cursor = collection.find(query, projection = projection)
text = ""
for doc in cursor:
    for content in doc.values():
        content.replace('/',' ')
        text = text + content

cut = jieba.cut(text)
string = ' '.join(cut)
print(len(string))

img = Image.open(r'./static/img/tree.jpg')
img_array = np.array(img)   #将图片转换为数组
wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path="msyh.ttc"    #字体所在位置C:\Windows\Fonts
)
wc.generate_from_text(string)

#绘制图片

fig = plt.figure(1)
plt.imshow(wc)
plt.axis('off') #是否显示坐标轴

# plt.show()  #显示生成的词云图片
plt.savefig('./static/img/generated_tree.jpg',dpi=500)
