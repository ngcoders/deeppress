import os
import re
import logging
import threading
import time

from deeppress import api

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


class TailThread(threading.Thread):
    ''' used to tail a file and extract information '''
    def __init__(self, job: dict, num_steps: int, filename: str):
        ''' initialize '''
        super().__init__()
        self.job = job
        self.num_steps = num_steps
        self.filename = filename
        self.running = True

    def first_line_pr(self, msg: str):
        ''' check if the first line of precision recall is available '''
        regex = (
            r'Eval.metrics.at.step.(?P<step>\d+).*'
        )
        search = re.search(regex, msg, re.S ^ re.M ^ re.IGNORECASE)
        return bool(search)

    def get_precision_recall(self, msg: str):
        ''' check if the whole of precision recall is available '''
        scientific_number = r'-?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *-?\ *[0-9]+)?'
        regex = (
            r'Eval.metrics.at.step.(?P<step>\d+).*'
            r'DetectionBoxes_Precision/mAP@.50IOU:.(?P<precision>' + scientific_number + r').*'
            r'DetectionBoxes_Recall/AR@10:.(?P<recall>' + scientific_number + r').*'
            r'Loss/total_loss:.(?P<loss>' + scientific_number + r').*'
            # r'learning_rate.=.(?P<learning_rate>' + scientific_number + r').*'
        )
        if search := re.search(regex, msg, re.S ^ re.M ^ re.IGNORECASE):
            steps = int(search['step'])
            precision = float(search['precision'])
            recall = float(search['recall'])
            loss = float(search['loss'])
            # learning_rate = float(search.group('learning_rate'))
            learning_rate = 0   # dummy
            return (steps, precision, recall, loss, learning_rate)
        return (None, None, None, None, None)

    def tail(self):
        ''' yields the new lines. Works like tail -f '''
        if not os.path.exists(self.filename):
            with open(self.filename, 'w'):
                pass
        with open(self.filename, 'r') as handle:
            handle.seek(0, 2)
            while self.running:
                line = handle.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield line

    def run(self):
        ''' run the thread '''
        while self.running:
            loglines = self.tail()
            multiline_msg = ''
            for line in loglines:
                # get the new lines of the file line by line
                print(line, end='', flush=True)
                multiline_msg += line
                if not self.first_line_pr(multiline_msg):
                    # if the first line is not found, flush the information
                    multiline_msg = ''
                    continue
                # if the first line is found, lets concatenate the message and find the information
                step, precision, recall, loss, learning_rate = self.get_precision_recall(multiline_msg)
                if step is not None:
                    # status = f'{step:6d} {precision:0.6f} {recall:0.6f} {loss:0.6f} {learning_rate:0.6f}'
                    status = f'Steps: {step}/{self.num_steps} Precision: {precision:0.6f} '\
                             f'Recall: {recall:0.6f} Loss: {loss:0.6f}'
                    print(status)
                    api.update_job_state(self.job, 'training', status)
                    multiline_msg = ''

    def stop(self):
        ''' stop the thread '''
        self.running = False
