import sys
sys.path.append('/home/capoothebugcat/PycharmProjects/JobsCrawler/JobsCrawler')
import JobsCrawler
from JobsCrawler.spiders import IndeedSpider,CareerBuilderSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
process.crawl(IndeedSpider.IndeedSpider)
process.crawl(CareerBuilderSpider.CareerBuilderSpider)
process.start()