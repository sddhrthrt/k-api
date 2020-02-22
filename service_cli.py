import os

from kubernetes import client, config


"""
based on https://github.com/kubernetes-client/python/blob/master/examples/deployment_crud.py
"""
NAMESPACE="file-server"
CONFIG_FILE='~/.kube/k3s.yaml'

class ServiceCLI:
    def __init__(self):
        config.load_kube_config(CONFIG_FILE)
        self.instantiate_api('apps_api', client.AppsV1Api)
        self.instantiate_api('core_api', client.CoreV1Api)
        self.instantiate_api('networking_v1_beta1_api', client.NetworkingV1beta1Api)

    def instantiate_api(self, attr, api, debug=False):
        api_instance = api()
        if debug:
            c = client.Configuration()
            c.debug = True
            api_instance = api(api_client=client.ApiClient(configuration=c))
        setattr(self, attr, api_instance)

    """
    SERVICES
    """
    def create_service(self, path):
        """ Ideally, we'd have one service and multiple deployments (with each path/file being served).
        On GKE, though, ingress doesn't allow replacement (IP/path > IP), this means we can't change the """
        body = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(
                    name=path
                    ),
                spec=client.V1ServiceSpec(
                    selector={'path': path},
                    ports=[client.V1ServicePort(
                        port=5000,
                        target_port=5000
                        )],
                    type="LoadBalancer"
                    ),
                )
        self.core_api.create_namespaced_service(namespace=NAMESPACE, body=body)

    def delete_service(self, path):
        self.core_api.delete_namespaced_service(name=path, namespace=NAMESPACE)

    def list_services(self):
        services = self.core_api.list_namespaced_service(namespace=NAMESPACE)
        return [s.metadata.name for s in services.items]

    def create_ingress_object(self, path):
        ingress = client.NetworkingV1beta1Ingress(
            api_version="networking.k8s.io/v1beta1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(name="file-server-ingress", annotations={
                "nginx.ingress.kubernetes.io/rewrite-target": "/"
            }),
            spec=client.NetworkingV1beta1IngressSpec(
                rules=[client.NetworkingV1beta1IngressRule(
                    http=client.NetworkingV1beta1HTTPIngressRuleValue(
                        paths=[client.NetworkingV1beta1HTTPIngressPath(
                            path=os.path.join("/", path),
                            backend=client.NetworkingV1beta1IngressBackend(
                                service_port=5000,
                                service_name=path))]
                    )
                )]
            )
        )
        return ingress
    
    """
    INGRESSES
    """
    def create_ingress(self, ingress):
        api_response = self.networking_v1_beta1_api.create_namespaced_ingress(
                body=ingress,
                namespace=NAMESPACE)
        print(f"Ingress created. Status={api_response.status}")

    def delete_ingress(self):
        api_response = self.networking_v1_beta1_api.delete_namespaced_ingress(
                name="file-server-ingress",
                namespace=NAMESPACE,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                    grace_period_seconds=5))
        print(f"Ingress deleted. status={api_response.status}")

    def add_ingress_path(self, path):
        ingress = self.get_ingress()

        if ingress is None:
            self.create_ingress(self.create_ingress_object(path))
            ingress = self.get_ingress()
        else:
            newpath = client.NetworkingV1beta1HTTPIngressPath(
                path=os.path.join("/", path),
                backend=client.NetworkingV1beta1IngressBackend(
                    service_port=5000,
                    service_name=path))

            ingress.spec.rules[0].http.paths.append(newpath)
            self.networking_v1_beta1_api.patch_namespaced_ingress(
                name="file-server-ingress",
                namespace=NAMESPACE, body=ingress)
        print(f"New ingress path added: {path}.")

    def delete_ingress_path(self, path):
        ingress = self.get_ingress()
        if ingress is None:
            return
        found = -1
        path = os.path.join("/", path)
        paths = ingress.spec.rules[0].http.paths
        for i in range(len(paths)):
            if paths[i].path == path:
                found = i
        if found > -1:
            paths = paths[:i] + paths[i+1:]
            if len(paths) == 0:
                self.delete_ingress()
            else:
                ingress.spec.rules[0].http.paths = paths
                self.networking_v1_beta1_api.patch_namespaced_ingress(
                    name="file-server-ingress",
                    namespace=NAMESPACE,
                    body=ingress)
            print(f"Path removed: {path}.")
        else:
            print(f"Path not found: {path}.")

    def get_ingress(self):
        ingress = self.networking_v1_beta1_api.list_namespaced_ingress(namespace=NAMESPACE).items
        return ingress[0] if len(ingress) else None

    """
    DEPLOYMENTS
    """
    def create_deployment_object(self, path, fileURL):
        ingress = self.get_ingress()
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=path),
            spec=client.V1DeploymentSpec(
                replicas=1,
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"path": path}),
                    spec=client.V1PodSpec(containers=[client.V1Container(
                        name=path,
                        image="gcr.io/mlexperiments-192901/file-server:latest",
                        ports=[client.V1ContainerPort(container_port=5000)],
                        image_pull_policy="Always",
                        args=[fileURL, path])])
                ),
                selector={'matchLabels': {"path": path}}
            )
        )

        return deployment

    def create_deployment(self, deployment):
        api_response = self.apps_api.create_namespaced_deployment(
                body=deployment,
                namespace=NAMESPACE)
        print(f"Deployment created. Status={api_response.status}")

    def delete_deployment(self, path):
        api_response = self.apps_api.delete_namespaced_deployment(
                name=path,
                namespace=NAMESPACE,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                    grace_period_seconds=5))
        print(f"Deployment deleted. status={api_response.status}")


