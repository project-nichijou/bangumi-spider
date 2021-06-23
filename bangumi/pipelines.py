# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from bangumi.items.bangumi_anime_name import BangumiAnimeNameItem
from bangumi.items.bangumi_anime_fail import BangumiAnimeFailItem
from bangumi import bangumi_settings
from bangumi.items.bangumi_anime_episode_intro import BangumiAnimeEpisodeIntroItem
from bangumi.items.bangumi_anime_episode import BangumiAnimeEpisodeItem
from bangumi.items.bangumi_anime import BangumiAnimeItem
from bangumi.items.bangumi_id import BangumiIDItem
from bangumi.database.bangumi_database import BangumiDatabase
from bangumi.database import database_settings
from itemadapter import ItemAdapter
from bs4 import BeautifulSoup

class BangumiPipeline:

	def __init__(self):
		self.config = database_settings.CONFIG
		self.database = BangumiDatabase(self.config)

	def process_item(self, item, spider):
		# define table
		type = 'fail'
		if isinstance(item, BangumiIDItem):
			table = 'bangumi_id'
			type = 'id'
			id = item['sid']
		if isinstance(item, BangumiAnimeItem):
			table = 'bangumi_anime'
			type = 'anime'
			id = item['sid']
		if isinstance(item, BangumiAnimeNameItem):
			table = 'bangumi_anime_name'
			type = 'anime_name'
			id = item['sid']
		if isinstance(item, BangumiAnimeEpisodeItem):
			table = 'bangumi_anime_episode'
			type = 'episode'
			id = item['eid']
		if isinstance(item, BangumiAnimeEpisodeIntroItem):
			table = 'bangumi_anime_episode'
			type = 'episode_intro'
			id = item['eid']
		if isinstance(item, BangumiAnimeFailItem):
			table = 'request_failed'
		# adjust links
		values = dict(item)
		for key in values.keys():
			if str(key).endswith('HTML') and values[key] != None:
				values[key] = BangumiPipeline.convert_to_absoulte(values[key])
		# write section
		self.save_to_database(table, values)
		# delete fail if exist
		if not type == 'fail':
			self.database.del_fail(type=type, id=id)
		return item

	def convert_to_absoulte(html: str):
		soup = BeautifulSoup(html, 'lxml')
		links = soup.findAll('a')
		for link in links:
			if link.attrs['href'].startswith('/'):
				link.attrs['href'] = f'{bangumi_settings.ORIGIN_URL}{link.attrs["href"]}'
		return str(soup)

	def save_to_database(self, table: str, values: dict):
		self.database.write(table, values)
