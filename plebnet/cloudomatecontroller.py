from cloudomate import wallet as wallet_util
from cloudomate.cmdline import providers
from cloudomate.util.config import UserOptions
from cloudomate.vps.rockhoster import RockHoster


def _user_settings():
    settings = UserOptions()
    settings.read_settings()
    return settings


def status(provider):
    settings = _user_settings()
    return provider.get_status(settings)


def options(provider):
    p = providers[provider]
    return p.options()


def get_network_fee():
    return wallet_util.get_network_fee()


if __name__ == '__main__':
    print status(RockHoster())
