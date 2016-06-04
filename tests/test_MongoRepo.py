import unittest
from mock import Mock, patch, sentinel
from datetime import timedelta
from tests.ditest import DependencyInjectionTestBase


class MongoRepoTests(DependencyInjectionTestBase):

    def setUp(self):
        super(MongoRepoTests, self).setUp()
        self.pictureCache.getBytes.return_value = None
        self.db = Mock()
        self.db.provenance.find_one.return_value = {}
        self.db.provenance.find.return_value = {}

    def setupRepo(self):
        from niprov.mongo import MongoRepository
        with patch('niprov.mongo.pymongo') as pymongo:
            self.repo = MongoRepository(dependencies=self.dependencies)
        self.repo.db = self.db

    def test_Connection(self):
        from niprov.mongo import MongoRepository
        with patch('niprov.mongo.pymongo') as pymongo:
            repo = MongoRepository(dependencies=self.dependencies)
        pymongo.MongoClient.assert_called_with(self.config.database_url)
        self.assertEqual(pymongo.MongoClient().get_default_database(), repo.db)

    def test_knowsByLocation(self):
        self.setupRepo()
        p = '/p/f1'
        self.db.provenance.find_one.return_value = None
        self.assertFalse(self.repo.knowsByLocation(p))
        self.db.provenance.find_one.assert_called_with({'location':p})
        self.db.provenance.find_one.return_value = 1
        self.assertTrue(self.repo.knowsByLocation(p))

    def test_byLocation_returns_img_from_record_with_path(self):
        self.setupRepo()
        p = '/p/f1'
        out = self.repo.byLocation(p)
        self.db.provenance.find_one.assert_called_with({'location':p})
        self.fileFactory.fromProvenance.assert_called_with(
            self.db.provenance.find_one())
        self.assertEqual(self.fileFactory.fromProvenance(), out)

    def test_getSeries(self):
        self.setupRepo()
        img = Mock()
        out = self.repo.getSeries(img)
        self.db.provenance.find_one.assert_called_with(
            {'seriesuid':img.getSeriesId()})
        self.fileFactory.fromProvenance.assert_called_with(
            self.db.provenance.find_one())
        self.assertEqual(self.fileFactory.fromProvenance(), out)

    def test_knowsSeries_returns_False_if_no_series_id(self):
        self.setupRepo()
        img = Mock()
        img.getSeriesId.return_value = None
        self.assertFalse(self.repo.knowsSeries(img))

    def test_knowsSeries(self):
        self.setupRepo()
        img = Mock()
        self.assertTrue(self.repo.knowsSeries(img))
        self.db.provenance.find_one.return_value = None
        self.assertFalse(self.repo.knowsSeries(img))

    def test_Add(self):
        self.setupRepo()
        img = Mock()
        img.provenance = {'a':1, 'b':2}
        self.repo.add(img)
        self.db.provenance.insert_one.assert_called_with({'a':1, 'b':2})

    def test_update(self):
        self.setupRepo()
        img = Mock()
        img.provenance = {'a':1, 'b':2}
        self.repo.update(img)
        self.db.provenance.update.assert_called_with(
            {'location':img.location.toString()}, {'a':1, 'b':2})

    def test_all(self):
        self.fileFactory.fromProvenance.side_effect = lambda p: 'img_'+p
        self.db.provenance.find.return_value = ['p1', 'p2']
        self.setupRepo()
        out = self.repo.all()
        self.db.provenance.find.assert_called_with()
        self.fileFactory.fromProvenance.assert_any_call('p1')
        self.fileFactory.fromProvenance.assert_any_call('p2')
        self.assertEqual(['img_p1', 'img_p2'], out)

    def test_bySubject(self):
        self.fileFactory.fromProvenance.side_effect = lambda p: 'img_'+p
        self.db.provenance.find.return_value = ['p1', 'p2']
        self.setupRepo()
        s = 'Brambo'
        out = self.repo.bySubject(s)
        self.db.provenance.find.assert_called_with({'subject':s})
        self.fileFactory.fromProvenance.assert_any_call('p1')
        self.fileFactory.fromProvenance.assert_any_call('p2')
        self.assertEqual(['img_p1', 'img_p2'], out)

    def test_byApproval(self):
        self.fileFactory.fromProvenance.side_effect = lambda p: 'img_'+p
        self.db.provenance.find.return_value = ['p1', 'p2']
        self.setupRepo()
        a = 'AOk'
        out = self.repo.byApproval(a)
        self.db.provenance.find.assert_called_with({'approval':a})
        self.fileFactory.fromProvenance.assert_any_call('p1')
        self.fileFactory.fromProvenance.assert_any_call('p2')
        self.assertEqual(['img_p1', 'img_p2'], out)

    def test_updateApproval(self):
        self.setupRepo()
        img = Mock()
        p = '/p/f1'
        newStatus = 'oh-oh'
        self.repo.updateApproval(p, newStatus)
        self.db.provenance.update.assert_called_with(
            {'location':p}, {'$set': {'approval': newStatus}})

    def test_latest(self):
        self.fileFactory.fromProvenance.side_effect = lambda p: 'img_'+p
        self.db.provenance.find.return_value = Mock()
        self.db.provenance.find.return_value.sort.return_value.limit.return_value = ['px','py']
        self.setupRepo()
        out = self.repo.latest()
        self.db.provenance.find.assert_called_with()
        self.db.provenance.find().sort.assert_called_with('added', -1)
        self.db.provenance.find().sort().limit.assert_called_with(20)
        self.fileFactory.fromProvenance.assert_any_call('px')
        self.fileFactory.fromProvenance.assert_any_call('py')
        self.assertEqual(['img_px', 'img_py'], out)

    def test_statistics(self):
        self.db.provenance.aggregate.return_value = [sentinel.stats,]
        self.setupRepo()
        out = self.repo.statistics()
        self.db.provenance.aggregate.assert_called_with(
           [{'$group':
                 {
                   '_id': None,
                   'totalsize': { '$sum': '$size' },
                   'count': { '$sum': 1 }
                 }
            }])
        self.assertEqual(sentinel.stats, out)

    def test_statistics_if_no_records(self):
        self.db.provenance.aggregate.return_value = []
        self.setupRepo()
        out = self.repo.statistics()
        self.assertEqual({'count':0}, out)

    def test_byId(self):
        self.setupRepo()
        ID = 'abc123'
        out = self.repo.byId(ID)
        self.db.provenance.find_one.assert_called_with({'id':ID})
        self.fileFactory.fromProvenance.assert_called_with(
            self.db.provenance.find_one())
        self.assertEqual(self.fileFactory.fromProvenance(), out)

    def test_byLocations(self):
        self.fileFactory.fromProvenance.side_effect = lambda p: 'img_'+p
        self.db.provenance.find.return_value = ['p1', 'p2']
        self.setupRepo()
        out = self.repo.byLocations(['l1','l2'])
        self.db.provenance.find.assert_called_with({'location':{'$in':['l1','l2']}})
        self.fileFactory.fromProvenance.assert_any_call('p1')
        self.fileFactory.fromProvenance.assert_any_call('p2')
        self.assertEqual(['img_p1', 'img_p2'], out)

    def test_byParents(self):
        self.fileFactory.fromProvenance.side_effect = lambda p: 'img_'+p
        self.db.provenance.find.return_value = ['p1', 'p2']
        self.setupRepo()
        out = self.repo.byParents(['x1','x2'])
        self.db.provenance.find.assert_called_with({'parents':{'$in':['x1','x2']}})
        self.fileFactory.fromProvenance.assert_any_call('p1')
        self.fileFactory.fromProvenance.assert_any_call('p2')
        self.assertEqual(['img_p1', 'img_p2'], out)

    def test_Converts_timedelta_to_float_when_serializing(self):
        self.setupRepo()
        img = Mock()
        img.provenance = {'a':1, 'duration':timedelta(seconds=67.89)}
        self.repo.add(img)
        self.db.provenance.insert_one.assert_called_with(
            {'a':1, 'duration':67.89})

    def test_Converts_duration_to_timedelta_when_deserializing(self):
        self.setupRepo()
        self.db.provenance.find_one.return_value = {'a':3, 'duration':89.01}
        out = self.repo.byLocation('/p/f1')
        self.fileFactory.fromProvenance.assert_called_with(
            {'a':3, 'duration':timedelta(seconds=89.01)})

    def test_Obtains_optional_snapshot_data_from_cache_when_serializing(self):
        self.pictureCache.getBytes.return_value = sentinel.snapbytes
        with patch('niprov.mongo.bson') as bson:
            bson.Binary.return_value = sentinel.snapbson
            self.setupRepo()
            img = Mock()
            img.provenance = {'a':1}
            self.repo.add(img)
            self.pictureCache.getBytes.assert_called_with(for_=img)
            bson.Binary.assert_called_with(sentinel.snapbytes)
            self.db.provenance.insert_one.assert_called_with({'a':1, 
                '_snapshot-data':sentinel.snapbson})

    def test_If_no_snapshot_doesnt_add_data_field(self):
        self.pictureCache.getBytes.return_value = None
        with patch('niprov.mongo.bson') as bson:
            self.setupRepo()
            img = Mock()
            img.provenance = {'a':1}
            self.repo.add(img)
            assert not bson.Binary.called
            self.db.provenance.insert_one.assert_called_with({'a':1})

    def test_If_snapshotdata_hands_them_to_pictureCache_on_deserializing(self):
        img = Mock()
        self.fileFactory.fromProvenance.return_value = img
        self.setupRepo()
        self.db.provenance.find_one.return_value = {'a':3}
        out = self.repo.byLocation('/p/f1')
        assert not self.pictureCache.keep.called
        self.db.provenance.find_one.return_value = {'a':3, '_snapshot-data':'y7yUyS'}
        out = self.repo.byLocation('/p/f1')
        self.pictureCache.keep.assert_called_with('y7yUyS', for_=img)

    def test_If_no_record_returned_byLocation_byId_getSeries_raise_alarm(self):
        self.setupRepo()
        self.db.provenance.find_one.return_value = None
        out = self.repo.byLocation('nowhere')
        self.listener.unknownFile.assert_called_with('nowhere')
        out = self.repo.byId('xxxx')
        self.listener.unknownFile.assert_called_with('id: xxxx')
        img = Mock()
        img.getSeriesId.return_value = '123abc'
        out = self.repo.getSeries(img)
        self.listener.unknownFile.assert_called_with('seriesuid: 123abc')

