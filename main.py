#!.venv/bin/python3

import json
import logging
import os.path
from bs4 import BeautifulSoup
import subprocess
import re
import datetime
import sys

logging.basicConfig(level=logging.INFO)

class KBot:
    def __init__(self, id):
        if not os.path.exists('files'):
            os.mkdir('files')
        self.id = id
        self.filename = os.path.join('files', ('result-' + str(self.id)))
        self.old_result_list = []
        self.result_list = []

    def get_items_and_compare_to_current_result(self):
        try:
            with open(self.filename, 'r') as file:
                logging.info(f'Opening file {self.filename}...')
                self.old_result_list = json.load(file)
        except Exception as e:
            print(f'Exception of {e.__class__.__name__}')
            logging.info(f'File {self.filename} not found or empty')
        self.result_list = self._update_result_list(self.id)
        if self.result_list != self.old_result_list:
            logging.info(f'Result differs from old result, writing to {self.filename}')
            self._write_to_file(self.result_list)
            logging.info(f'Differences:')

        else:
            logging.info(f'No difference; not writing to file')


    def _update_result_list(self, id: int):
        """
        :param id:
        :return:
        """

        command = ['curl', f'https://www.kleinanzeigen.de/s-bestandsliste.html?userId={id}']
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            raw_html = result.stdout
            soup = BeautifulSoup(raw_html, 'html.parser')
            url_list = (soup.find_all('a', class_='ellipsis'))
            logging.info(f'Found {len(url_list)} results')
            result_list = []
            for rel_link in url_list:
                url = 'https://www.kleinanzeigen.de' + rel_link.get('href')
                _raw_result = self._get_anzeige(url)
                desc = self._get_description(_raw_result)
                price = self._get_price(_raw_result)

                result_list.append({'url': url, 'desc': desc, 'price': price})
            return result_list

    @staticmethod
    def _get_description(text):
        soup = BeautifulSoup(text, 'html.parser')
        element = soup.find(id='viewad-description-text')
        if element:
            description = element.get_text(separator='\n')
            description = re.sub('\n', '', description).strip()
            return description
        return "No description found"

    @staticmethod
    def _get_price(text):
        soup = BeautifulSoup(text, 'html.parser')
        element = soup.find(class_="aditem-main--middle--price-shipping--price")
        if element:
            price = element.get_text(separator='')
            price = re.sub('\n', '', price).strip()
            return price
        return "No price found"

    @staticmethod
    def _get_anzeige(url):
        command = ['curl', url]
        result = subprocess.run(command, capture_output=True, text=True)
        text = result.stdout.encode('utf-8')
        return text


    def compare_result_lists(self, result_list_old:list, result_list_new:list):
        diffs = {}

        for item1 in result_list_old:
            # Check if the item exists in result_list_new
            matching_item = next((item2 for item2 in result_list_new if item2['url'] == item1['url']), None)

            # If no match is found, add the item from list1 to the differences
            if matching_item is None:
                diffs[item1] = "Not Found"
            else:
                # Compare the 'desc' values
                if item1['desc'] != matching_item['desc']:
                    diffs[item1] = {"Found": item1, "In List2": matching_item}

            # Iterate over each dictionary in result_list_new
        for item2 in result_list_new:
            # Check if the item exists in list1
            matching_item = next((item1 for item1 in result_list_new if item1['url'] == item2['url']), None)

            # If no match is found, add the item from result_list_new to the differences
            if matching_item is None:
                diffs[item2] = "Not Found"

        return diffs


    def _write_to_file(self, object):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename = 'result-' + str(self.id)
        logging.info(f'Writing result to file {filename}.')

        with open('files/' + filename, 'w') as file:
            (json.dump(object, file, ensure_ascii=False))


IDK = 110484591
IDX = 9245418
ID = 19918217

if __name__ == "__main__":
    user_id = int(sys.argv[1])
    KBot(user_id).get_items_and_compare_to_current_result()
