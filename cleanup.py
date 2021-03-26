#!/usr/bin/env python3

# Std libs
import argparse
import contextlib
import sys
import time
import urllib3

# 3rd party deps
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import kubernetes

urllib3.disable_warnings()
try:
    config.load_incluster_config()
except kubernetes.config.config_exception.ConfigException as e:
    try:
        config.load_kube_config()
    except kubernetes.config.config_exception.ConfigException as e2:
        raise e2
        sys.exit(1)


def should_pod_be_deleted(pod)-> bool:
    try:
        containers = pod.status.container_statuses
    except Exception:
        return False

    for container in containers:
        try:
            if container.last_state.terminated.reason == 'ContainerCannotRun':
                return True
        except Exception:
            continue

    return False


def get_namespaces_to_check(api):
    for namespace in api.list_namespace().items:
        if namespace.metadata.name not in ('kube-system', 'reboot-coordinator'):
            yield namespace


def get_pods_to_check(namespace, api, dry_run=False):
    for pod in api.list_namespaced_pod(namespace=namespace.metadata.name).items:
        if dry_run:
            print(f"\tChecking pod: {pod.metadata.name}")
        if should_pod_be_deleted(pod):
            yield pod


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pod Cleaner")
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    print("dry-run" if args.dry_run else 'wet-run')

    api = client.CoreV1Api()
    for namespace in get_namespaces_to_check(api):
        if args.dry_run:
            print(f"Checking namespace: {namespace.metadata.name}")
        for pod_to_be_deleted in get_pods_to_check(namespace, api, args.dry_run):
            if args.dry_run:
                print('dry-run: would have deleted', pod.metadata.name, 'in', pod.metadata.namespace)
                continue

            try:
                print('deleting', pod.metadata.name, 'in', pod.metadata.namespace)
                api.delete_namespaced_pod(pod.metadata.name, pod.metadata.namespace)
            except ApiException as e:
                print('exception while deleting: ', e)
