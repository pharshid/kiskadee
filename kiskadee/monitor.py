import kiskadee.model
from kiskadee.queue import analysis_enqueue, package_dequeue, \
        package_enqueue
import threading
from threading import Thread
from multiprocessing import Process

running = True


def sync_analyses():
    """enqueues package versions without analyses in the db for analysis"""
    # sweep db for versions without analyses
    # if queue empty
    # enqueue all
    # else: check the queue for each package version and running jobs?
    # run analysis on the one not in queue nor under analysis
    # we could also empty the queue in the very begining of this task
    pass


def monitor():
    plugins = kiskadee.load_plugins()
    for plugin in plugins:
        plugin_name = plugin.__name__.split('.')[len(__name__.split('.')) - 1]
        print("Collecting data for %s plugin \n" % plugin_name)
        consumer_queue = Thread(target=save_or_update_pkgs,
                                args=(plugin_name,))
        consumer_queue.daemon = True
        consumer_queue.start()
        plugin_thread = Thread(target=plugin.watch)
        plugin_thread.daemon = True
        plugin_thread.start()
        plugin_thread.join()


def enqueue_source(func):
    def wrapper(*args, **kwargs):
        sources = func(*args, **kwargs)
        for source in sources:
            analysis_enqueue(source)
    return wrapper


def enqueue_pkg(func):
    def wrapper(*args, **kwargs):
        package = func(*args, **kwargs)
        package_enqueue(package)
    return wrapper


def save_or_update_pkgs(plugin_name):
    queue_file = "%s_queue_output" % plugin_name
    print("Writing output in %s file" % queue_file)
    with open(queue_file, '+w') as target:
        while True:
            # In the future we will use some logging tool to do this.
            target.write("dequed package: %s \n" % str(package_dequeue()))
            # Database stuff here.

def daemon():
    # TODO: improve with start/stop system
    p = Process(target=monitor)
    p.daemon = True
    p.start()
    p.join()
    # cleanup goes here
