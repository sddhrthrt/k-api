"""
based on https://github.com/kubernetes-client/python/blob/master/examples/deployment_crud.py
"""
import sys

from kubernetes import client, config


DEPLOYMENT_NAME="file-server"
NAMESPACE="file-server"

def create_deployment_object():
    container = client.V1Container(
            name="file-server-service",
            image="localhost:5000/file-server:latest",
            ports=[client.V1ContainerPort(container_port=5000)])
    template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "file-server"}),
            spec=client.V1PodSpec(containers=[container]))
    spec = client.V1DeploymentSpec(
            replicas=1,
            template=template,
            selector={'matchLabels': {'app': 'file-server'}})
    deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
            spec=spec)

    return deployment

def create_deployment(api_instance, deployment):
    api_response = api_instance.create_namespaced_deployment(
            body=deployment,
            namespace=NAMESPACE)
    print(f"Deployment created. Status={api_response.status}")


def delete_deployment(api_instance):
    api_response = api_instance.delete_namespaced_deployment(
            name=DEPLOYMENT_NAME,
            namespace=NAMESPACE,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
    print(f"Deployment deleted. status={api_response.status}")

def main(task):
    if task is None:
        return
    config.load_kube_config('~/.kube/k3s.yaml')
    apps_v1 = client.AppsV1Api()
    c = client.Configuration()
    c.debug = True
    apps_v1 = client.AppsV1Api(api_client=client.ApiClient(configuration=c))

    deployment = create_deployment_object()
    
    if task == 'create':
        create_deployment(apps_v1, deployment)
    if task == 'delete':
        delete_deployment(apps_v1)

if __name__=='__main__':
    task = None
    if len(sys.argv) > 0:
        task = sys.argv[1]
    print(f"starting {task}...")
    main(task)
