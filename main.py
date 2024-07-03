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
    description: str
    price: str

    def find_changes(self, other):
        if not isinstance(other, ListItem):
            return None

        changes = {}
        for attr in ['url', 'title', 'price', 'description']:
            if getattr(self, attr) != getattr(other, attr):
                changes[attr] = (getattr(self, attr), getattr(other, attr))

        return changes if changes else None


@dataclass
class UserStuff:
    """Params: int, list[ListItem]"""
    user_id: int
    stuff_list: list[ListItem]

    def __eq__(self, other):
        if isinstance(other, UserStuff):
            return self.user_id == other.user_id and self.stuff_list == other.stuff_list
        return False

    def find_changes(self, other):
        if not isinstance(other, UserStuff):
            return None

        changes = []
        for item_self, item_other in zip(self.stuff_list, other.stuff_list):
            item_changes = item_self.find_changes(item_other)
            if item_changes:
                changes.append((item_self, item_other, item_changes))

        return changes if changes else None


def save_user_stuff_to_file(user_stuff: UserStuff, file_name: str) -> None:
    with open(file_name, 'wb') as file:
        pickle.dump(user_stuff, file)


def load_user_stuff_from_file(file_name: str):
    try:
        with open(file_name, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None


class MyBot:
    def __init__(self, user_id):
        self.user_id = user_id
        self.urls: list[str] = []
        self.user_stuff_old: UserStuff
        self.user_stuff_new: UserStuff

    def _create_url_list(self):
        urls: list[str] = []
        command = ['curl', f'https://www.kleinanzeigen.de/s-bestandsliste.html?userId={self.user_id}']
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            soup = BeautifulSoup(result.stdout, 'html.parser')

            raw_urls = soup.find_all('a', class_='ellipsis')
            for line in raw_urls:
                item_url = 'https://www.kleinanzeigen.de' + line.get('href')
                urls.append(item_url)
        return urls

    def create_user_stuff_object(self) -> UserStuff:
        stuff = UserStuff(self.user_id, [])
        self.urls = self._create_url_list()
        for ad_url in self.urls:
            ad_page = self._get_ad(ad_url)
            item = ListItem(ad_url, self._get_title(ad_page), self._get_description(ad_page), self._get_price(ad_page))
            stuff.stuff_list.append(item)
        return stuff

    def print_user_stuff_items(self, user_stuff_obj: UserStuff) -> None:
        print(f'User ID: {self.user_id}')
        for item in user_stuff_obj.stuff_list:
            print("---")
            print(item.url, item.title, item.price, item.description[0:20], sep='\n')
            print("---")

    @staticmethod
    def _get_ad(url) -> str:
        command = ['curl', url]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        return "No ad found"

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
        element = soup.find(class_="boxedarticle--price")
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
    user = int(sys.argv[1])
    print("creating bot with user_id:", user)
    bot = MyBot(user) # user_id = 1234,
    print("check if user_stuff_old exists ...")

    bot.user_stuff_old = load_user_stuff_from_file(f'user_stuff_{user}.pkl')
    if bot.user_stuff_old:
        print("User_stuff_old found, now creating user_stuff_new ...")
        bot.user_stuff_new = bot.create_user_stuff_object()
        if bot.user_stuff_old != bot.user_stuff_new:
            print("User stuff has changed, saving new user_stuff object")
            save_user_stuff_to_file(bot.user_stuff_new, f'user_stuff_{user_id}.pkl')
            print(bot.user_stuff_old.find_changes(bot.user_stuff_new))
        else:
            print("Nothing has changed, nothing to do!")
    else:
        print("User_stuff_old not found, creating user_stuff_new ...")
        save_user_stuff_to_file(bot.user_stuff_new, f'user_stuff_{user_id}.pkl')
        bot.print_user_stuff_items(bot.user_stuff_new)