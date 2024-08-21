import ipaddress
import os

import pytest
from rest_framework.test import APIClient



MANAGER_IP = os.environ.get('MANAGER_IPS', '123.123.123.123,127.0.0.2').split(',')[0]
print(f"MANAGER_IP: {MANAGER_IP}")
DEFAULT_RAFFLE = {
    "name": "Foobar raffle",
    "total_tickets": 15,
    "prizes": [
        {"name": "invisibility", "amount": 1},
        {"name": "warm hug", "amount": 3},
        {"name": "firm handshake", "amount": 5},
    ]
}


class RaffleClient(APIClient):
    default_format = 'json'


class IncrementingIpFactory:
    def __init__(self):
        self.num = 0x01000000

    def __call__(self):
        self.num += 1
        return ipaddress.IPv4Address._string_from_ip_int(self.num)


make_ip = IncrementingIpFactory()


def unexpected_response_error(resp):
    return f'Unexpected response {resp.status_code} / {resp.content}'


def make_raffle(client, **overrides):
    resp = client.post("/raffles/",
                       data=DEFAULT_RAFFLE | overrides,
                       REMOTE_ADDR=MANAGER_IP)
    if resp.status_code != 201:
        print(f"Response content: {resp.content}")
        raise Exception('Unable to create a raffle')
    return resp.json()


@pytest.fixture
def ip_factory():
    return make_ip()


@pytest.fixture
def client():
    return RaffleClient()


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def get_ticket(client):
    def _inner(raffle_id):
        resp = client.post(f"/raffles/{raffle_id}/participate/",
                           REMOTE_ADDR=make_ip())
        if resp.status_code != 201:
            raise Exception('Unable to get a ticket to the raffle')
        return resp.json()
    return _inner


@pytest.fixture
def raffle(client):
    return make_raffle(client=client)


@pytest.fixture
def raffle_factory(client):
    def _factory(**overrides):
        return make_raffle(client, **overrides)
    return _factory


@pytest.fixture
def default_raffle():
    return DEFAULT_RAFFLE


@pytest.fixture
def manager_ip():
    return MANAGER_IP

DISABLE_TEST_CACHING = True

@pytest.fixture(autouse=True)
def disable_test_caching(settings):
    settings.DISABLE_TEST_CACHING = True