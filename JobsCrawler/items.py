from scrapy import Item, Field

class JD_Item(Item):

    IDents = Field()
    metadata = Field()
    data = Field()
