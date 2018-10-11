from __future__ import absolute_import

import sys
import logging
import tensorflow as tf
import time
import threading

from deeppress import api
from deeppress.job import TrainingJob
from deeppress.job import ClassificationJob


tf.logging.set_verbosity(tf.logging.INFO)
_LOGGER = logging.getLogger('deeppress.trainer')


class TrainingApp(object):

    def __init__(self):
        self.current_job = None

    def start(self, join=False):
        _LOGGER.debug("Getting models")
        page = 1
        while True:
            try:
                self.current_job = None
                res = api.get_jobs(page=page, per_page=50)
                if isinstance(res, dict) and 'data' in res.keys():
                    data = res['data']
                    total = res['total']
                    page += 1
                    if len(data) == 0:
                        # No Jobs, Sleep
                        return False

                    for record in data:
                        self.current_job = None
                        if record['done']:
                            _LOGGER.debug("Job already done")
                            continue
                        if record['state'] == 'paused':
                            _LOGGER.debug("Job is paused")
                            continue

                        if record['model_type'] == 'detector':
                            self.current_job = TrainingJob(record)
                            self.current_job.start()
                            if join:
                                self.current_job.join()
                            return True
                        elif record['model_type'] == 'classifier':
                            self.cuurent_job = ClassificationJob(record)
                            self.current_job.start()
                            if join:
                                self.current_job.join
                            return True
                        else:
                            _LOGGER.error('Training for model type %s not implemented' % record['model_type'])
                        # page = 1
                        # break
                else:
                    break
            except Exception as e:
                _LOGGER.error(e)
        return False

    def stop(self):
        if self.current_job:
            self.current_job.terminate()

    def check_job_status(self, id):
        """Keep checking job status"""
        while self.current_job.is_alive():
            _LOGGER.debug("Checking job status")
            job = api.get_job(id)
            if job['state'] == 'paused':
                self.current_job.terminate()
                break
            time.sleep(60)

    def status(self):
        return self.current_job.get_status()


if __name__ == '__main__':
    app = TrainingApp()
    app.start(True)
