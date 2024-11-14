import requests
import json 
from bs4 import BeautifulSoup

from ..base import *

@register([u'Cambridge (EN)', u'Cambridge (EN)'])
class CambridgeEN(WebService):

    def __init__(self):
        super().__init__()

    def _get_from_api(self):

        word = self.quote_word.lower().replace(' ', '%20')
        url = f'https://dictionary.cambridge.org/dictionary/english/{word}'
            
        headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        } 
    
        response = requests.get(url, headers=headers)
        if response.status_code != requests.codes.ok:
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
    
        block = self.find_block(soup)
        if block is None:
            return

        meaning = self.definition(block)

        # div with ALL EXAMPLES
        dataset_example = soup.find('div', {'id': 'dataset-example'})
        examples = self.example_list(dataset_example, {'class': 'deg'})
    
        if examples is None:
            examples = self.example_list(block, {'class': 'eg deg'})
    
        results = {
            'meaning': meaning,
            'examples': examples,
            'us_phonetics': self.audio_with_phonetics(soup, 'us dpron-i'),
            'uk_phonetics': self.audio_with_phonetics(soup, 'uk dpron-i'),
            'word_type': self.description(block)
        }

        return self.cache_this(results)

     def find_block(self, soup):
        try:
            # American dictionary block
            data_block = soup.find('div', {'data-tab': 'ds-cacd'})
            if data_block is None:
                # Regular dictionary block
                data_block = soup.find('div', {'class': 'pr dictionary'})

        except AttributeError:
            return None

        return data_block

    def example_list(self, block, span_info):
        try:
            examples = block.find_all('span', span_info)
        except AttributeError:
            return None
    
        if len(examples) <= 0:
            return None
    
        li = '' 
        for example in examples:
            child_elements = [str(child) for child in example.children]
            text = ''.join(child_elements)
            li += f'<li>{text.strip()}</li>'
    
        return f'<ul>{li}</ul>'

    def definition(self, data_block):
        try:
            div = data_block.find('div', { 'class': 'def ddef_d db' })
        except AttributeError:
            return None
    
        if div is None:
            return None

        child_elements = [str(child) for child in div.children]
        definition = ''.join(child_elements)
    
        return definition

    def audio_with_phonetics(self, block, class_name):
        try:
            span = block.find('span', { 'class': class_name }) 
            source = span.find('source', { 'type': 'audio/mpeg' })
            phonetics = span.find('span', { 'class': 'pron dpron' })
        except AttributeError as err:
            return None
    
        audio = ""
        if source:
            audio = f'<audio controls src="https://dictionary.cambridge.org{source["src"]}"></audio>'
        
        result = {
            'audio': audio,
            'phonetics': phonetics.get_text(),
        }
    
        return result

    def description(self, block):
        try:
            desc = block.find('span', { 'class': 'pos dpos' }) 
            code = block.find('span', { 'class': 'gram dgram' }) 
        except AttributeError:
            return None
    
        if desc is None and code is None:
            return ''
        elif desc is None and code is not None:
            desc = ''
        elif desc is not None and code is None:
            code = ''

        return f'{desc}{code}'   

    @export('MEANING')
    def fld_meaning(self):
        val = self._get_field('meaning')
        if val == None or val == '':
            return ''
        return val

    @export('EXAMPLES')
    def fld_examples(self):
        val = self._get_field('examples')
        if val == None or val == '':
            return ''
        return val

    @export('WORD_TYPE')
    def fld_word_type(self):
        val = self._get_field('word_type')
        if val == None or val == '':
            return ''
        return val

    @export('US_PHONETICS')
    def fld_us_phonetics(self):
        val = self._get_field('us_phonetics')

        if val is None:
            return ''
        elif 'phonetics' in val:
            us_phon = val['phonetics']
            if us_phon is not None and us_phon != '':
                return us_phon
        return ''

    @export('US_AUDIO')
    def fld_us_audio(self):
        val = self._get_field('us_phonetics')

        if val is None:
            return '' 
        elif 'phonetics' in val:
            audio = val['audio']
            if audio is not None and audio != '':
                return audio 
        return ''   

    @export('UK_PHONETICS')
    def fld_uk_phonetics(self):
        val = self._get_field('uk_phonetics')

        if val is None:
            return ''
        elif 'phonetics' in val:
            us_phon = val['phonetics']
            if us_phon is not None and us_phon != '':
                return us_phon
        return ''

    @export('UK_AUDIO')
    def fld_uk_audio(self):
        val = self._get_field('uk_phonetics')

        if val is None:
            return '' 
        elif 'phonetics' in val:
            audio = val['audio']
            if audio is not None and audio != '':
                return audio 
        return '' 

    @export('CUSTOM')
    def fld_custom(self):
        us_phon = self._get_field('us_phonetics')
        word_type = self._get_field('word_type')
        if word_type is None:
            word_type = ''

        audio = ''
        phonetics = ''

        if not 'phonetics' in us_phon:
            pass
        elif us_phon['phonetics'] is not None:
            phonetics = f"<span class='phonetics'>{us_phon['phonetics']}</span>"

        if not 'audio' in us_phon:
            pass
        elif us_phon['audio'] is not None:
            audio = us_phon['audio']

        result = f"<div>{''.join([audio, phonetics, word_type])</div>"
        return result