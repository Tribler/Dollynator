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
    return list(provider.start())


if __name__ == '__main__':
    print status(RockHoster())
