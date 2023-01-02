#!/usr/bin/env python


import os
import subprocess
import sys
import time

import kubernetes
# 3rd party deps
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# constants
TEST_NAMESPACE = 'test-pod-cleaner'
TEST_IMAGE = 'nginx'


def create_pod(api, name, namespace, image, cmd):
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name=name,
                    image=image,
                    command=cmd)]))

    return api.create_namespaced_pod(namespace=namespace, body=pod)


def create_pods(api, namespace, image):
    create_pod(api, 'test-completed', namespace, image, ['nginx'])
    create_pod(api, 'test-running', namespace,
               image, ['nginx', '-g', 'daemon off;'])
    create_pod(api, 'test-crashloop', namespace, image, ['exit 1'])
    create_pod(api, 'test-can-not-run', namespace, image, ['foo'])

    while True:
        pod = api.read_namespaced_pod(name='test-running', namespace=namespace)
        print(
            f"Waiting for pod {pod.metadata.name} to be running: {pod.status.phase}")
        if pod.status.phase == 'Running':
            break
        time.sleep(1)


def create_namespace(api, name):
    namespace = client.V1Namespace()
    namespace.metadata = client.V1ObjectMeta(name=name)
    api.create_namespace(body=namespace)

    while True:
        namespace = api.read_namespace(name=name)
        print(
            f"Waiting for namespace {name} to be created, status: {namespace.status.phase}")
        if namespace.status.phase == 'Active':
            return namespace
        time.sleep(1)


def delete_namespace(api, name):
    return api.delete_namespace(name=name)


def namespace_name(name):
    return f"{name}-{int(time.time())}"


def run_cleanup():
    return subprocess.run(
        [sys.executable, 'cleanup.py', '--verbose', '--debug'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)


def ask_and_exit(exit_code=0):
    if os.getenv('CI') == 'true':
        sys.exit(exit_code)

    prompt = input(f"Clean up namespace {namespace}? [y/N] ")
    if prompt.lower() == 'y':
        print("Deleting namespace")
        delete_namespace(api, namespace)

    sys.exit(exit_code)


if __name__ == '__main__':
    print("loading kube config")
    try:
        config.load_incluster_config()
    except kubernetes.config.config_exception.ConfigException:
        try:
            config.load_kube_config()
        except kubernetes.config.config_exception.ConfigException as e2:
            raise e2

    api = client.CoreV1Api()
    namespace = namespace_name(TEST_NAMESPACE)

    print(f"Creating namespace: {namespace}")
    create_namespace(api, namespace)

    print("Creating pods")
    create_pods(api, namespace, TEST_IMAGE)

    print("Waiting for good luck")
    time.sleep(30)

    print("Starting cleanup.py")
    cleanup = run_cleanup()

    print(cleanup.stdout)
    print(cleanup.stderr)

    if cleanup.returncode != 0:
        print("cleanup.py failed")
        ask_and_exit(1)

    print("Waiting 30s for pods to be removed from API-server...")
    time.sleep(60)

    print("Checking remaining pods")
    pods = api.list_namespaced_pod(namespace=namespace).items
    for pod in pods:
        if pod.metadata.name in ('test-can-not-run', 'test-crashloop'):
            print(f"Pod {pod.metadata.name} was not deleted")
            print(pod)
            ask_and_exit(1)

    ask_and_exit(0)
