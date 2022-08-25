import scrapy
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import re

class DoubanSpider(RedisCrawlSpider):
    name = 'douban_redis'
    allowed_domains = ['douban.com']
    # start_urls = ['https://movie.douban.com/top250?start=0&filter=']
    # start_urls = ['https://movie.douban.com/top250?start={}&filter='.format(num) for num in range(0, 226, 25)]
    redis_key = 'douban:start_urls'

    rules = (
        Rule(LinkExtractor(restrict_xpaths=r'//div[@class="hd"]/a'), callback='parse_info'),
        Rule(LinkExtractor(restrict_xpaths=r'//div[@class="paginator"]/a'), follow=True),
    )

    def parse_info(self, response):
        page_url = response.url
        title = response.xpath("//h1/span[@property='v:itemreviewed']/text()").extract_first()
        year = response.xpath("//h1/span[@class='year']/text()").extract_first()
        score = response.xpath("//strong[@class='ll rating_num']/text()").extract_first()
        directedBy = response.xpath("//span[@class='attrs']/a[@rel='v:directedBy']/text()").extract_first()
        actors = response.xpath("string(//span[@class='actor']/span[@class='attrs']/span)").extract_first()
        if actors == '':
            actors = response.xpath("string(//span[@class='actor']/span[@class='attrs'])").extract_first()
        movie_type = '/'.join(response.xpath("//span[@property='v:genre']/text()").extract())
        rank = re.findall(r"\d+",response.xpath("//span[@class='top250-no']/text()").extract_first())[0]
        comment_num = response.xpath("//span[@property='v:votes']/text()").extract_first()
        comments = response.xpath("//p/span[@class='short']/text()").extract()
        comment = ''
        # 任意选一条长度小于100的短评
        for cmt in comments:
            if len(cmt) < 100:
                comment = cmt
        # 没有长度小于100的短评 读取长文
        if comment == '':
            comments = response.xpath("//p/span[@class='full']/text()").extract_first()
        introduc = response.xpath("string(//div[@class='indent']/span[@class='all hidden'])").extract_first()
        if introduc == '':
            introduc = response.xpath("string(//div[@class='indent']/span[@property='v:summary'])").extract_first()
        image_url = response.xpath("//img[@title='点击看更多海报']/@src").extract_first()
        image_name = page_url.split('/')[-2]
        print(title)
        yield {
            "page_url":page_url,
            "title":title,
            "year":year,
            "score":score,
            "directedBy":directedBy,
            "actors":actors,
            "movie_type":movie_type,
            "rank":rank,
            "comment":comment,
            "comment_num":comment_num,
            "introduc":introduc,
            "image_urls": image_url,
            "image_name": image_name
        }

