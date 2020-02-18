#!/usr/bin/env python3
import urllib3
from kubernetes import client, config
from kubernetes.client.rest import ApiException

urllib3.disable_warnings()

config.load_kube_config()
api = client.CoreV1Api()
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
                print('deleting', pod.metadata.name, 'in', pod.metadata.namespace)
                api.delete_namespaced_pod(pod.metadata.name, pod.metadata.namespace)
