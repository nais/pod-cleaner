#!/usr/bin/env python3

# Std libs
import unittest

# 1st party deps
from cleanup import should_pod_be_deleted

# 3rd party deps
from kubernetes import client


class TestCleanup(unittest.TestCase):
    def test_should_pod_be_deleted_for_not_running_pod(self):
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


if __name__ == '__main__':
    unittest.main()
