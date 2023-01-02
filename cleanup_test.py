#!/usr/bin/env python3

# Std libs
import unittest

# 1st party deps
from cleanup import should_pod_be_deleted, get_namespaces_to_check, get_pods_to_check

# 3rd party deps
from kubernetes import client


class TestCleanup(unittest.TestCase):
    def test_should_pod_be_deleted_for_cannot_not(self):
        pod = client.V1Pod()
        pod.status = client.V1PodStatus()
        pod.status.container_statuses = [
            client.V1ContainerStatus(
                image='test',
                image_id='test',
                name='test',
                ready=False,
                restart_count=0,
                last_state=client.V1ContainerState(
                    terminated=client.V1ContainerStateTerminated(
                        reason='ContainerCannotRun',
                        exit_code=1,
                    )
                )
            )]
        self.assertTrue(should_pod_be_deleted(pod))

    def test_should_pod_be_deleted_for_other_reason(self):
        pod = client.V1Pod()
        pod.status = client.V1PodStatus()
        pod.status.container_statuses = [
            client.V1ContainerStatus(
                image='test',
                image_id='test',
                name='test',
                ready=False,
                restart_count=0,
                last_state=client.V1ContainerState(
                    terminated=client.V1ContainerStateTerminated(
                        reason='OtherReason',
                        exit_code=1,
                    )
                )
            )]
        self.assertFalse(should_pod_be_deleted(pod))

    def test_should_pod_be_deleted_for_running_pod(self):
        pod = client.V1Pod()
        pod.status = client.V1PodStatus()
        pod.status.container_statuses = [
            client.V1ContainerStatus(
                image='test',
                image_id='test',
                name='test',
                ready=True,
                restart_count=0,
                last_state=client.V1ContainerState(
                    running=client.V1ContainerStateRunning(
                        started_at='2021-09-01T00:00:00Z',
                    )
                )
            )]
        self.assertFalse(should_pod_be_deleted(pod))

    def test_get_namespaces_to_check(self):
        # mock api.list_namespace
        # assert that the correct namespaces are returned

        api = client.CoreV1Api()
        api.list_namespace = lambda: client.V1NamespaceList(
            items=[
                client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name='test'
                    )
                ),
                client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name='kube-system'
                    )
                ),
                client.V1Namespace(
                    metadata=client.V1ObjectMeta(
                        name='reboot-coordinator'
                    )
                ),
            ]
        )

        namespaces = list(get_namespaces_to_check(api))
        self.assertEqual(len(namespaces), 1)
        self.assertEqual(namespaces[0].metadata.name, 'test')

    def test_get_pods_to_check(self):
        # mock api.list_namespaced_pod
        # assert that the correct pods are returned

        api = client.CoreV1Api()
        api.list_namespaced_pod = lambda namespace: client.V1PodList(
            items=[
                client.V1Pod(
                    metadata=client.V1ObjectMeta(
                        name='test'
                    ),
                    status=client.V1PodStatus(
                        container_statuses=[
                            client.V1ContainerStatus(
                                image='test',
                                image_id='test',
                                name='test',
                                ready=False,
                                restart_count=0,
                                last_state=client.V1ContainerState(
                                    terminated=client.V1ContainerStateTerminated(
                                        reason='ContainerCannotRun',
                                        exit_code=1,
                                    )
                                )
                            )
                        ]
                    )
                ),
                client.V1Pod(
                    metadata=client.V1ObjectMeta(
                        name='test2'
                    ),
                    status=client.V1PodStatus(
                        container_statuses=[
                            client.V1ContainerStatus(
                                image='test',
                                image_id='test',
                                name='test',
                                ready=False,
                                restart_count=0,
                                last_state=client.V1ContainerState(
                                    terminated=client.V1ContainerStateTerminated(
                                        reason='OtherReason',
                                        exit_code=1,
                                    )
                                )
                            )
                        ]
                    )
                ),
                client.V1Pod(
                    metadata=client.V1ObjectMeta(
                        name='test3'
                    ),
                    status=client.V1PodStatus(
                        container_statuses=[
                            client.V1ContainerStatus(
                                image='test',
                                image_id='test',
                                name='test',
                                ready=True,
                                restart_count=0,
                                last_state=client.V1ContainerState(
                                    running=client.V1ContainerStateRunning(
                                        started_at='2021-09-01T00:00:00Z',
                                    )
                                )
                            )
                        ]
                    )
                ),
            ]
        )

        namespace = client.V1Namespace(
            metadata=client.V1ObjectMeta(
                name='test'
            )
        )

        pods = list(get_pods_to_check(namespace, api))
        self.assertEqual(len(pods), 1)
        self.assertEqual(pods[0].metadata.name, 'test')


if __name__ == '__main__':
    unittest.main()
