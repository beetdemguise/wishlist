# -*- coding: utf-8 -*-
import bs4
import requests


class WishlistBase(object):
    def __init__(self, base_url):
        self.url = base_url

    def request_wishlist_data(self, user):
        if not self.url:
            raise ValueError('No URL provided')

        if not user:
            raise ValueError('No user provided')

        return bs4.BeautifulSoup(
            requests.get(self.url.format(username=user)).content,
            'html.parser')

    def get_wishlist(self, user, url=None):
        raise NotImplementedError()

    def get_item_description(self, item_id):
        raise NotImplementedError()


class WishlistItem(object):
    def __init__(self, item_id, rank, title, price, description):
        self.item_id = item_id
        self.rank = rank
        self.title = title
        self.price = price
        self.description = description


class Steam(WishlistBase):
    def __init__(self,
                 base_url='https://steamcommunity.com/id/{username}/wishlist'):
        super(Steam, self).__init__(base_url)

    def get_wishlist(self, user):
        if not self.url:
            raise ValueError('No URL provided')

        if not user:
            raise ValueError('No user provided')

        soup = self.request_wishlist_data(user)

        items = []
        for row in soup.find_all('div', class_='wishlistRow'):
            game_id = row['id'].replace('game_', '')
            rank = row.find('div',
                            class_='wishlist_rank_ro').get_text().strip()
            title = row.find('h4', class_='ellipsis').get_text().strip()
            price = row.find('div', class_='price').get_text().strip()
            desc = self.get_item_description(game_id)

            items.append(WishlistItem(game_id, rank, title, price, desc))
        return sorted(items, key=lambda obj: obj.rank)

    def get_item_description(self, item_id):
        url = 'https://steamcommunity.com/app/{item_id}'.format(
            item_id=item_id)

        soup = bs4.BeautifulSoup(requests.get(url).content, 'html.parser')

        return soup.find('div', class_='apphub_StoreAppText').get_text()
