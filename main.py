#!.venv/bin/python3


from bs4 import BeautifulSoup
import subprocess
import re
import sys
import pickle

from dataclasses import dataclass


@dataclass
class ListItem:
    """Params: url: str, price: str, description: str"""
    url: str
    title: str
    price: str
    description: str


@dataclass
class UserStuff:
    """Params: int, list[ListItem]"""
    user_id: int
    stuff_list: list[ListItem]

    def __eq__(self, other):
        if isinstance(other, UserStuff):
            return self.user_id == other.user_id and self.stuff_list == other.stuff_list
        return False


def save_user_stuff(user_stuff: UserStuff, file_name: str) -> None:
    with open(file_name, 'wb') as file:
        pickle.dump(user_stuff, file)


def load_user_stuff(file_name: str) -> UserStuff:
    with open(file_name, 'rb') as file:
        return pickle.load(file)


def _get_ad(url) -> str:
    command = ['curl', url]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout


class MyBot:
    def __init__(self, user_id):
        self.user_id = user_id
        self.urls: list[str] = []
        self.user_stuff: UserStuff

    def create_url_list(self):
        urls = []
        command = ['curl', f'https://www.kleinanzeigen.de/s-bestandsliste.html?userId={self.user_id}']
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            soup = BeautifulSoup(result.stdout, 'html.parser')

            raw_urls = soup.find_all('a', class_='ellipsis')
            for line in raw_urls:
                item_url = 'https://www.kleinanzeigen.de' + line.get('href')
                urls.append(item_url)

        self.urls = urls
        return urls

    def create_user_stuff_object(self) -> UserStuff:
        stuff = UserStuff(self.user_id, [])
        for ad_url in self.urls:
            ad_page = _get_ad(ad_url)
            item = ListItem(ad_url, self._get_title(ad_page), self._get_description(ad_page), self._get_price(ad_page))
            stuff.stuff_list.append(item)
        return stuff

    def print_urls(self) -> None:
        for u in self.urls:
            print(u)

    def print_user_stuff_items(self) -> None:
        print(f'User ID: {self.user_id}')
        for item in self.user_stuff.stuff_list:
            print("---")
            print(item.url, item.title, item.price, item.description[0:20], sep='\n')
            print("---")

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
    def _get_title(text):
        soup = BeautifulSoup(text, 'html.parser')
        element = soup.find(class_="boxedarticle--title")
        if element:
            price = element.get_text(separator='')
            price = re.sub('\n', '', price).strip()
            return price
        return "No title found"

if __name__ == "__main__":
    user_id = int(sys.argv[1])
    bot = MyBot(user_id)
    print(f'printing urls for user {user_id}:')
    print(bot.create_url_list())
    bot.user_stuff = bot.create_user_stuff_object()
    print(f"printing user_stuff_items for user {user_id}:")
    bot.print_user_stuff_items()
