import json
from scrapy import Spider, Request
from spiders.common import parse_tweet_info, url_to_mid

class RepostSpider(Spider):
    name = "repost"
    custom_settings = {
        'LOG_LEVEL': 'INFO',  # Reduce the amount of logged info to declutter the output
    }

    def __init__(self, *args, **kwargs):
        super(RepostSpider, self).__init__(*args, **kwargs)
        self.unique_nicks = set()  # Use a set to store unique nicknames

    def start_requests(self):
        tweet_ids = ['Ouf8067R1']
        for tweet_id in tweet_ids:
            mid = url_to_mid(tweet_id)
            url = f"https://weibo.com/ajax/statuses/repostTimeline?id={mid}&page=1&moduleID=feed&count=10"
            yield Request(url, callback=self.parse, meta={'page_num': 1, 'mid': mid})

    def parse(self, response, **kwargs):
        data = json.loads(response.text)
        for tweet in data['data']:
            item = parse_tweet_info(tweet)
            # Extract nickname and add to the set for uniqueness
            nick_name = item['user']['nick_name']
            self.unique_nicks.add(nick_name)  # Adds only if not already present
            yield item
        if data['data']:
            mid, page_num = response.meta['mid'], response.meta['page_num']
            page_num += 1
            url = f"https://weibo.com/ajax/statuses/repostTimeline?id={mid}&page={page_num}&moduleID=feed&count=10"
            yield Request(url, callback=self.parse, meta={'page_num': page_num, 'mid': mid})
        else:
            # Once all pages have been scraped, write unique nicknames to the file
            self.write_nicks_to_file()

    def write_nicks_to_file(self):
        with open('unique_nick_names.txt', 'w', encoding='utf-8') as file:
            for index, nick in enumerate(sorted(self.unique_nicks), start=1):
                file.write(f"{index}. {nick}\n")  # Write each unique nickname with an index

    def url_to_mid(self, tweet_id):
        # Implement based on the actual conversion logic needed
        return tweet_id

    def parse_tweet_info(self, tweet):
        # Actual parsing logic based on the JSON structure of the tweet
        return {
            'user': {
                'nick_name': 'example_nick'  # This should be replaced with the correct field name
            }
        }
