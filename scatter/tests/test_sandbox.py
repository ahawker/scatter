"""
    scatter.tests.test_sandbox
    ~~~~~~~~~~~~~~~~~~~~~~~~~~


"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'

from scatter.app import Scatter
from scatter.tests import ScatterTestCase
from scatter.utils import resolve_type


class TestServiceConfig(ScatterTestCase):
    """

    """

    def test_sandbox(self):
        """

        """
        print 'sandbox, eh'
        from scatter.ext.async import AsyncService
        from scatter.ext.gevent import GeventService

        xxx = GeventService()
        print xxx
        print 'getting result_worker'
        rw= xxx.result_worker
        print 'GOT!!!!!@@!@!@!'
        print rw

        ssss = xxx.task_queue
        print ssss

        print xxx.worker_pool
        print xxx.request_queue
        print xxx.result_queue
        print xxx.request_worker

