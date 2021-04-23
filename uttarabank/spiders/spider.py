import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import UuttarabankItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'
base = 'https://www.uttarabank-bd.com/index.php/home/news/{}'

class UuttarabankSpider(scrapy.Spider):
	now = datetime.datetime.now()
	year = now.year
	name = 'uttarabank'
	start_urls = [base.format(year)]

	def parse(self, response):
		yield response.follow(response.url, self.parse_post, dont_filter=True)

		if self.year > 2016:
			self.year -= 1
			yield response.follow(base.format(self.year), self.parse)

	def parse_post(self, response):
		articles = response.xpath('//div[@class="tabscontent"]//div[@class="row"]')
		length = len(articles)

		for index in range(length):
			item = ItemLoader(item=UuttarabankItem(), response=response)
			item.default_output_processor = TakeFirst()

			date = response.xpath(f'(//span[@style="color:#ff0000; font-size:12px;"])[{index + 1}]//text()').get()
			title = response.xpath(f'(//div[@class="floatleft col75"]/span[@title="Project Details"])[{index + 1}]//text()').get()
			content = response.xpath(f'(//div[@class="eleven columns row"])[{index + 1}]//text()').getall()
			content = [p.strip() for p in content if p.strip()]
			content = re.sub(pattern, "",' '.join(content))

			item.add_value('title', title)
			item.add_value('link', response.url)
			item.add_value('content', content)
			item.add_value('date', date)

			yield item.load_item()
