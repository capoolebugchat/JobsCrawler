import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import JD_Item
from w3lib.html import remove_tags
class IndeedSpider(CrawlSpider):

    # Initiate variables
    name = 'IndeedSpider'
    site = 'Indeed'
    allowed_domains = ['vn.indeed.com']
    start_urls = ['http://vn.indeed.com/']

    # (For internal use) XPath and rules for links extracting
    next_page_xpath = '//ul[@class="pagination-list"]/li[6]'
    link_to_jd_xpath = '//div[@id="mosaic-zone-jobcards"]'

    # Rules for spider: follow with link to next site to continue scraping,
    # parse each JD with parse_jd,
    # process_links is to modify link to avoid 403
    rules = [
        Rule(link_extractor=LinkExtractor(allow='/jobs', restrict_xpaths=next_page_xpath), follow=True),
        Rule(link_extractor=LinkExtractor(allow='/rc/', restrict_xpaths=link_to_jd_xpath),
             callback='parse_jd', process_links='process_links')
    ]

    def process_links(self, links):
        for i in range(len(links)):
            links[i].url = "https://vn.indeed.com/viewjob?"+links[i].url.split('?')[1].split('&')[0]
        return links

    def __init__(self):
        super(IndeedSpider, self).__init__()

        with open('query.txt', 'r') as rf:
            self.query = rf.readline()

        # Start urls converter from query
        start_urls = []
        query_words = self.query.split(' ')
        patch = query_words[0]
        for word in query_words[1:]:
            patch += '+'
            patch += word
        start_url = 'https://vn.indeed.com/jobs?q=' + patch + '&l=Ha+Noi'
        start_urls.append(start_url)
        self.start_urls = start_urls

    def parse_jd(self, response):

        # (Internal use only) XPath of data
        title_xpath = '//div[@class="jobsearch-DesktopStickyContainer"]//h1'
        metadata_xpath = '//div[@class="jobsearch-DesktopStickyContainer"]//div[not(child::*)]'
        data_xpath = '//div[@id="jobDescriptionText"]'

        # IDents of JD
        url = response.request.url
        title = remove_tags(response.selector.xpath(title_xpath).get())
        raw_metadata = response.selector.xpath(metadata_xpath).getall()
        metadata = []
        for datum in raw_metadata:
            if 'reviews' in datum:
                continue
            elif remove_tags(datum) == '':
                continue
            elif 'Read what people' in datum:
                continue
            else:
                metadata.append(remove_tags(datum))
        company = metadata[0]

        # metadata
        location = metadata[1]

        # data getting
        data = remove_tags(response.selector.xpath(data_xpath).get()).split('\n')

        # Initiate Item for the scraped information
        IDents = {
            'Site': self.site,
            'URL': response.request.url,
            'Title': title,
            'Company': company
        }
        metadata = {
            'Location': location,
        },
        data = {
            'JD': data
        }

        yield JD_Item(IDents=IDents, metadata=metadata, data=data)