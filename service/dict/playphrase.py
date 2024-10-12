# -*- coding:utf-8 -*-
import os
import requests

from ..base import *

@register([u'PlayPhrase', u'PlayPhrase'])
class PlayPhrase(WebService):

    def __init__(self):
        super().__init__()

    def _get_from_api(self):
        word = self.quote_word.lower().replace(' ', '%20')
        url = f'https://www.playphrase.me/api/v1/phrases/search?q={word}&limit=1&language=en'
        
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'x-csrf-token': 'cmf6ALYjeK3Xxi1Wobc1dIitdPqz+IjROylUqKHePZ+HQCkfROzIedaKmgSWlbgJogBBpd5HpkcmvFLF'
        } 

        response = requests.get(url, headers=headers)
        if response.status_code != requests.codes.ok:
            return None

        response = response.json()

        phrases = response["phrases"]
        if len(phrases) <= 0:
            return None

        video = phrases[0]["video-url"]
        
        return self.cache_this({ 'video': video })

    @export('VIDEO')
    def fld_meaning(self):
        video = self._get_field('video')
        if video == None or video == '':
            return ''
        
        filename = get_hex_name(self.unique.lower(), video, 'mp4')
        full_path = f'/home/vagelo/.local/share/Anki2/main/collection.media/{filename}'

        if os.path.exists(full_path) or self.download(video, full_path, 5):
            return f'[sound:{filename}]'

        return ''
