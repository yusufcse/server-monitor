import requests
import time
import signal
import subprocess
import threading
from datetime import timedelta


def _Monitor():
    # replace with your server url
    base_url = "http://127.0.0.1:5000/"
    get_task_queue = "get_task_queue"
    remove_task = "remove_task"
    get_task_definition = "get_task_definition"
    insert_into_task_history = "insert_into_task_history"
    time_out = 10
    # replace
    scripts = "Scripts"
    cmd_line = "Commend_Line"
    http_request = "HTTP Request"
    try:
        resp_queue = requests.get(base_url + get_task_queue, timeout=time_out)
        if resp_queue.status_code != 200:
            return
        else:
            # reading task
            task_queue = list(resp_queue.json())
            # executing tasks
            for item in task_queue:
                # getting task definition
                task_def_id = str(item["task_def_id"])
                try:
                    resp = requests.get(url=base_url + get_task_definition + "/" + task_def_id, timeout=time_out)
                    if resp.status_code == 200:
                        # getting task method and instruction
                        task_def = resp.json()
                        task_run_method = task_def["task_run_method"]
                        task_instruction = task_def["task_instruction"]
                        # executing task according to task run method
                        if scripts in task_run_method:
                            # execute scripts
                            subprocess.call(task_instruction)
                            if _RemoveTask(base_url, remove_task, time_out, item["task_queue_id"]):
                                return
                        elif cmd_line in task_run_method:
                            # run commend line
                            sp = subprocess.run(task_instruction, shell=True)  # shell=True for windows
                            if sp.returncode == 0:
                                if _RemoveTask(base_url, remove_task, time_out, item["task_queue_id"]):
                                    return
                        elif http_request in task_run_method:
                            # send to task_history
                            json_data = {
                                "task_def_id" : str(item["task_def_id"]),
                                "task_info" : str(item["metadata"] + " " + task_instruction),
                                "status_id" : str(item["status_id"])
                            }
                            try:
                                resp = requests.post(url=base_url + insert_into_task_history,
                                                     json=json_data, timeout=time_out)
                                if resp.status_code == 200:
                                    if _RemoveTask(base_url, remove_task, time_out, item["task_queue_id"]):
                                        return
                            except (requests.exceptions.HTTPError,
                                    requests.exceptions.ConnectionError,
                                    requests.exceptions.Timeout,
                                    requests.exceptions.RequestException) as e:
                                print("except :", e)
                except (requests.exceptions.HTTPError,
                        requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException) as e:
                    print("except :", e)
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException) as e:
        print("except :", e)


def _RemoveTask(base_url, remove_task, time_out, task_queue_id):
    try:
        resp = requests.get(url=base_url + remove_task + "/" + str(task_queue_id),
                            timeout=time_out)
        if resp.status_code != 200:
            return True
        else:
            return False
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException) as e:
        print("except :", e)


# make changes to your desire one
WAIT_TIME_SECONDS = 20


class ProgramKilled(Exception):
    pass


def signal_handler(signum, frame):
    raise ProgramKilled


class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    # Start executing after the wait time
    job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=_Monitor)
    job.start()

    while True:
        try:
            time.sleep(1)
        except ProgramKilled:
            print("Program killed: running cleanup code")
            job.stop()
            break
