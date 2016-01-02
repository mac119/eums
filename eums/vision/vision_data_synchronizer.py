from abc import ABCMeta, abstractmethod

import requests
from celery.utils.log import get_task_logger

from eums import settings
from eums.vision.vision_data_converter import convert_vision_value

logger = get_task_logger(__name__)


class VisionException(Exception):
    def __init__(self, message=''):
        super(VisionException, self).__init__(message)


class VisionDataSynchronizer:
    __metaclass__ = ABCMeta
    NO_DATA_MESSAGE = u'No Data Available'

    def __init__(self, url):
        if not url:
            raise VisionException(message='Url is required')

        self.url = url
        logger.info("Vision sync url:%s" % self.url)

    @abstractmethod
    def _save_records(self, records):
        pass

    def _load_records(self):
        response = requests.get(self.url, headers={'Content-Type': 'application/json'},
                                auth=(settings.VISION_USER, settings.VISION_PASSWORD),
                                verify=False)

        if response.status_code != 200:
            raise VisionException(message=('Load data failed! Http code:%s' % response.status_code))

        return self._get_json(response.json())

    def sync(self):
        try:
            original_records = self._load_records()
            converted_records = self._convert_records(original_records)
            self._save_records(converted_records)
        except Exception, e:
            raise VisionException(message=e.message)

    @staticmethod
    def _get_json(self, data):
        return []

    @staticmethod
    def _convert_records(records):
        def _convert_record(record):
            return {key: convert_vision_value(key, value) for key, value in record.iteritems()}
        return map(_convert_record, records)
