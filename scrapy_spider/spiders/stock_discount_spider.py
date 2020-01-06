# -*- coding: utf-8 -*-
import scrapy
import csv

class StockDiscountSpider(scrapy.Spider):
	name = 'stock_discount_spider'

	def start_requests(self):
		# write header to output
		with open('stock_discounts.csv', 'w') as f:
			f.write('code,avg,min,max\n')
		
		# read stock codes
		with open('stock_codes.csv', 'r') as f:
			reader = csv.reader(f)
			code_list = list(reader)
		stock_codes = [code[0] for code in code_list]
		
		# scrap each stock code
		urls = ['https://www.indopremier.com/module/saham/include/targetprice.php?code=' + str(code) for code in stock_codes]
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		stock_code = response.url[-4:]

		# extract discounts
		i = 0
		total_disc = 0
		min_disc = 100
		max_disc = 0
		while True:
			i += 1
			disc_text = response.xpath('/html/body/div[2]/table/tbody/tr[' + str(i) + ']/td[7]/text()').get()
			if disc_text == None:
				break
			disc = float(disc_text[:-1])
			total_disc += disc
			if disc < min_disc:
				min_disc = disc
			if disc > max_disc:
				max_disc = disc
		if i > 1:
			avg_disc = total_disc / (i - 1)
			with open('stock_discounts.csv', 'a') as f:
				f.write(stock_code + ',' + str(round(avg_disc)) + ',' + str(round(min_disc)) + ',' + str(round(max_disc)) + '\n')
				# self.log(stock_code + ' avg:' + str(round(avg_disc)) + ' min:' + str(round(min_disc)) + ' max:' + str(round(max_disc)))
		
		# save html
		filename = 'html/' + stock_code + '.html'
		with open(filename, 'wb') as f:
			f.write(response.body)
