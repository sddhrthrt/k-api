import sys

from service_cli import ServiceCLI


def main(task):
    if task is None:
        return
    service_cli = ServiceCLI()
    deployment = service_cli.create_deployment_object()
    
    if task == 'create':
        service_cli.create_deployment(deployment)
    if task == 'delete':
        service_cli.delete_deployment()

if __name__=='__main__':
    task = None
    if len(sys.argv) > 0:
        task = sys.argv[1]
    print(f"starting {task}...")
    main(task)
