#!/usr/bin/env python3

# Std libs
import argparse
import sys

import kubernetes
import urllib3
# 3rd party deps
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def pod_is_terminated(pod) -> bool:
    try:
        reason = pod.status.reason
    except Exception:
        return False

    if reason == 'Terminated':
        return True

    return False


def no_node_for_pod(pod) -> bool:
    try:
        reason = pod.status.reason
    except Exception:
        return False

    if reason == 'NodeAffinity':
        return True

    return False


def container_cannot_run(pod) -> bool:
    try:
        containers = pod.status.container_statuses
    except Exception:
        return False

    if not containers:
        return False

    for container in containers:
        try:
            if container.last_state.terminated.reason == 'ContainerCannotRun':
                return True
        except Exception:
            continue

    return False


def should_pod_be_deleted(pod) -> bool:
    return pod_is_terminated(pod) or container_cannot_run(pod) or no_node_for_pod(pod)


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
    urllib3.disable_warnings()

    try:
        config.load_incluster_config()
    except kubernetes.config.config_exception.ConfigException:
        try:
            config.load_kube_config()
        except kubernetes.config.config_exception.ConfigException as e2:
            raise e2

    parser = argparse.ArgumentParser(description="Pod Cleaner")
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    print("dry-run" if args.dry_run else 'wet-run')

    api = client.CoreV1Api()
    for namespace in get_namespaces_to_check(api):
        if args.dry_run or args.verbose:
            print(f"Checking namespace: {namespace.metadata.name}")
        for pod in get_pods_to_check(namespace, api, args.dry_run):
            if args.dry_run:
                print('dry-run: would have deleted',
                      pod.metadata.name, 'in', pod.metadata.namespace)
                continue

            try:
                print('deleting', pod.metadata.name,
                      'in', pod.metadata.namespace)
                api.delete_namespaced_pod(
                    pod.metadata.name, pod.metadata.namespace)
            except ApiException as e:
                print('exception while deleting: ', e)
