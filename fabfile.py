from fabric.api import env

from sitesetup.fab.config import init_file
from sitesetup.fab.tasks import *


env.use_ssh_config = True

# Most settings can be configured in fabfile.cfg
init_file('fabfile.cfg')
