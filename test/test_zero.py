"""Tests for the 'zero' plugin"""

from _common import unittest
from helper import TestHelper

from beets.library import Item
from beets import config
from beetsplug.zero import ZeroPlugin
from beets.mediafile import MediaFile


class ZeroPluginTest(unittest.TestCase, TestHelper):
    def setUp(self):
        self.setup_beets()

    def tearDown(self):
        self.teardown_beets()
        self.unload_plugins()

    def test_no_patterns(self):
        tags = {
            'comments': 'test comment',
            'day': 13,
            'month': 3,
            'year': 2012,
        }
        z = ZeroPlugin()
        z.debug = False
        z.fields = ['comments', 'month', 'day']
        z.patterns = {'comments': ['.'],
                      'month': ['.'],
                      'day': ['.']}
        z.write_event(None, None, tags)
        self.assertEqual(tags['comments'], None)
        self.assertEqual(tags['day'], None)
        self.assertEqual(tags['month'], None)
        self.assertEqual(tags['year'], 2012)

    def test_patterns(self):
        z = ZeroPlugin()
        z.debug = False
        z.fields = ['comments', 'year']
        z.patterns = {'comments': 'eac lame'.split(),
                      'year': '2098 2099'.split()}

        tags = {
            'comments': 'from lame collection, ripped by eac',
            'year': 2012,
        }
        z.write_event(None, None, tags)
        self.assertEqual(tags['comments'], None)
        self.assertEqual(tags['year'], 2012)

    def test_delete_replaygain_tag(self):
        path = self.create_mediafile_fixture()
        item = Item.from_path(path)
        item.rg_track_peak = 0.0
        item.write()

        mediafile = MediaFile(item.path)
        self.assertIsNotNone(mediafile.rg_track_peak)
        self.assertIsNotNone(mediafile.rg_track_gain)

        config['zero'] = {
            'fields': ['rg_track_peak', 'rg_track_gain'],
        }
        self.load_plugins('zero')

        item.write()
        mediafile = MediaFile(item.path)
        self.assertIsNone(mediafile.rg_track_peak)
        self.assertIsNone(mediafile.rg_track_gain)

    def test_do_not_change_database(self):
        item = self.add_item_fixture(year=2000)
        mediafile = MediaFile(item.path)

        config['zero'] = {'fields': ['year']}
        self.load_plugins('zero')

        item.write()
        self.assertEqual(item['year'], 2000)
        self.assertIsNone(mediafile.year)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
