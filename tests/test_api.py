# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from pytest import raises
from mock import create_autospec, MagicMock, patch, sentinel
import pytest
parametrize = pytest.mark.parametrize

from wishlist.api import WishlistBase, Steam


@pytest.fixture()
def base():
    return WishlistBase(MagicMock())


@pytest.fixture()
def steam():
    return Steam()


@pytest.fixture()
def soup():
    return create_autospec(BeautifulSoup, spec_set=True)


@pytest.yield_fixture()
def bs4():
    with patch('wishlist.api.bs4') as bs_patch:
        yield bs_patch


@pytest.yield_fixture()
def requests():
    with patch('wishlist.api.requests.get') as req_patch:
        yield req_patch


class TestWishlistBase(object):
    def test_not_implemented_errors(self, base):
        with raises(NotImplementedError):
            base.get_wishlist(sentinel.user)
            base.get_item_description(sentinel.user)

    def test_request_wishlist_data_no_url(self, base):
        base.url = None
        with raises(ValueError):
            base.request_wishlist_data(sentinel.user)

    def test_request_wishlist_data_no_user(self, base):
        with raises(ValueError):
            base.request_wishlist_data(None)

    def test_request_wishlist_data(self, base, requests, bs4):
        soup = bs4.BeautifulSoup
        requests.return_value = MagicMock(content=sentinel.content)

        base.request_wishlist_data(sentinel.user)

        base.url.format.assert_called_once_with(username=sentinel.user)
        requests.assert_called_once_with(
            base.url.format(username=sentinel.user))
        soup.assert_called_once_with(sentinel.content, 'html.parser')


class TestSteam(object):
    def test_get_wishlist_no_user(self, steam):
        with raises(ValueError):
            steam.get_wishlist('')

    def test_get_wishlist_no_url(self, steam):
        steam.url = ''
        with raises(ValueError):
            steam.get_wishlist('beetdemguise')

    def test_get_wishlist(self, steam, soup):
        num = 3
        soup.find_all.return_value = num * [soup()]
        steam.request_wishlist_data = MagicMock(return_value=soup)
        steam.get_item_description = MagicMock(return_value=sentinel.desc)

        data = steam.get_wishlist(sentinel.user)

        steam.request_wishlist_data.assert_called_once_with(sentinel.user)
        assert steam.get_item_description.call_count == num
        assert len(data) == num
        assert all(item.item_id and item.rank and item.title and item.price and
                   item.description == sentinel.desc for item in data)

    def test_get_item_description(self, steam, requests, bs4):
        soup = bs4.BeautifulSoup
        requests.return_value = MagicMock(content=sentinel.content)

        steam.get_item_description(sentinel.item_id)

        requests.assert_called_once_with(
            'https://steamcommunity.com/app/{}'.format(sentinel.item_id))
        soup.assert_called_once_with(sentinel.content, 'html.parser')
        soup().find.assert_called_once_with('div',
                                            class_='apphub_StoreAppText')
        soup().find().get_text.assert_called_once()
