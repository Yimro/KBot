import logging
import unittest

import pytest

import bot as bot
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
    mock_item_list = [bot.ListItem(mock_url_list[i], f'title{i}', f'description{i}', f'price{i}') for i in range(3)]
    mock_user_stuff_old = bot.UserStuff(123, mock_item_list)
    mock_user_stuff_new = copy.deepcopy(mock_user_stuff_old)
    mock_user_stuff_new.stuff_list[0].description = 'description_changed0'


def tearDownModule():
    """Called once after module"""
    print("doing tearDownModule...")


def readHtmlFile(file_name):
    with open(file_name, 'r') as file:
        return file.read()

class TestKBotUsingHtmlFiles(unittest.TestCase):
    @patch('bot.MyBot._get_ad')
    def test_get_ad_using_html_file(self, mock_get_ad):
        # Read HTML content from file
        ad_page = readHtmlFile('test_html_files/ad_page.html')
        mock_get_ad.return_value = ad_page
        result = bot.MyBot._get_ad('url')
        self.assertEqual(result, ad_page)


class TestKBot(unittest.TestCase):

    @patch('bot.MyBot._create_url_list')
    @patch('bot.MyBot._get_ad')
    @patch('bot.MyBot._get_title')
    @patch('bot.MyBot._get_description')
    @patch('bot.MyBot._get_price')
    @patch('bot.load_user_stuff_from_file')
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
        botti = bot.MyBot(123)

        # Call create_user_stuff_object method
        user_stuff = botti.create_user_stuff_object()
        print(f'botti.urls: {botti.urls}')

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

        # Call the _get_ad method
        result = bot.MyBot._get_ad('url')
        self.assertEqual(result, 'ad_page')


    @patch('bot.BeautifulSoup')
    def test_get_description(self, mock_soup):
        mock_soup.return_value.find.return_value = None
        result = bot.MyBot(123)._get_description('text')
        self.assertEqual(result, 'No description found')

    @patch('bot.BeautifulSoup')
    def test_get_price_no_price_found(self, mock_soup):
        mock_soup.return_value.find.return_value = None
        result = bot.MyBot._get_price('text')
        self.assertEqual(result, 'No price found')

    @patch('bot.BeautifulSoup')
    def test_get_price_price_found(self, mock_soup):
        mock_element = MagicMock()
        mock_element.get_text.return_value = '200'
        mock_soup.return_value.find.return_value = mock_element
        price = bot.MyBot._get_price('dummy text')
        self.assertEqual(price, "200")

    def test_user_stuff_find_changes(self):
        # Create two UserStuff objects with the same stuff_list
        user_stuff1 = mock_user_stuff_old
        user_stuff2 = mock_user_stuff_new

        # Call find_changes method
        changes = user_stuff1.find_changes(user_stuff2)
        print(f'changes: {changes}')

        # Assert that the changes are as expected
        expected_changes = [
            (user_stuff2.stuff_list[0].url, {'description': ('description0', 'description_changed0')})]
        self.assertEqual(changes, expected_changes)

    #@pytest.mark.skip(reason="")
    @patch('bot.MyBot.create_user_stuff_object')
    @patch('bot.load_user_stuff_from_file')
    @patch('sys.argv', ['bot.py', '123'])
    def test_check_for_changes_with_mock_user_objects(self, mock_load_user_stuff, mock_create_user_stuff_object):
        # given
        # 2 different mock_user_stuff_objects:
        mock_load_user_stuff.return_value = mock_user_stuff_old
        mock_create_user_stuff_object.return_value = mock_user_stuff_new
        bot.os.path.getmtime = MagicMock()

        # when
        # main loop runs
        bot.check_for_changes()

        # then
        mock_create_user_stuff_object.assert_called_once()
        mock_load_user_stuff.assert_called_once()


if __name__ == '__main__':
    unittest.main()