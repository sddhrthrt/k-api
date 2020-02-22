#!/usr/bin/env python

import sys

from service_cli import ServiceCLI

def create(path, fileURL):
    service_cli = ServiceCLI()
    existing_services = service_cli.list_services()
    if path in existing_services:
        print(f"Service already exists for path /{path}. Not creating another one.")
        return
    deployment = service_cli.create_deployment_object(path, fileURL)
    service_cli.create_deployment(deployment)
    service_cli.create_service(path)
    service_cli.add_ingress_path(path)

def delete(path):
    service_cli = ServiceCLI()
    existing_services = service_cli.list_services()
    if path not in existing_services:
        print(f"Can't find service for path /{path}. Cleaning up anything else left.")
    else:
        print(f"Cleaning up /{path}.")
    service_cli.delete_deployment(path)
    service_cli.delete_service(path)
    service_cli.delete_ingress_path(path)

if __name__=='__main__':
    task = None
    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        print(f"""Argument not found.
Usage:

{sys.argv[0]} create path fileURL
{sys.argv[0]} delete path
{sys.argv[0]} list
              """)
    if task == "create":
        if len(sys.argv) < 3:
            print(f"Usage: {sys.argv[0]} create path fileURL")
        else:
            path, fileURL = sys.argv[2:4]
            print(f"Creating /{path} to serve {fileURL}...")
            create(path, fileURL)
    if task == "delete":
        if len(sys.argv) < 2:
            print(f"Usage: {sys.argv[0]} delete path")
        else:
            path = sys.argv[2]
            delete(path)
    if task == "list":
        service_cli = ServiceCLI()
        existing_services = service_cli.list_services()
        if len(existing_services):
            print(f"Existing services:")
            for s in existing_services:
                print(f"- {s}")
        else:
            print(f"No services running.")
        
