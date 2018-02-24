"""Provide kiskadee queues and operations on them."""
import time
from multiprocessing import Queue

import kiskadee

def empty_queue(func):
    """Decorator that checks if retrieve data from a
    queue will trigger a empty exception.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return {}
    return wrapper

def enqueue_project(fetcher_watch):
    """Decorator to be used with watch fetchers method. Every project returned
    by the watch method, will be enqueued on the queue projects.
    :arg1: watch method
    :returns: a wrapper variable
    """
    def wrapper(*args, **kwargs):
        project = fetcher_watch(*args, **kwargs)
        kiskadee.queue.queues.enqueue_project(project)
        fetcher = project['fetcher'].name
        kiskadee.logger.debug(
                "{} fetcher: sending package {}_{} for monitor"
                .format(fetcher, package['name'], package['version'])
            )
        time.sleep(2)
    return wrapper

analysis = Queue()
results = Queue()
projects = Queue()

class Queues():
    """Provide kiskadee queues objects."""

    @staticmethod
    def enqueue_analysis(project_to_analysis):
        """Put a analysis on the analysis queue."""
        log_msg = "Sending project {}_{} for analysis"\
                .format(project_to_analysis['name'],
                        project_to_analysis['version'])
        kiskadee.logger.debug(log_msg)
        analysis.put(project_to_analysis)

    @staticmethod
    def dequeue_analysis():
        """Get a analysis from the analysis queue."""
        project_to_analysis = analysis.get()
        kiskadee.logger.debug(
                'RUNNER: deqeued {}-{} from {}'
                .format(project_to_analysis['name'],
                        project_to_analysis['version'],
                        project_to_analysis['fetcher'])
            )
        return project_to_analysis

    @staticmethod
    def enqueue_result(project):
        """Put a result on the results queue."""
        kiskadee.logger.debug(
                "RUNNER: Sending {}-{} to Monitor"
                .format(project["name"],
                        project["version"])
            )
        results.put(project)

    @staticmethod
    @empty_queue
    def dequeue_result():
        """Get a result from the results queue."""
        return results.get(timeout=1)

    @staticmethod
    def enqueue_project(project):
        """Put a result on the results queue."""
        projects.put(project)

    @staticmethod
    @empty_queue
    def dequeue_project():
        """Get a result from the results queue."""
        return projects.get(timeout=1)
