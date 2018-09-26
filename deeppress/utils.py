import logging
import re
import threading
import time

import api

_LOGGER = logging.getLogger('deeppress.utils')


class TFLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.msg = ""

    def emit(self, record):
        self.acquire()
        self.msg = self.format(record)
        self.release()

    def get_status(self, total_steps=50000):
        regex = r"global.step.(?P<steps>\d+).*loss.=.(?P<loss>\d+\.\d+).*(?P<time>\d+\.\d+).*sec/step"
        self.acquire()
        msg = self.msg
        self.release()
        m = re.match(regex, msg, re.MULTILINE)
        if m:
            steps = int(m.group('steps'))
            loss = float(m.group('loss'))
            sec_per_step = float(m.group('time'))
            return steps, loss, sec_per_step
        return None, None, None


class StatusThread(threading.Thread):
    def __init__(self, handler, num_steps, job):
        threading.Thread.__init__(self)
        self.job = job
        self.num_steps = num_steps
        self.handler = handler
        self.running = True

    def run(self):
        while self.running:
            steps, loss, sec_per_step = self.handler.get_status()
            if steps:
                eta_sec = sec_per_step * (int(self.num_steps - steps))
                eta_min = eta_sec//60
                eta = "{}h{}m".format(int(eta_min//60), int(eta_min % 60))
                status = "Steps: {}/{} | Loss: {} | ETA: {}".format(steps, self.num_steps, loss, eta)
                _LOGGER.info(status)
                api.update_job_state(self.job, status)
            time.sleep(60)

    def stop(self):
        self.running = False