import os
import unittest
from unittest.mock import patch

from utils import JSONFile

from digest import NewsDigest

MOCK_DIGEST_PATH = os.path.join("tests", "test_data", "digest.json")


class TestCase(unittest.TestCase):
    @staticmethod
    def __mocked_get_digest_article_list__(_, __, ___, ____):
        return JSONFile(MOCK_DIGEST_PATH).read()

    def test_method(self):
        with patch.object(
            NewsDigest,
            "__get_digest_article_list__",
            self.__mocked_get_digest_article_list__,
        ):
            NewsDigest().build()
