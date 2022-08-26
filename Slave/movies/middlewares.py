# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
import redis
import random
from scrapy.exceptions import NotConfigured
from twisted.internet.error import ConnectError, TimeoutError
import json
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class RandomProxyMiddleWare(object):
    def __init__(self, settings):
        # 2.初始化配置及相关变量
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.proxy_key = settings.get('PROXY_REDIS_KEY')
        self.max_failed = 1

    @property
    def proxies(self):
        # return [i.decode('utf-8') for i in self.r.hkeys('use_proxy')]
        # return [i.decode('utf-8') for i in self.r.hkeys('use_proxy')
        #         if json.loads(self.r.hget('use_proxy', i.decode('utf-8')).decode('utf-8'))['https'] == True]
        return []

    @classmethod
    def from_crawler(cls, crawler):
        # 1. 创建中间件对象
        # 默认代理是启用的
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # 3. 为每个request对象分配随机的ip代理
        if self.proxies and not request.meta.get('proxy'):
            proxies_list = self.proxies
            if proxies_list:
                request.meta['proxy'] = 'https://' + random.choice(proxies_list)

    def process_response(self, request, response, spider):
        # 4. 请求成功
        # 如果proxy为空则直接返回
        if not request.meta.get('proxy'):
            return response
        cur_proxy = request.meta.get('proxy').replace('https://', '')
        # 判断ip是否被对方封禁
        if response.status in (400, 401, 403):
            # 先拿到当前ip:port对应的value
            value = json.loads(self.r.hget(self.proxy_key, cur_proxy).decode('utf-8'))
            value['fail_count'] += 1
            self.r.hset(self.proxy_key, cur_proxy,
                        str(value).replace("'", '"').replace('False', 'false').replace('True', 'true'))
        # 当某个IP的失败次数累积到一定的数量
        filed_times = json.loads(self.r.hget(self.proxy_key, cur_proxy).decode('utf-8'))['fail_count'] or 0
        if int(filed_times) >= self.max_failed:
            print('got wrong http code (%s) when use %s' % (response.status, cur_proxy))
            # 可以认为该IP被对方封禁。从代理池中将该IP删除
            self.remove_proxy(cur_proxy)
            del request.meta['proxy']
            # 返回request 将该请求重新->调度器
            return request
        return response

    def process_exception(self, request, exception, spider):
        # 4.1 请求失败
        cur_proxy = request.meta.get('proxy')
        # 请求使用代理，并且网络请求报错，认为该IP出错，删除，并重新->调度器
        if cur_proxy and isinstance(cur_proxy, (ConnectError, TimeoutError)):
            print('error (%s) occur when use proxy %s' % (exception, cur_proxy))
            self.remove_proxy(cur_proxy)
            del request.meta['proxy']
            return request

    def remove_proxy(self, proxy):
        if proxy in self.proxies:
            self.r.hdel(self.proxy_key, proxy)


class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        request.headers.setdefault(b'User-Agent', UserAgent().random)

class MoviesSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MoviesDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        # 在请求页面时伪装成站内请求，用以反 反爬虫
        referer = request.url
        if referer:
            request.headers['referer'] = referer

        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
