import requests
from flask.ext.testing import LiveServerTestCase
from fdanalytics.app import app


class FD_AnalyticsLiveServerTestCase(LiveServerTestCase):
    def create_app(self):
        return app

    def _namespace(self):
        return "{}/analytics/api/v1.0".format(self.get_server_url())


class RootTest(FD_AnalyticsLiveServerTestCase):
    def setUp(self):
        self.url = self._namespace()

    def test_get_returns_200(self):
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)
