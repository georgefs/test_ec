import requests
import cPickle
import os
import json

class MockResponse(object):
    def __init__(self, content, status=200):
        self.content = content
        self.status_code = status

class RecordRequests(object):
    def __init__(self, cache_file, read_only=True):
        self.cache_file = cache_file
        self.read_only = read_only
        if os.path.exists(cache_file):
            with open(cache_file) as ifile:
                self._cache = cPickle.load(ifile)
        else:
            self._cache = {}

    def clear(self):
        self._cache = {}

    def cache(self, method, url, **kwargs):
        _key = (method, url, str(kwargs))
        assert not self.read_only or _key in self._cache, _key

        if _key in self._cache:
            return self._cache[_key]

        r = getattr(requests, method)(url, **kwargs)
        self._cache[_key] = r
        return r

    def get(self, url, **kwargs):
        return self.cache("get", url, **kwargs)

    def post(self, url, **kwargs):
        return self.cache("post", url, **kwargs)

    def save(self):
        with open(self.cache_file, 'w') as ofile:
            cPickle.dump(self._cache, ofile)


class TestCase(object):
    def __init__(self, advertiser_id, product_key):
        self.advertiser_id = advertiser_id
        self.product_key = product_key

    @property
    def item(self):
        return cPickle.loads(TestCaseManager.get(self.advertiser_id, self.product_key, 'item'))

    @item.setter
    def item(self, value):
        TestCaseManager.save(self.advertiser_id, self.product_key, 'item', cPickle.dumps(value))

    @property
    def html(self):
        return TestCaseManager.get(self.advertiser_id, self.product_key, 'html')

    @html.setter
    def html(self, value):
        TestCaseManager.save(self.advertiser_id, self.product_key, 'html', value)

    @property
    def cache_path(self):
        return TestCaseManager.path(self.advertiser_id, self.product_key, 'pickle')

    def __str__(self):
        return self.product_key

class TestCaseManager(object):
    FILEPATH = os.path.join(os.path.dirname(__file__), "test_cases")

    @classmethod
    def listall(cls):
        from ec.site import site
        for advertiser_id in site.registed_ec:
            for test in cls.list(advertiser_id):
                yield test

    @classmethod
    def list(cls, advertiser_id):
        if not os.path.exists('%s/%s' % (cls.FILEPATH, advertiser_id)):
            return

        for i in os.listdir("%s/%s" % (cls.FILEPATH, advertiser_id)):
            if not i.endswith('.item'): continue

            product_key = i.replace('.item', '').replace('__', ':')
            yield TestCase(advertiser_id, product_key)

    @classmethod
    def get(cls, advertiser_id, product_key, type):
        return open(cls.path(advertiser_id, product_key, type)).read()

    @classmethod
    def save(cls, advertiser_id, product_key, type, value):
        filename = cls.path(advertiser_id, product_key, type)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as ofile:
            ofile.write(value)

    @classmethod
    def path(cls, advertiser_id, product_key, type):
        return "%s/%s/%s.%s" % (cls.FILEPATH, advertiser_id, product_key.replace(':', "__"), type)
