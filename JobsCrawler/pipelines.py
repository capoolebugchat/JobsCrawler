# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import datetime
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter

class JDsPipeline:
    def process_item(self, item, spider):
        return item

class JSONExportPipeline:

    count_id = 0
    count_cb = 0

    def __init__(self):
        with open('query.txt', 'r') as query:
            qr = query.readline().replace(' ','')
        time = ('Time:'+'"'+str(datetime.datetime.now().__getattribute__('year')) + '/'
                + str(datetime.datetime.now().__getattribute__('day')) + '/'
                + str(datetime.datetime.now().__getattribute__('month')) + ' '
                + str(datetime.datetime.now().__getattribute__('hour')) + ':'
                + str(datetime.datetime.now().__getattribute__('minute')) + ':'
                + str(datetime.datetime.now().__getattribute__('second')) + '"'
                )

        self.fileCB = open('Data/' + 'CareerBuilder' + qr + "result.json", 'wb')
        self.fileCB.write(bytes(time, encoding='utf-8'))
        self.fileCB.write(bytes('\n', encoding='utf-8'))
        self.exporterCB = JsonItemExporter(self.fileCB, encoding='utf-8', ensure_ascii=False, indent=4)
        self.exporterCB.start_exporting()

        self.fileID = open('Data/' + 'Indeed' + qr + "result.json", 'wb')
        self.fileID.write(bytes(time, encoding='utf-8'))
        self.fileID.write(bytes('\n', encoding='utf-8'))
        self.exporterID = JsonItemExporter(self.fileID, encoding='utf-8', ensure_ascii=False, indent=4)
        self.exporterID.start_exporting()

    '''
    def close_spider(self, spider):
        if spider.name == 'CareerBuilderSpider':
            self.fileCB.write(bytes("\nScraped:%s\n" % str(self.count_cb), encoding='utf-8'))
            self.exporterCB.finish_exporting()
            self.fileCB.close()
        if spider.name == 'IndeedSpider':
            self.fileID.write(bytes("\nScraped:%s\n" % str(self.count_id), encoding='utf-8'))
            self.exporterID.finish_exporting()
            self.fileID.close()
    '''

    def process_item(self, item, spider):
        if item['IDents']['Site'] == 'CareerBuilder':
            self.count_cb+=1
            self.exporterCB.export_item(item)
        if item['IDents']['Site'] == 'Indeed':
            self.count_id+=1
            self.exporterID.export_item(item)
        return item