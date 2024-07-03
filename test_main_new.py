import logging
import unittest

import pytest

import bot as main
from unittest.mock import patch, MagicMock
import copy

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.DEBUG)

global mock_url_list, mock_item_list, mock_user_stuff_old, mock_user_stuff_new

def setUpModule():
    """Called once before module"""
    print("setUpModule: creating mock objects")
    global mock_url_list, mock_item_list, mock_user_stuff_old, mock_user_stuff_new
    mock_url_list = [f'url{i}' for i in range(3)]
    mock_item_list = [main.ListItem(mock_url_list[i], f'title{i}', f'description{i}', f'price{i}') for i in range(3)]
    mock_user_stuff_old = main.UserStuff(123, mock_item_list)
    mock_user_stuff_new = copy.deepcopy(mock_user_stuff_old)
    mock_user_stuff_new.stuff_list[0].description = 'description_changed0'


def tearDownModule():
    """Called once after module"""
    print("doing tearDownModule...")


def test_case_01():
    assert 'python'.upper() == 'PYTHON'


class TKBot(unittest.TestCase):

    @patch('main.MyBot._create_url_list')
    @patch('main.MyBot._get_ad')
    @patch('main.MyBot._get_title')
    @patch('main.MyBot._get_description')
    @patch('main.MyBot._get_price')
    @patch('main.load_user_stuff_from_file')
    def test_create_user_stuff_object(self, mock_load_user_stuff, mock_get_price, mock_get_description, mock_get_title,
                                      mock_get_ad, mock_create_url_list):
        # Mock the methods
        mock_create_url_list.return_value = ['url0', 'url1', 'url2']
        mock_get_ad.return_value = 'ad_page'
        mock_get_title.return_value = 'title'
        mock_get_description.return_value = 'description'
        mock_get_price.return_value = 'price'
        mock_load_user_stuff.return_value = None

        # Create a MyBot object
        bot = main.MyBot(123)

        # Call create_user_stuff_object method
        user_stuff = bot.create_user_stuff_object()
        print(f'bot.urls: {bot.urls}')

        # Assert that the UserStuff object has the expected attributes
        self.assertEqual(user_stuff.user_id, 123)
        self.assertEqual(len(user_stuff.stuff_list), 3)
        for item in user_stuff.stuff_list:
            # self.assertEqual(item.url, 'url0')
            self.assertEqual(item.title, 'title')
            self.assertEqual(item.description, 'description')
            self.assertEqual(item.price, 'price')

    @patch('subprocess.run')
    def test_get_ad(self, mock_run):
        # Mock the subprocess.run method
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'ad_page'
        mock_run.return_value = mock_result

        # Create a MyBot object
        bot = main.MyBot(123)

        # Call the _get_ad method

        result = main.MyBot._get_ad('url')
        self.assertEqual(result, 'ad_page')


    @patch('main.BeautifulSoup')
    def test_get_description(self, mock_soup):
        mock_soup.return_value.find.return_value = None

        bot = main.MyBot(123)

        result = bot._get_description('text')
        self.assertEqual(result, 'No description found')

    @patch('main.BeautifulSoup')
    def test_get_price(self, mock_soup):

        mock_soup.return_value.find.return_value = None

        result = main.MyBot._get_price('text')
        self.assertEqual(result, 'No price found')

    @patch('main.BeautifulSoup')
    def test_get_price_2(self, mock_soup):

        mock_element = MagicMock()
        mock_element.get_text.return_value = '200'

        mock_soup.return_value.find.return_value = mock_element

        price = main.MyBot._get_price('dummy text')

        self.assertEqual(price, "200")


    def test_find_changes(self):
        # Create two UserStuff objects with the same stuff_list
        user_stuff1 = mock_user_stuff_old
        user_stuff2 = mock_user_stuff_new

        # Call find_changes method
        changes = user_stuff1.find_changes(user_stuff2)

        # Assert that the changes are as expected
        expected_changes = [
            (mock_item_list[0], user_stuff2.stuff_list[0], {'description': ('description0', 'description_changed0')})]
        self.assertEqual(changes, expected_changes)


if __name__ == '__main__':
    unittest.main()