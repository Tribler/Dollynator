from cloudomate.util.config import UserOptions
from cloudomate.vps.rockhoster import RockHoster
from cloudomate.wallet import Wallet


def _user_settings():
    settings = UserOptions()
    settings.read_settings()
    return settings


def status(provider):
    settings = _user_settings()
    return provider.get_status(settings)


def options(provider):
    return list(provider.start())


def purchase(provider, vps_option, wallet):
    settings = _user_settings()
    return provider.purchase(settings, vps_option, wallet)


if __name__ == '__main__':
    print purchase(RockHoster(), options(RockHoster())[0], Wallet())
