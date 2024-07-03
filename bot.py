#!.venv/bin/python3
import copy
import datetime
import os

from bs4 import BeautifulSoup
import subprocess
import re
import sys
import pickle
import pprint
import send_email as send_email

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


def print_changes_with_color(changes):
    for old_item, new_item, attrs_changes in changes:
        if old_item.url != new_item.url:
            print(f"Changes for item from {old_item.url} to {new_item.url}:")
        else:
            print(f"Changes for item {old_item.url}:")
        for attr, value in attrs_changes.items():
            print(f"\t{attr}: \033[91m{value[0]}\033[0m -> \033[92m{value[1]}\033[0m")


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


def check_for_changes():
    # user id entered
    user = int(sys.argv[1])
    filename = f'user_stuff_{user}.pkl'

    # try to load old user stuff from file if exists
    saved_user_stuff = load_user_stuff_from_file(filename)
    if saved_user_stuff:
        time_modified = os.path.getmtime(filename)
        print(f'Saved user stuff found. Last modified at: {datetime.datetime.fromtimestamp(time_modified)}')
        print(f'User id: {saved_user_stuff.user_id}; Number of Items: {len(saved_user_stuff.stuff_list)}')
        print(f'Creating new user stuff object for user {user}...')
        new_user_stuff = MyBot(user).create_user_stuff_object()

        ### for testing purposes, create a new user_stuff object ###
        # new_user_stuff = copy.deepcopy(user_stuff)
        # for testing purposes, change new user_stuff object
        #new_user_stuff.stuff_list[0].title = new_user_stuff.stuff_list[0].title + 'x'
        #new_user_stuff.stuff_list[1].price = new_user_stuff.stuff_list[1].price + 'x'
        #############################################################

        if saved_user_stuff != new_user_stuff:
            print(f"User stuff for {user} has changed, saving new user_stuff object.")
            save_user_stuff_to_file(new_user_stuff, filename)
            print_changes_with_color(saved_user_stuff.find_changes(new_user_stuff))
            send_email()

        else:
            print("Nothing has changed, nothing to do!")

    else:
        print(f"No saved user stuff found, creating new user_stuff object for {user}")
        user_stuff = MyBot(user).create_user_stuff_object()
        filename = f'user_stuff_{user}.pkl'
        save_user_stuff_to_file(user_stuff, filename)
        print(f"User stuff saved to file {filename}")


def local_changes():
    if len(sys.argv) < 2:
        print("Usage: bot.py <user_id>")
        sys.exit(1)

    # user id entered
    user = int(sys.argv[1])
    # create bot object
    bot = MyBot(user)
    # load user stuff from file if exists
    user_stuff = load_user_stuff_from_file(f'user_stuff_{user}.pkl')
    print(type(user_stuff))
    print(f'user_stuff: user {user}; length: {len(user_stuff.stuff_list)}')
    print(f'user_stuff: title of item 0: {user_stuff.stuff_list[0].title}')


    user_stuff2 = copy.deepcopy(user_stuff)
    print(f'user_stuff2: user {user}; length: {len(user_stuff2.stuff_list)}')
    print(f'user_stuff2: title of item 0: {user_stuff2.stuff_list[0].title}')

    print('user_stuff2: changing title of item 0')
    user_stuff2.stuff_list[0].title = 'New Title'

    print(f'user_stuff2: Title of item 0: {user_stuff2.stuff_list[0].title}')

    print(user_stuff == user_stuff2)
    pprint.pprint(user_stuff.find_changes(user_stuff2))
    print_changes_with_color(user_stuff.find_changes(user_stuff2))

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: bot.py <user_id>")
        sys.exit(1)

    check_for_changes()