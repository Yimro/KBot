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

    def setUp(self):
        self.mock_url_list = []
        self.mock_item_list = []
        for i in range(3):
            self.mock_url_list.append(f'url{i}')
            self.mock_item_list.append(main.ListItem(self.mock_url_list[i], f'price{i}', f'description{i}'))


    def test_01(self):
        mock_user_stuff = main.UserStuff(123, self.mock_item_list)


        @patch('main.MyBot.create_url_list', return_value=self.mock_url_list) #first patch
        @patch('main.MyBot.create_user_stuff_object', return_value=mock_user_stuff) #second patch
        def d(second_patch, first_patch):

            assert first_patch is main.MyBot.create_url_list
            assert second_patch is main.MyBot.create_user_stuff_object
            #print(main.MyBot.create_url_list())

            bot = main.MyBot(1234)
            print(bot.create_url_list())
            print(bot.create_user_stuff_object())

        d()


    def test_02_items_changed(self):
        mock_url_list = []
        mock_item_list = []
        for i in range(3):
            mock_url_list.append(f'url{i}')
            mock_item_list.append(main.ListItem(mock_url_list[i], f'price{i}', f'description{i}'))
        mock_user_stuff = main.UserStuff(123, mock_item_list)


        mock_item_list_2 = []
        for i in range(3):
            mock_url_list.append(f'url{i}')
            mock_item_list_2.append(main.ListItem(mock_url_list[i], f'price{i}', f'description_changed{i}'))
        mock_user_stuff_2 = main.UserStuff(123, mock_item_list_2)


        @patch('main.MyBot.create_url_list', return_value=mock_url_list)  # first patch
        @patch('main.MyBot.create_user_stuff_object', return_value=mock_user_stuff)  # second patch
        def e(second_patch, first_patch):
            assert first_patch is main.MyBot.create_url_list
            assert second_patch is main.MyBot.create_user_stuff_object

            #self.assertTrue(mock_user_stuff != mock_user_stuff_2)
            print("check 1")
            self.assertTrue(mock_user_stuff != mock_user_stuff_2)

        e()




if __name__ == '__main__':
    unittest.main()
