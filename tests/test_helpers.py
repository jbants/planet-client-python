from planet.api.helpers import downloader
import time

SPEED_UP = 100.
WRITE_DELAY = 3 / SPEED_UP
ACTIVATE_DELAY = .5 / SPEED_UP
DOWNLOAD_DELAY = .5 / SPEED_UP
ASSET_DELAY = .5 / SPEED_UP


class Resp(object):

    def __init__(self, resp):
        self.resp = resp

    def get(self):
        return self.resp


class Body(object):
    def __init__(self, name):
        self.name = name
        self._got_write = False

    def write(self, file, callback):
        callback(start=self)
        callback(total=1024, wrote=1024)
        callback(finish=self)
        self._got_write = True

    def await(self):
        time.sleep(WRITE_DELAY)
        pass

    def cancel(self):
        pass


def asset(name, type, status):
    return {"_name": name, "type": type, 'status': status}


def assets(*assets):
    res = {}
    for a in assets:
        res[a['type']] = a
    res['_pinged'] = 0
    return res


class HelperClient(object):

    def __init__(self):
        self.assets = {}
        self._shutdown = False

    def get_assets(self, item):
        if item['id'] in self.assets:
            a = self.assets[item['id']]
            if a['_pinged'] > 2:
                a['a']['status'] = 'active'
                a['b']['status'] = 'active'
            a['_pinged'] += 1
        else:
            a = assets(asset(item['id'] + '.junk', 'a', 'inactive'),
                       asset(item['id'] + '.crud', 'b', 'inactive'))
            self.assets[item['id']] = a
        time.sleep(ASSET_DELAY)
        return Resp(a)

    def activate(self, asset):
        time.sleep(ACTIVATE_DELAY)
        asset['status'] = 'activating'

    def download(self, asset, writer):
        time.sleep(DOWNLOAD_DELAY)
        b = Body(asset['_name'])
        writer(b)
        return b

    def shutdown(self):
        self._shutdown = True


def items_iter(cnt):
    for i in range(cnt):
        yield {'id': str(i)}


def test_pipeline():
    from planet.api.utils import handle_interrupt
    from planet.api.utils import monitor_stats
    import logging
    import sys
    logging.basicConfig(
        stream=sys.stderr, level=logging.INFO,
        format='%(asctime)s %(message)s', datefmt='%M:%S'
    )
    cl = HelperClient()
    items = items_iter(100)
    asset_types = ['a', 'b']
    dl = downloader(
        cl, asset_types, 'whatever', no_sleep=True,
        astage__size=10, pstage__size=10, dstage__size=2)
    monitor_stats(dl.stats, sys.stdout.write)
    handle_interrupt(dl.shutdown, dl.download, items)
    print dl.stats()


if __name__ == '__main__':
    test_pipeline()
