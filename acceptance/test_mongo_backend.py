import unittest
from pymongo import MongoClient

URL = 'mongodb://niprov-admin:{0}@ds041571.mongolab.com:41571/niprov'
PASSWORD = 'uU0mpDXtQXeL6wku'


class MongoTests(unittest.TestCase):

    def setUp(self):
        from niprov import Context
        self.provenance = Context()
        self.fullURL = URL.format(PASSWORD)
        self.provenance.config.database_type = 'MongoDB'
        self.provenance.config.database_url = self.fullURL

    def tearDown(self):
        client = MongoClient(self.fullURL)
        client.get_default_database().provenance.drop()

    def test_Something(self):
        self.provenance.discover('testdata')
        img = self.provenance.report(forFile='testdata/eeg/stub.cnt')
        self.assertEqual(img.provenance['subject'], 'Jane Doe')



