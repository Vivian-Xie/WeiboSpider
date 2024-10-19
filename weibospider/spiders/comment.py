import json
from scrapy import Spider, Request
from spiders.common import parse_user_info, parse_time, url_to_mid

class CommentSpider(Spider):
    name = "comment"
    custom_settings = {
        'LOG_LEVEL': 'INFO',  # Setting log level to INFO to reduce clutter
    }

    def __init__(self, *args, **kwargs):
        super(CommentSpider, self).__init__(*args, **kwargs)
        self.unique_nicknames = set()  # Use a set to store unique nicknames

    def start_requests(self):
        tweet_ids = ['OAaPqcG7M']
        for tweet_id in tweet_ids:
            mid = url_to_mid(tweet_id)
            url = f"https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={mid}&is_show_bulletin=2&is_mix=0&count=20"
            yield Request(url, callback=self.parse, meta={'source_url': url})

    def parse(self, response, **kwargs):
        data = json.loads(response.text)
        for comment_info in data['data']:
            item = self.parse_comment(comment_info)
            nick_name = item['comment_user']['nick_name']
            self.unique_nicknames.add(nick_name)
            if 'more_info' in comment_info:
                url = f"https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={comment_info['id']}&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id=0&count=100"
                yield Request(url, callback=self.parse, priority=20)
        if data.get('max_id', 0) != 0 and 'fetch_level=1' not in response.url:
            url = response.meta['source_url'] + '&max_id=' + str(data['max_id'])
            yield Request(url, callback=self.parse, meta=response.meta)
        else:
            # Once all pages have been scraped, write unique nicknames to the file
            self.write_nicknames_to_file()

    def write_nicknames_to_file(self):
        with open('unique_comments.txt', 'w', encoding='utf-8') as file:
            sorted_nicknames = sorted(self.unique_nicknames)
            for index, nick in enumerate(sorted_nicknames, start=1):
                file.write(f"{index}. {nick}\n")  # Write each unique nickname with an index

    @staticmethod
    def parse_comment(data):
        """
        解析comment
        """
        item = dict()
        item['created_at'] = parse_time(data['created_at'])
        item['_id'] = data['id']
        item['like_counts'] = data['like_counts']
        item['ip_location'] = data.get('source', '')
        item['content'] = data['text_raw']
        item['comment_user'] = parse_user_info(data['user'])
        if 'reply_comment' in data:
            item['reply_comment'] = {
                '_id': data['reply_comment']['id'],
                'text': data['reply_comment']['text'],
                'user': parse_user_info(data['reply_comment']['user']),
            }
        return item
