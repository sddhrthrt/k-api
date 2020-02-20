### A sample CLI for deploying apps on kubernetes.

## Setup
- Run k3s locally.
- Enable a kubernetes api proxy using `kubectl proxy --port=8080 &`
- Make sure the `~/kube/k3s.yaml` file (copied from `/etc/rancher/k3s/k3s.yaml`) has the right port (8080)
- Set up a [local docker repo](https://www.docker.com/blog/how-to-use-your-own-registry/) at say, `localhost:5000`
- [Add this repo to your `k3s.yaml`](https://rancher.com/docs/k3s/latest/en/installation/private-registry/)
- Build docker for `file_server` - I used `cd file_server; docker build -t localhost:5000/file-server:latest`
- Run `python cli.py create` to create a `file_server` instance.

## Todo:
- Enable passing `path` and `file URL` args to docker (docker already accepts them, just need to accept those args from cli and pass them on to the `container` object.
- Create ingress so as to access the API endpoint from `localhost`.
- Enable multiple endpoints
  - Add a deployment
  - Patch the service
  - Add an ingress
- Manage creation and deletion of multiple endpoints using `label` fields in metadata. 
  - List endpoints based on `label` metadata.
  - Delete deployment, patch service and patch ingresses
- Write cli in Go (because I want to be able to write ground-up services in Go)

## Usage:

```
python cli.py create
python cli.py delete
```

The CLI object can also be used from code:

```
from service_cli import ServiceCLI
s = ServiceCLI()
s.create_deployment(s.create_deployment_object())
s.create_service()
```

