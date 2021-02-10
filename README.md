# Ansible Playbook JSON to YAML

Before starting, for details on Ansible Docs, refer to [Ansible Docs](https://docs.ansible.com/ansible/2.8/modules/modules_by_category.html)

## Overview

The idea is to build a single production grade Flask API with the following

      • Expose API to convert input JSON and return the proper Ansible Playbook YAML

## Motivation

To avoid the pain points of

      • Manually taking care of indentation or special characters.
      
      • Ease of interaction with UI technologies like Angular

## Tech / Framework used

      --> Docker Image to host the Flast app. 
	  			
      --> Python 3 & Flask

## Containerization CI (Continuous Integration)

| CI Provider | Status          |
| ------- | ------------------ |
| Docker   | ![Docker](https://github.com/maheshyaddanapudi/ansible-playbook-json2yaml/workflows/Docker/badge.svg?branch=main) |
| Docker Image CI   | ![Docker Image CI](https://github.com/maheshyaddanapudi/ansible-playbook-json2yaml/workflows/Docker%20Image%20CI/badge.svg?branch=main) |

Docker Image published to <a href="https://hub.docker.com/repository/docker/zzzmahesh/ansible-playbook-json2yaml" target="_blank">DockerHub here</a>

Image is equipped with production ready Nginx & UWSGI 

To pull the image :

	docker pull zzzmahesh/ansible-playbook-json2yaml

## Run : Python

		cd <to project root folder>/target
		
	Below command will start the application
		python3 main.py

## Application URLs

		http://localhost:8080 - To access the POST API

## Run ansible Boot : Docker

To run the container :

    docker run --name ansible-playbook-json2yaml -p 8080:8080 -d zzzmahesh/ansible-playbook-json2yaml:latest

## API I/O

### Input Sample

        [
            {
                "name": "Play 1",
                "hosts": "all",
                "gather_facts": false,
                "vars": [{"sample_var_1":"Hi"}, {"sample_var_2":"Hi"}],
                "modules": [
                    {
                    "name": "Custom task definition 1 1",
                    "module": "shell",
                    "become": "ansible-docs-boot",
                    "become_method": "su",
                    "input_fields": {
                        "cmd": "echo {{sample_var_1}}"
                    }
                },
                {
                    "name": "Custom task definition 1 2",
                    "module": "shell",
                    "delegate_to": "localhost",
                    "become": "ansible-docs-boot",
                    "become_method": "su",
                    "input_fields": {
                        "cmd": "echo {{sample_var_2}}"
                    }
                }
                ]
            },
            {
                "name": "Play 2",
                "hosts": "all",
                "gather_facts": false,
                "vars": [{"sample_var_3":"Hi"}, {"sample_var_4":"Hi"}],
                "modules": [
                    {
                    "name": "Custom task definition 2 1",
                    "module": "shell",
                    "delegate_to": "localhost",
                    "input_fields": {
                        "cmd": "echo {{sample_var_3}}"
                    }
                },
                {
                    "name": "Custom task definition 2 2",
                    "module": "shell",
                    "delegate_to": "localhost",
                    "become": "ansible-docs-boot",
                    "become_method": "su",
                    "input_fields": {
                        "cmd": "echo {{sample_var_4}}"
                    }
                }
                ]
            }
        ]

###Output Sample
        ---
        - gather_facts: false
          hosts: all
          name: Play_1 - Play 1
          tasks:
          - action:
              args: cmd="echo {{sample_var_1}}"
              module: shell
            become: true
            become_method: su
            become_user: ansible-docs-boot
            name: Task_1 - Custom task definition 1 1
            no_log: false
            register: Task_1_out
          - action:
              args: cmd="echo {{sample_var_2}}"
              module: shell
            become: true
            become_method: su
            become_user: ansible-docs-boot
            delegate_to: localhost
            name: Task_2 - Custom task definition 1 2
            no_log: false
            register: Task_2_out
          vars:
          - sample_var_1: Hi
          - sample_var_2: Hi
        - gather_facts: false
          hosts: all
          name: Play_2 - Play 2
          tasks:
          - action:
              args: cmd="echo {{sample_var_3}}"
              module: shell
            delegate_to: localhost
            name: Task_1 - Custom task definition 2 1
            no_log: false
            register: Task_1_out
          - action:
              args: cmd="echo {{sample_var_4}}"
              module: shell
            become: true
            become_method: su
            become_user: ansible-docs-boot
            delegate_to: localhost
            name: Task_2 - Custom task definition 2 2
            no_log: false
            register: Task_2_out
          vars:
          - sample_var_3: Hi
          - sample_var_4: Hi
