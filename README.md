# 1. 环境配置
## 1.1 爬虫部分软件包版本
- Python 3.8.13
- Scrapy 2.6.2
- Scrapy-redis 0.7.3
- pymongo 4.2.0
- redis 4.3.4
## 1.2 数据库
- MongoDB
- Redis
## 1.3 前后端交互
### 前端
- jinja2
- Echarts
### 后端
- flask 2.2.2
## 1.4 IP代理池
&ensp;&ensp;参考：[https://github.com/jhao104/proxy_pool](https://github.com/jhao104/proxy_pool)进行配置。
# 2. 项目文件目录
**---FlaskProject（数据可视化代码）**<br>
------static（用到的静态资源）<br>
------templates（前端展示模板）<br>
------app.py（后端代码）<br>
------data.txt（爬取到的数据示例）<br>
------wordCloud.py（生成词云代码）<br>
**---Master（主机端的代码）**<br>
------main.py（将数据从redis中取出，放入到MongoDB）<br>
**---Pic（运行效果图）**<br>
**---proxy_pool（IP代理池）**<br>
**---Slave（从机端的代码）**<br>
------movies<br>
---------spiders<br>
------------douban_redis.py（爬取数据的主要代码）<br>
---------middlewares.py（中间件，实现IP代理、动态User-Agent等功能）<br>
---------settings.py（爬虫的相关配置）<br>
# 3. 项目配置过程
&ensp;&ensp;项目整体基于分布式的思想设计，分为**主机端代码**和**从机端代码。**
## 3.1 从机
&ensp;&ensp;从机负责执行爬虫程序，从网站爬取数据并存储到主机的Redis数据库中。Redis数据库可以记录爬取的url进度，因此爬虫程序可以中途暂停，从机数目可以任意设置，并且所有从机都执行相同的代码。<br>
&ensp;&ensp;在进行项目测试的时候可以通过在一台电脑上配置虚拟机，从而实现分布式的效果。虚拟机推荐使用[CentOS 7](http://isoredirect.centos.org/centos/7/isos/x86_64/)系统，系统轻量化、占用资源少。从机需要在`settings.py`文件中设置主机的IP和端口。<br>
&ensp;&ensp;从机环境配置完成后，cd到`spiders`文件夹下运行：`scrapy runspider douban_redis.py`命令可以启动从机程序，从机程序启动后会等待主机发放起始url。<br>
## 3.2 主机
&ensp;&ensp;主机负责维护Redis数据库，并将Redis数据库中的数据存储到MongoDB数据库中。<br>
&ensp;&ensp;启动Redis服务后，在`redis-cli.exe`中运行：`lpush douban:start_urls https://movie.douban.com/top250`命令即可在Redis数据库中插入起始url，插入成功后从机会自动开始爬取程序。<br>
&ensp;&ensp;主机端运行代理池`proxy_pool`下的代码可获取免费代理IP，并存入`redis`数据库中。<br>
&ensp;&ensp;主机端的main.py用于实现取数据的功能，可以将Redis数据库中的数据取出，放入到MongoDB数据库中。
## 3.3 可视化
&ensp;&ensp;安装flask后，在主机端打开`FlaskProject`文件，运行`app.py`即可启动后端服务。启动后端服务后，在浏览器访问在本机默认IP:端口`http://127.0.0.1:5000/`即可看到可视化效果。<br>
## 3.4 IP代理池
&ensp;&ensp;项目参考：[https://github.com/jhao104/proxy_pool](https://github.com/jhao104/proxy_pool)<br>
&ensp;&ensp;参考说明配置完环境后运行以下命令可以启动IP池程序。<br>
```
# 启动调度程序
python proxyPool.py schedule

# 启动webApi服务
python proxyPool.py server
```
# 4. 运行截图
## 4.1 从机运行
### 从机爬虫程序
![从机爬虫程序](https://github.com/CoderDon/Crawler/raw/main/Pic/slave.jpg)
## 4.2 主机数据库
### Redis数据库缓存URL
![Redis数据库缓存URL](https://github.com/CoderDon/Crawler/raw/main/Pic/redis_data.jpg)
### Redis缓存代理IPs
![Redis缓存代理IPs](https://github.com/CoderDon/Crawler/raw/main/Pic/proxy.jpg)
### MongoDB数据库
![MongoDB数据库](https://github.com/CoderDon/Crawler/raw/main/Pic/mongoDB_data.jpg)
## 4.3 可视化
### 首页
![首页](https://github.com/CoderDon/Crawler/raw/main/Pic/index.jpg)
### 电影
![电影](https://github.com/CoderDon/Crawler/raw/main/Pic/movies.jpg)
### 评分
![评分](https://github.com/CoderDon/Crawler/raw/main/Pic/score.jpg)
### 词云
![词云](https://github.com/CoderDon/Crawler/raw/main/Pic/words.jpg)