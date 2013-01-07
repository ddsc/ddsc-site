from persistent.mapping import PersistentMapping
from persistent import Persistent


class WMSSource(Persistent):
    wms_url = None
    name = None

    def __init__(self, wms_url=None):
        self.wms_url = wms_url


class DDSCSite(PersistentMapping):
    __parent__ = __name__ = None

    def __init__(self):
        self.wms_sources = PersistentMapping()


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = DDSCSite()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
