"""
    scatter.tests.test_service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~


"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'


from scatter.tests import ServiceTestCase
from scatter.utils import resolve_type


class TestServiceConfig(ServiceTestCase):
    """

    """

    def test_config_attribute_access(self):
        """
        """
        for key in self.service.default_config:
            attr = getattr(self.service, key.lower(), None)
            conf = self.service.config.get(key.upper())
            self.assert_equal(attr, conf)

    def test_config_mode(self):
        """
        """
        self.assert_equal(self.service.test, True)

    def test_config_collection(self):
        self.assert_is_not_none(self.service.config)
        self.assert_is_not_empty(self.service.config)


class TestServiceAttributes(ServiceTestCase):
    """

    """

    def test_id(self):
        self.assert_is_not_none(self.service.id)
        self.assert_is_instance(self.service.id, basestring)

    def test_name(self):
        self.assert_equal(self.service_class.__name__, self.service.name)

    def test_type(self):
        self.assert_equal(self.service_class.__name__, self.service.type)

    def test_fully_qualified_type(self):
        self.assert_equal(resolve_type(self.service), self.service.fully_qualified_type)

    def test_attribute_collection(self):
        self.assert_is_not_none(self.service.attributes)

    def test_initialize(self):
        pass

        # with tests.ScatterLogCapture(self.service) as out:
        #     msg = 'Hello World!'
        #     self.service.log.info(msg)
        #     out.assert_info(msg)




