from cloudomate.util.config import UserOptions
from cloudomate.vps.rockhoster import RockHoster
from cloudomate import wallet as wallet_util
from cloudomate.cmdline import providers

def _user_settings():
    settings = UserOptions()
    settings.read_settings()
    return settings


def status(provider):
    settings = _user_settings()
    return provider.get_status(settings)

def options(provider):
    providers[provider]
    for i, item, estimated_price, price_string in providers.get_configurations():
        yield i, item, estimated_price

def get_network_fee():
    return wallet_util.get_network_fee()


if __name__ == '__main__':
    print status(RockHoster())
