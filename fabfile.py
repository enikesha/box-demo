from fab_deploy import *

COMMON_OPTIONS = dict(
    INSTANCE_NAME = 'box-demo',
    LOCAL_CONFIG = 'local_settings.py',
    VCS = 'git',
    SUDO_USER = 'web',
    PIP_REQUIREMENTS_PATH = '.',
    PIP_REQUIREMENTS = 'requirements.txt',
    PIP_REQUIREMENTS_ACTIVE = 'requirements.txt',
    DJANGO_SETTINGS = 'settings',
    DB_USER = 'root',
    DB_PASSWORD = '',
)

@define_host('sites@do0.enikesha.net', COMMON_OPTIONS)
def do0():
    return dict(
        GIT_BRANCH = 'master',
        )
