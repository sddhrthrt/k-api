from kubernetes import client, config


"""
based on https://github.com/kubernetes-client/python/blob/master/examples/deployment_crud.py
"""
DEPLOYMENT_NAME="file-server"
NAMESPACE="file-server"
CONFIG_FILE='~/.kube/k3s.yaml'

class ServiceCLI:
    def __init__(self):
        config.load_kube_config(CONFIG_FILE)
        self.instantiate_api('apps_api', client.AppsV1Api, debug=True)
        self.instantiate_api('core_api', client.CoreV1Api, debug=True)
        self.instantiate_api('networking_v1_beta1_api', client.NetworkingV1beta1Api, debug=True)

    def instantiate_api(self, attr, api, debug=False):
        api_instance = api()
        if debug:
            c = client.Configuration()
            c.debug = True
            api_instance = api(api_client=client.ApiClient(configuration=c))
        setattr(self, attr, api_instance)

    def create_service(self):
        #TODO: check if service already exists. we need a monolith service
        body = client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(
                    name="file-server-service",
                    ),
                spec=client.V1ServiceSpec(
                    selector={'app': 'file-server'},
                    ports=[client.V1ServicePort(
                        port=5000,
                        target_port=5000
                        )],
                    type="LoadBalancer"
                    ),
                )
        self.core_api.create_namespaced_service(namespace=NAMESPACE, body=body)

    def create_ingress_object(self):
        ingress = client.NetworkingV1beta1Ingress(
            api_version="networking.k8s.io/v1beta1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(name="file-server-ingress", annotations={
                'kubernetes.io/ingress.class': 'traefik'
            }),
            spec=client.NetworkingV1beta1IngressSpec(
                rules=[client.NetworkingV1beta1IngressRule(
                    host="file-server-ingress",
                    http=client.NetworkingV1beta1HTTPIngressRuleValue(
                        paths=[client.NetworkingV1beta1HTTPIngressPath(
                            path="/thispath",
                            backend=client.NetworkingV1beta1IngressBackend(
                                service_port=5000,
                                service_name="file-server-service"
                            ))]
                    )
                )]
            )
        )
        return ingress

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


    def create_deployment_object(self):
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
            spec=client.V1DeploymentSpec(
                replicas=1,
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": "file-server"}),
                    spec=client.V1PodSpec(containers=[client.V1Container(
                        name="file-server-service",
                        image="localhost:5000/file-server:latest",
                        ports=[client.V1ContainerPort(container_port=5000)],
                        image_pull_policy="Always")
                    ])
                ),
                selector={'matchLabels': {'app': 'file-server'}}
            )
        )

        return deployment

    def create_deployment(self, deployment):
        api_response = self.apps_api.create_namespaced_deployment(
                body=deployment,
                namespace=NAMESPACE)
        print(f"Deployment created. Status={api_response.status}")

    def delete_deployment(self):
        api_response = self.apps_api.delete_namespaced_deployment(
                name=DEPLOYMENT_NAME,
                namespace=NAMESPACE,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                    grace_period_seconds=5))
        print(f"Deployment deleted. status={api_response.status}")


