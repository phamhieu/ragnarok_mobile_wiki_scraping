import logging
import requests
import re
import time
import sys

import lxml.html as html
import app.services.database as db

from sqlitedict import SqliteDict


reload(sys)
sys.setdefaultencoding('utf8')


class Interface(object):
    requestSession = requests.session()
    dbManager = db.DbManager()
    dbDict = SqliteDict(dbManager.db_dir, autocommit=True)
    # update logging level
    logging.getLogger().setLevel(logging.INFO)

    def fetch_data(self, url):
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/39.0.2171.95 Safari/537.36'
                )
            }
        try:
            result = self.requestSession.get(url, headers = headers)
            if result.status_code == 200:
                return result.content
            else:
                logging.exception(
                    (
                        'Fetch data failed {} for url {}'
                    ).format(result.status_code, url)
                )
                return None
        except:
            logging.exception(
                (
                    'Fetch data exception for url {}'
                ).format(url)
            )
            return None

    def scrap_data(self, **kargs):
        raise NotImplementedError('subclasses must override scrap_data()!')

class Monster(Interface):
    def parse_monster(self, parser):
        XPATH_LINE = (
	        '//table[@class="db_data_table"]'
	        '//tr'
        )
        lines = parser.xpath(XPATH_LINE)

        if not lines:
            return None

        for line in lines:
            XPATH_ROW = (
                './/td'
            )
            rows = line.xpath(XPATH_ROW)
            if not rows:
            	continue

            XPATH_NAME = (
                './/div//a/text()'
                )
            raw_name = rows[1].xpath(XPATH_NAME)

            XPATH_URL = (
                './/div//a/@href'
                )
            raw_url = rows[1].xpath(XPATH_URL)

            XPATH_LV_HP = (
                './/div/text()'
                )
            raw_lv_hp = rows[2].xpath(XPATH_LV_HP)
            raw_lv = raw_lv_hp[0].replace('Lv', '').replace(',', '').strip()
            raw_hp = raw_lv_hp[1].replace('Hp', '').replace(',', '').strip()

            XPATH_baseexp_jobexp = (
                './/div/text()'
                )
            raw_baseexp_jobexp = rows[3].xpath(XPATH_baseexp_jobexp)
            raw_baseexp = raw_baseexp_jobexp[0].replace('Base Exp', '').replace(',', '').strip()
            raw_jobexp = raw_baseexp_jobexp[1].replace('Job Exp', '').replace(',', '').strip()

            monster = db.Monster()
            monster.name = ''.join(raw_name).strip() if raw_name else None
            monster.url = 'https://www.roguard.net' + ''.join(raw_url).strip() if raw_url else None
            monster.level = int(''.join(raw_lv).strip() if raw_lv else '0')
            monster.hp = int(''.join(raw_hp).strip() if raw_hp else '0')
            monster.base_ex = int(''.join(raw_baseexp).strip() if raw_baseexp else '0')
            monster.job_ex = int(''.join(raw_jobexp).strip() if raw_jobexp else '0')
            # logging.info('monster.name: {}'.format(monster.name))
            # logging.info('monster.url: {}'.format(monster.url))
            # logging.info('monster.level: {}'.format(monster.level))
            # logging.info('monster.hp: {}'.format(monster.hp))
            # logging.info('monster.base_ex: {}'.format(monster.base_ex))
            # logging.info('monster.job_ex: {}'.format(monster.job_ex))
            # insert to db
            self.dbManager.insert_monster(monster)

    def scrap_data(self, **kargs):
        def next_scraping_url(_pageIndex):
            BASE_URL = "https://www.roguard.net/db/monsters/?page="
            return '{}{}'.format(BASE_URL, _pageIndex)

        index = 0
        while index <= 17:
            nextId = index + 1
            url = next_scraping_url(nextId)
            logging.info('Scrap url: {}'.format(url))

            web_content = self.fetch_data(url)
            if web_content is None:
                return
            
            # logging.info('web_content: {}'.format(web_content))
            parser = html.fromstring(web_content)
            if parser is None:
                return None 

            self.parse_monster(parser)

            index += 1
            # we dont want to exploit the website
            time.sleep(3.0)
