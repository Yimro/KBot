import unittest
import main
from unittest.mock import MagicMock
from unittest.mock import patch


def setUpModule():
    """Called once before module"""
    print("doing setUpModule...")

def tearDownModule():
    """Called once after module"""
    print("doing tearDownModule...")



class Test01(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """called once befor any test"""
        print("doing setUpClass ...")



    @classmethod
    def tearDownClass(cls):
        """called once after all tests, if setUpClass == succesful"""
        print("doing tearDownClass ...")



    def test_01(self):
        mock_url_list = []
        mock_item_list = []
        for i in range(3):
            mock_url_list.append(f'url{i}')
            mock_item_list.append(main.ListItem(mock_url_list[i], f'price{i}', f'description{i}'))
        mock_user_stuff = main.UserStuff(123, mock_item_list)

        @patch('main.MyBot.create_url_list', return_value=mock_url_list)
        @patch('main.MyBot.create_user_stuff', return_value=mock_user_stuff)
        def d(m, n):

            #assert n is main.MyBot.create_url_list
            #assert m is main.MyBot.create_user_stuff
            #print(main.MyBot.create_url_list())

            bot = main.MyBot(1234)
            print(bot.create_url_list())
            print(bot.create_user_stuff())

        d()


    def test_02(self):
        pass


if __name__ == '__main__':
    unittest.main()
