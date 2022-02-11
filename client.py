#!/bin/env python3

import socket
import os
import sys
import glob
from ftplib import FTP
from func import fileProperty, getHash
import hashlib
import threading
from time import sleep
import queue
import logger as lg

# defns
concurrent_connections = 1
directory_path = ''
server_address = ''
server_host = '127.0.0.1'
server_port = 5000
server_timeout = 10
q = queue.Queue()
tasks = []

def usage():
    print('Usage: {} [server_address] [directory_path] [concurrent_connections]'.format(os.path.basename(sys.argv[0])))
    sys.exit()

# Worker, handles each task
def worker():
    while True:
        item = q.get()
        if item is None:
            break
        upload_files(item)
        sleep(1)
        q.task_done()


def start_workers(worker_pool=1000):
    threads = []
    for i in range(worker_pool):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    return threads


def stop_workers(threads):
    # stop workers
    for i in threads:
        q.put(None)
    for t in threads:
        t.join()

def create_queue(task_items):
    for item in task_items:
        q.put(item)

def upload_files(file_name):
    lg.default('[🗂] Processing: {}'.format(file_name))
    file = open(file_name, 'rb')
    file_hash = getHash(file)
    fp = FTP()
    fp.connect(host=server_host, port=server_port, timeout=server_timeout)
    fp.storbinary(cmd='STOR '+ file_name + ';' + file_hash, fp=file, callback=upload_callback)

def process_files(directory_path):
    global server_host, server_port, tasks
    tasks = []
    for file_name in glob.iglob('{}/**'.format(directory_path), recursive=True):
        if os.path.isfile(file_name):
            tasks.append(file_name)

def upload_callback(data):
    print(data)


def main():
    global directory_path, concurrent_connections, server_address, server_host, server_port

    # validate cli inputs
    if len(sys.argv) < 3:
        usage()

    server_address = sys.argv[1]
    directory_path = sys.argv[2]

    if len(sys.argv) == 4:
        concurrent_connections = int(sys.argv[3])

    _server = server_address.split(':')
    server_host = _server[0]
    server_port = int(_server[1])

    process_files(directory_path)

    # Start up workers
    workers = start_workers(worker_pool=concurrent_connections)
    create_queue(tasks)

    # Blocks until all tasks are complete
    q.join()

    stop_workers(workers)

if __name__ == '__main__':
    main()