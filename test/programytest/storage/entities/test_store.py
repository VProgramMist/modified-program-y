import unittest.mock
import os
from programy.storage.entities.store import Store
from programy.storage.utils.processors import TextFile
from programy.storage.utils.processors import CSVFileReader


class MockStore(Store):

    def __init__(self, throw_except=False):
        Store.__init__(self)
        self.throw_except = throw_except
        self.processed = False
        self.committed = False
        self.rolled_back = False

    def process_line(self, name, fields):
        if self.throw_except is True:
            raise Exception("Mock Exception")

        self.processed = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class StoreTests(unittest.TestCase):

    def test_init(self):
        store = Store()
        self.assertIsNotNone(store)

    def test_get_split_char(self):
        store = Store()
        self.assertEquals(",", store.get_split_char())

    def test_split_into_fields(self):
        store = Store()
        self.assertEquals(["FIELD1"], store.split_into_fields("FIELD1"))
        self.assertEquals(["FIELD1", "FIELD2"], store.split_into_fields("FIELD1,FIELD2"))
        self.assertEquals(["FIELD1", "FIELD2", "FIELD3"], store.split_into_fields("FIELD1,FIELD2,FIELD3"))

    def test_process_line(self):
        store = Store()
        self.assertFalse(store.process_line("test", []))

    def test_upload_from_text_no_text_with_commit(self):
        store = MockStore(throw_except=False)
        store.upload_from_text("test", "", commit=True)
        self.assertFalse(store.processed)
        self.assertTrue(store.committed)
        self.assertFalse(store.rolled_back)

    def test_upload_from_text_no_lines_with_commit(self):
        store = MockStore(throw_except=False)
        store.upload_from_text("test", """"
        """, commit=True)
        self.assertTrue(store.processed)
        self.assertTrue(store.committed)
        self.assertFalse(store.rolled_back)

    def test_upload_from_text_empty_lines_with_commit(self):
        store = MockStore(throw_except=False)
        store.upload_from_text("test", """"
        
        
        
        """, commit=True)
        self.assertTrue(store.processed)
        self.assertTrue(store.committed)
        self.assertFalse(store.rolled_back)

    def test_upload_from_text_with_lines_with_commit(self):
        store = MockStore(throw_except=False)
        store.upload_from_text("test", """"
        FIELD1, FIELD2
        FIELD3 FIELD4
        """, commit=True)
        self.assertTrue(store.processed)
        self.assertTrue(store.committed)
        self.assertFalse(store.rolled_back)

    def test_upload_from_text_with_lines_without_commit(self):
        store = MockStore(throw_except=False)
        store.upload_from_text("test", """"
        FIELD1, FIELD2
        FIELD3 FIELD4
        """, commit=False)
        self.assertTrue(store.processed)
        self.assertFalse(store.committed)
        self.assertFalse(store.rolled_back)

    def test_upload_from_text_with_lines_with_commit_exception(self):
        store = MockStore(throw_except=True)
        store.upload_from_text("test", """"
        FIELD1, FIELD2
        FIELD3 FIELD4
        """, commit=True)
        self.assertFalse(store.processed)
        self.assertFalse(store.committed)
        self.assertTrue(store.rolled_back)

    def test_get_file_processor_text(self):
        store = Store()
        self.assertIsInstance(store.get_file_processor(Store.TEXT_FORMAT, os.path.dirname(__file__) + os.sep + "test.txt"), TextFile)

    def test_get_file_processor_csv(self):
        store = Store()
        self.assertIsInstance(store.get_file_processor(Store.CSV_FORMAT, os.path.dirname(__file__) + os.sep + "test.csv"), CSVFileReader)

    def test_get_file_processor_unknown(self):
        store = Store()
        with self.assertRaises(Exception):
            store.get_file_processor("UNKNOWN")

    def test_get_just_filename_from_filepath(self):
        store = Store()
        self.assertEqual("", store.get_just_filename_from_filepath(""))
        self.assertEqual("TEST", store.get_just_filename_from_filepath("test"))
        self.assertEqual("TEST", store.get_just_filename_from_filepath("test.txt"))
        self.assertEqual("TEST", store.get_just_filename_from_filepath(os.path.dirname(__file__) + os.sep + "test.txt"))

    def test_upload_from_file(self):
        store = MockStore(throw_except=False)
        final_count, final_success = store.upload_from_file( os.path.dirname(__file__) + os.sep + "test.txt")
        self.assertEquals(1, final_count)
        self.assertEquals(0, final_success)
        self.assertTrue(store.processed)
        self.assertTrue(store.committed)
        self.assertFalse(store.rolled_back)

    def test_upload_from_file_exception(self):
        store = MockStore(throw_except=True)
        final_count, final_success = store.upload_from_file( os.path.dirname(__file__) + os.sep + "test.txt")
        self.assertEquals(0, final_count)
        self.assertEquals(0, final_success)
        self.assertFalse(store.processed)
        self.assertFalse(store.committed)
        self.assertTrue(store.rolled_back)

    def test_upload_from_directory_with_subdir(self):
        store = Store()
        final_count, final_success = store.upload_from_directory(os.path.dirname(__file__) + os.sep + "testdir", subdir=True)
        self.assertEquals(5, final_count)
        self.assertEquals(0, final_success)

    def test_upload_from_directory_with_subdir_with_ext(self):
        store = Store()
        final_count, final_success = store.upload_from_directory(os.path.dirname(__file__) + os.sep + "testdir", subdir=True, extension=".txt")
        self.assertEquals(3, final_count)
        self.assertEquals(0, final_success)

    def test_upload_from_directory_without_subdir(self):
        store = Store()
        final_count, final_success = store.upload_from_directory(os.path.dirname(__file__) + os.sep + "testdir", subdir=False)
        self.assertEquals(3, final_count)
        self.assertEquals(0, final_success)

    def test_upload_from_directory_without_subdir_with_ext(self):
        store = Store()
        final_count, final_success = store.upload_from_directory(os.path.dirname(__file__) + os.sep + "testdir", subdir=False, extension=".txt")
        self.assertEquals(2, final_count)
        self.assertEquals(0, final_success)

