import json
import os
import sys
import logging
import re
import cStringIO
from util import *
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "../../ec")))
from ec.site import site

class MockRequests(RecordRequests):
    def __init__(self, test):
        super(MockRequests, self).__init__(test.cache_path, read_only=False)

    def cache(self, method, url, **kwargs):
        if 'cache_image' in url:
            return MockResponse(url)

        return super(MockRequests, self).cache(method, url, **kwargs)


def status():
    for ec in site.registed_ec.values():
        print ec.commerce_id, ec.commerce_name, len(list(TestCaseManager.list(ec.commerce_id)))


def collect_all():
    import csv
    with open('collect_status.csv', 'w') as ofile:
        writer = csv.DictWriter(ofile, ['id', 'name', 'test', 'success', 'failed', 'skip'])
        for ec_id, ec in site.registed_ec.items():
            results = collect(ec_id)
            results['id'] = ec_id
            results['name'] = ec.commerce_name
            writer.writerow(results)

def collect(advertiser_id, test_url=None):
    from collections import Counter
    ec = site.get_ec(commerce_id = advertiser_id)
    c = Counter()

    for url in ec.test_case(test_url):
        product_key = ec.get_key(url)

        try:
            add_test_case(url, advertiser_id)
            c['success'] += 1
        except NotImplementedError:
            logging.warning("parser not support %s %s", product_key, url)
            c['skip'] += 1
            continue
        except KeyboardInterrupt:
            raise
        except:
            logging.exception("parser failed %s %s", product_key, url)
            c['failed'] += 1
            continue
        finally:
            c['test'] += 1

    print 'collect %s cases, skip %s, success %s, fail %s '%(c['test'], c['skip'], c['success'], c['failed'])
    return c

def add_test_case(url, advertiser_id=None):
    print 'collect', url

    ec = site.get_ec(url=url, commerce_id=advertiser_id)
    product_key = ec.get_key(url)

    test = TestCase(advertiser_id, product_key)

    requests = MockRequests(test)
    requests.clear()

    ec._http = requests

    content = requests.get(url).content
    test.html = content
    test.item = ec.get_item(url)

    requests.save()

if __name__ == "__main__":
    import clime; clime.start(debug=True)
