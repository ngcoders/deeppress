import sys
import logging
import tensorflow as tf
import time
import threading
from queue import Queue
from functools import wraps
from logging.handlers import QueueHandler


from bottle import route, run, install
import api
from job import TrainingJob
import config
from web import AuthPlugin


tf.logging.set_verbosity(tf.logging.INFO)

# Add handler to get current status of training


_LOGGER = logging.getLogger('deeppress')
_LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
# log_queue = Queue(10)
# qh = QueueHandler(log_queue)
# add formatter to ch
ch.setFormatter(formatter)
_LOGGER.addHandler(ch)
# _LOGGER.addHandler(qh)


class TrainingApp(object):

    def __init__(self):
        self.current_job = None

    def run(self):
        self.run_server()
        jobs = {}
        try:
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
                            time.sleep(120)
                            page = 1
                            continue

                        for record in data:
                            self.current_job = None
                            if record['done']:
                                _LOGGER.debug("Job already done")
                                continue
                            if record['state'] == 'paused':
                                _LOGGER.debug("Job is paused")
                                continue

                            self.current_job = TrainingJob(record)
                            self.current_job.start()
                            # TODO: Run loop to check job status from server
                            self.check_job_status(record['id'])
                            self.current_job.join()
                            self.current_job = None
                            page = 1
                            break

                        # if len(jobs) == total:
                        #     break
                    else:
                        # Invalid data
                        time.sleep(120)
                except Exception as e:
                    _LOGGER.error(e)
                    time.sleep(120)
        except Exception as e:
            _LOGGER.error(e)
            _LOGGER.error("Failed to get records")
            exit(-1)

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

    def run_server(self):
        """Start the webserver in a thread"""
        t = threading.Thread(target=run, args=(), kwargs={"host": "localhost", "port":8080})
        t.daemon = True
        t.start()

    def register_routes(self):
        """List all the application routes"""
        @route('/status', auth='basic')
        def status():
            """Check the current job status"""
            if self.current_job:
                return self.current_job.get_status()
            return {"message": "No job running"}

        @route('/stop', auth='basic')
        def stop():
            """Stop the running job"""
            self.stop()

        # @route('/logs')
        # def get_logs():
        #     """Get log messages"""
        #     all_msg = []
        #     while True:
        #         try:
        #             record = log_queue.get_nowait()
        #             if record:
        #                 all_msg.append("%s %s : %s" % (record.asctime, record.levelname, record.getMessage()))
        #         except:
        #             break
        #
        #         if len(all_msg) > 10:
        #             break
        #
        #     return {"log": all_msg}

if __name__ == '__main__':

    install(AuthPlugin(config.LOCAL_AUTH_TOKEN))
    app = TrainingApp()
    app.register_routes()
    app.run()
