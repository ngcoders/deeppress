from __future__ import absolute_import

import sys
import logging

import time
import threading

from deeppress import api
from deeppress.classifier_backend_main import ClassificationJob


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
                if not isinstance(res, dict) or 'data' not in res.keys():
                    break
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
                        from deeppress.job import TrainingJob
                        self.current_job = TrainingJob(record)
                        self.current_job.start()
                        if join:
                            self.current_job.join()
                        return True
                    if record['model_type'] == 'classifier':
                        self.current_job = ClassificationJob(record)
                        _LOGGER.debug(record)
                        self.current_job.start()
                        if join:
                            self.current_job.join
                            _LOGGER.debug("Training complete")
                        return True
                    else:
                        _LOGGER.error(f"Training for model type {record['model_type']} not implemented")

                                    # page = 1
                                    # break
            except Exception as e:
                _LOGGER.exception(e)
        return False

    def stop(self):
        import psutil
        def kills(pid):
            ''' Kills the parent and all spawned child processes '''
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                # _LOGGER.debug(f'killing {child.pid}')
                child.kill()
            # _LOGGER.debug(f'killing {parent.pid}')
            parent.kill()
        
        if self.current_job:
            _LOGGER.debug("Terminating active jobs")
            kills(self.current_job.pid)
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
