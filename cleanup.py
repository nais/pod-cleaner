#!/usr/bin/env python3
import sys

import urllib3
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import argparse

parser = argparse.ArgumentParser(description="Pod Cleaner")
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()

print("dry-run" if args.dry_run else 'wet-run')

config.load_incluster_config()
api = client.CoreV1Api()
while True:
    pods = api.list_pod_for_all_namespaces()

    for pod in pods.items:
        if pod.status and \
                pod.status.container_statuses:
            for container_status in pod.status.container_statuses:
                if not container_status.ready \
                        and container_status.last_state \
                        and container_status.last_state.terminated \
                        and container_status.last_state.terminated.reason \
                        and container_status.last_state.terminated.reason == 'ContainerCannotRun':
                    if args.dry_run:
                        print('dry-run: would have deleted', pod.metadata.name, 'in', pod.metadata.namespace)
                    else:
                        try:
                            print('deleting', pod.metadata.name, 'in', pod.metadata.namespace)
                            api.delete_namespaced_pod(pod.metadata.name, pod.metadata.namespace)
                        except ApiException as e:
                            print('exception while deleting: ', e)
