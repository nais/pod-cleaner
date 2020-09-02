#!/usr/bin/env python3
import kubernetes
import sys

import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import argparse

ignored_namespaces = ['kube-system', 'reboot-coordinator']

parser = argparse.ArgumentParser(description="Pod Cleaner")
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()

print("dry-run" if args.dry_run else 'wet-run')

try:
    config.load_incluster_config()
except kubernetes.config.config_exception.ConfigException as e:
    try:
        config.load_kube_config()
    except kubernetes.config.config_exception.ConfigException as e2:
        print(e)
        print(e2)
        sys.exit(1)

api = client.CoreV1Api()
namespaces = api.list_namespace()
for namespace in namespaces.items:
    namespace_name = namespace.metadata.name

    if namespace_name in ignored_namespaces:
        continue

    pods = api.list_namespaced_pod(namespace=namespace_name)
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
