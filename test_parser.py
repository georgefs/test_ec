import unittest
import json
from mock import *
import os
import cStringIO
from schema import *
import codecs
import logging
import re
from util import *

class MockRequests(RecordRequests):
    def __init__(self, test):
        super(MockRequests, self).__init__(test.cache_path, read_only=True)

    def cache(self, method, url, **kwargs):
        if 'cache_image' in url:
            return MockResponse(url)

        return super(MockRequests, self).cache(method, url, **kwargs)


class TestEC(unittest.TestCase):
    def setUp(self):
        pass

    def test_items(self):
        from ec.site import site
        from collections import defaultdict
        results = defaultdict(list)
        for test in TestCaseManager.listall():
            try:
                # load test case
                cache_item = test.item
            except:
                logging.error("test case error %s", test)
                continue

            assert 'advertiser_id' in cache_item and 'link' in cache_item
            advertiser_id = cache_item["advertiser_id"]
            url = cache_item["link"]

            try:
                ec = site.registed_ec[advertiser_id]
                assert ec and ec == site.get_ec(url=url) == site.get_ec(commerce_id=advertiser_id)
                product_key = ec.get_key(url)
                ec._http = MockRequests(test)
                ec_item = ec.get_item(url)

                assert ec_item == cache_item
                logging.info("test %s passed!", test)
                results[advertiser_id].append(True)
            except KeyboardInterrupt:
                raise
            except:
                logging.exception("test %s failed!", test)
                results[advertiser_id].append(False)

        for advertiser_id in site.registed_ec:
            test_results = results[advertiser_id]
            success_tests = [k for k in test_results if k]
            fail_tests = [k for k in test_results if not k]

            if len(test_results) < 10:
                logging.warning("parser %s: doens't have enough test case %s", advertiser_id, len(test_results))

            if success_tests == test_results:
                logging.info("parser %s: pass all test %s", advertiser_id, len(test_results))
            else:
                logging.error("parser %s: fail %s/%s tests", advertiser_id, len(fail_tests), len(test_results))

        self.assertTrue(all(all(results[advertiser_id]) for advertiser_id in results))

    def tearDown(self):
        pass
        # self.patcher.stop()
