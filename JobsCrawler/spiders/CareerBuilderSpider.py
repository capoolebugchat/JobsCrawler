import scrapy
import os
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from w3lib.html import remove_tags
from ..items import JD_Item

# Light preprocessing
def rm_tags_list(elements):
    for i in range(len(elements)):
        elements[i] = remove_tags(elements[i])
    return elements

class CareerBuilderSpider(CrawlSpider):

    # Initiate variables
    name = 'CareerBuilderSpider'
    site = 'CareerBuilder'
    allowed_domains = ['careerbuilder.vn']

    # Internally used variables
    JD_url_prefix = 'https://careerbuilder.vn/vi/tim-viec-lam/'
    JD_xpath      = '//div[@class="job-item  "]//a[@class="job_link"]'
    np_url_prefix = 'https://careerbuilder.vn/viec-lam/'
    np_xpath      = '//div[@class="pagination"]//li[@class="next-page"]'

    # Set spider's rules: recursive call for next page, parse each JD at parse_jd()
    rules = [
        Rule(link_extractor=LinkExtractor(allow=np_url_prefix, restrict_xpaths=np_xpath), follow=True),
        Rule(link_extractor=LinkExtractor(allow=JD_url_prefix, restrict_xpaths=JD_xpath), callback= 'parse_jD')
    ]

    # spider's query getting and links constructing
    def __init__(self):
        super(CareerBuilderSpider, self).__init__()

        with open('query.txt', 'r') as rf:
            self.query = rf.readline()

        # Start urls converter from query
        start_urls = []
        query_words = self.query.split(' ')
        patch = query_words[0]
        for word in query_words[1:]:
            patch += '-'
            patch += word
        start_url = 'https://careerbuilder.vn/viec-lam/' + patch + '-k-vi.html'
        start_urls.append(start_url)
        self.start_urls = start_urls

        ''' Move these to Pipelines
        if not os.path.exists('Data/' + self.site + '/' + self.query):
            os.makedirs('Data/' + self.site + '/' + self.query)
        '''

    # For internal uses only
    def parse_obscure_jd(self, response):
        with open('obscureLinks.txt', 'a') as obs_l_file:
            obs_l_file.write(response.request.url)
            obs_l_file.write('\n')

    # Main parser
    def parse_jD(self, response):

        # XPaths of visible data
        metadata_xpath = '//div[@class="detail-box has-background"]'
        data_xpath = '//div[@class="detail-row"]'

        # Separating layouts. Since CB uses more than 2 layouts
        # and some are damn weird man
        try:
            job_title = remove_tags(response.selector.xpath('//div[@class="job-desc"]/h1').get())
        except TypeError:
            self.parse_obscure_jd(response)
            pass

        # Go see https://careerbuilder.vn/vi/tim-viec-lam/data-analyst.35B6F20B.html
        # to inspect the clean layout (in case of changing) (God please, no)

        # Identifications of each JDs
        company_name = remove_tags(response.selector.xpath('//div[@class="job-desc"]/a').get())

        # Metadata of each JDs
        metadata = response.selector.xpath(metadata_xpath+'//li/p').getall()
        metadata = rm_tags_list(metadata)
        try:
            day_update = metadata[0]
            field = metadata[1]
            empl_type = metadata[2]
            salary = metadata[3]
            exp_req = metadata[4]
            level = metadata[5]
        except IndexError:
            self.parse_obscure_jd(response)
            pass

        # There could be or could be not a deadline of applying
        try:
            day_end = remove_tags(metadata[6])
        except IndexError:
            day_end = 'unknown'

        # Remove redundant characters
        field = field.replace('\t', '')
        field = field.replace('\r', '')
        field = field.replace('\n', '')
        field = field.strip(' ')
        exp_req = exp_req.replace('\r', '')
        exp_req = exp_req.replace('\n', '')
        exp_req = exp_req.strip(' ')

        # Data
        benefits = rm_tags_list(response.selector.xpath(data_xpath+'[1]//li').getall())
        job_desc = rm_tags_list(response.selector.xpath(data_xpath+'[2]//li').getall())
        job_reqm = rm_tags_list(response.selector.xpath(data_xpath+'[3]//li').getall())
        if not job_desc:
            job_desc = rm_tags_list(response.selector.xpath(data_xpath + '[2]//p').getall())
        if not job_reqm:
            job_reqm = rm_tags_list(response.selector.xpath(data_xpath + '[3]//p').getall())
        others = rm_tags_list(response.selector.xpath(data_xpath+'[4]//li').getall())

        # Initiate Item for the scraped information
        IDents = {
            'Site': self.site,
            'URL': response.request.url,
            'Title': job_title,
            'Company': company_name
        }
        metadata = {
            'dayUpdate': day_update,
            'field': field,
            'emplType': empl_type,
            'salary': salary,
            'expReq': exp_req,
            'level': level,
            'dayEnd': day_end
        },
        data = {
            'benefits': benefits,
            'description': job_desc,
            'requirements': job_reqm,
            'others': others
        }

        yield JD_Item(IDents=IDents, metadata=metadata, data=data)

