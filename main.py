from flask import Flask, request, Response
from yaml import load, dump
import json


app = Flask(__name__)


try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


@app.route('/', methods=['POST'])
def playbook_generator():
    playbook = '---'
    try:
        plays = []
        request_json = request.get_json()
        print('Request received : \n'+str(request_json))
        print('Total plays found : '+str(len(request_json)))

        play_counter = 1

        for a_play in request_json:

            play_name = 'Play_'+str(play_counter)+' - '+a_play['name']

            print('Starting preparation of : Play_'+str(play_counter))

            play_counter = play_counter + 1

            tasks = []

            task_counter = 1

            for a_module in a_play['modules']:

                print('Starting preparation of : Task_' + str(task_counter))

                args = ''
                for k, v in a_module['input_fields'].items():
                    if args == '' and v != '' and v is not None and v != 'null':
                        args = args + k + '="' + v + '"'
                    elif v != '' and v is not None and v != 'null':
                        args = args + ' ' + k + '="' + v + '"'

                become_as = ''
                become_method = 'su'
                delegate_to = ''
                no_log = False

                try:
                    become_as = a_module['become']
                    try:
                        become_method = a_module['become_method']
                    except Exception as e:
                        print(str(e) + ' not found in task definition')
                except Exception as e:
                    print(str(e) + ' not found in task definition')

                try:
                    delegate_to = a_module['delegate_to']
                except Exception as e:
                    print(str(e) + ' not found in task definition')

                try:
                    no_log = a_module['no_log']
                except Exception as e:
                    print(str(e) + ' not found in task definition')

                task_name = 'Task_'+str(task_counter)
                
                task_counter = task_counter + 1

                if become_as is None or become_as == '':
                    if delegate_to is None or delegate_to == '':
                        tasks.append(dict(name=task_name+' - '+a_module['name'], action=dict(module=a_module['module'], args=args),
                                          no_log=no_log,
                                          register=task_name + '_out'))
                    else:
                        tasks.append(dict(name=task_name+' - '+a_module['name'], action=dict(module=a_module['module'], args=args),
                                          delegate_to=delegate_to,
                                          no_log=no_log,
                                          register=task_name + '_out'))
                else:
                    if delegate_to is None or delegate_to == '':
                        tasks.append(dict(name=task_name+' - '+a_module['name'], action=dict(module=a_module['module'], args=args), become=True,
                                          become_method=become_method,
                                          become_user=become_as,
                                          no_log=no_log, register=task_name + '_out'))
                    else:
                        tasks.append(dict(name=task_name+' - '+a_module['name'], action=dict(module=a_module['module'], args=args), become=True,
                                          become_method=become_method,
                                          become_user=become_as,
                                          delegate_to=delegate_to, no_log=no_log,
                                          register=task_name + '_out'))

            print('Constructing Play JSON')
            
            play_json = dict()

            for k, v in a_play.items():
                if k != 'input_fields' and k != 'modules' and k != 'name':
                    play_json[k] = v

            play_json['name']=play_name
            play_json['tasks']=tasks

            print('Intermediate Play JSON : '+str(play_json))

            plays.append(play_json)

        print('Constructing Consolidated Plays YAML')

        data = load(json.dumps(plays, indent=4), Loader=Loader)
        play_yaml = dump(data, Dumper=Dumper)

        print('Constructing Play Book')

        playbook = playbook + "\n" + play_yaml

    except Exception as e:
        print(str(e) + ' : Unexpected error occured.')

    print('Response sent : \n'+str(playbook))

    resp = Response(playbook)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['content-type'] = "text/yaml"

    return resp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
