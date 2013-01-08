import logging

from persistent.mapping import PersistentMapping
from persistent import Persistent
from repoze.folder import Folder

logger = logging.getLogger(__name__)


class WMSSource(Persistent):

    def __init__(self, wms_url=None, name=None):
        self.wms_url = wms_url
        self.name = name


class DDSCSite(Folder):
    __parent__ = __name__ = None
    name = 'DDSC site'


class WMSSourcesFolder(Folder):
    pass


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = DDSCSite()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
        logger.info("Started new ZODB root object.")
    root = zodb_root['app_root']
    # Basic setup that's needed.  TODO: find someplace else for this.
    if not 'wms_sources' in root:
        root['wms_sources'] = WMSSourcesFolder()
        logger.info("Added WMS sources folder to root.")
    return root
