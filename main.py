from flask import Flask, request, Response, jsonify, make_response, Blueprint
from yaml import load, dump
import json
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)


try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


REQUEST_API = Blueprint('api', __name__)

def get_blueprint():
    """Return the blueprint for the main app module"""
    return REQUEST_API


### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "ansible-playbook-json2yaml"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


app.register_blueprint(get_blueprint())


@app.errorhandler(400)
def handle_400_error(_error):
    """Return a http 400 error to client"""
    return make_response(jsonify({'error': 'Misunderstood'}), 400)


@app.errorhandler(401)
def handle_401_error(_error):
    """Return a http 401 error to client"""
    return make_response(jsonify({'error': 'Unauthorised'}), 401)


@app.errorhandler(404)
def handle_404_error(_error):
    """Return a http 404 error to client"""
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def handle_500_error(_error):
    """Return a http 500 error to client"""
    return make_response(jsonify({'error': 'Server error'}), 500)

@app.route('/generate-yaml', methods=['POST'])
def playbook_yaml_generator():
    playbook = '---'
    try:
        plays = []
        request_json = request.get_json()
        print('Request received : \n'+str(request_json))
        print('Total plays found : '+str(len(request_json)))

        play_counter = 1

        for a_play in request_json:

            play_name = a_play['name']

            print('Starting preparation of : Play_'+str(play_counter))

            play_counter = play_counter + 1

            tasks = []

            task_counter = 1

            for a_module in a_play['modules']:

                print('Starting preparation of : Task_' + str(task_counter))

                free_form_found = False

                args = ''
                for k, v in a_module['input_fields'].items():

                    if k == 'free_form':
                        free_form_found = True

                    if args == '' and v != '' and v is not None and v != 'null':
                        args = args + k + '="' + v + '"'
                    elif v != '' and v is not None and v != 'null':
                        args = args + ' ' + k + '="' + v + '"'

                task = dict()
                become_as = ''
                become_method = 'su'
                delegate_to = ''
                no_log = False
                register_out = ''
                when_condition = ''
                with_items = ''

                try:
                    when_condition = a_module['when']
                    task['when'] = when_condition
                except Exception as e:
                    print(str(e) + ' not found in task definition')

                try:
                    with_items = a_module['with_items']
                    task['with_items'] = with_items
                except Exception as e:
                    print(str(e) + ' not found in task definition')

                try:
                    become_as = a_module['become']
                    task['become'] = become_as
                    try:
                        become_method = a_module['become_method']
                        task['become_method'] = become_method
                    except Exception as e:
                        print(str(e) + ' not found in task definition')
                except Exception as e:
                    print(str(e) + ' not found in task definition')

                try:
                    delegate_to = a_module['delegate_to']
                    task['delegate_to'] = delegate_to
                except Exception as e:
                    print(str(e) + ' not found in task definition')

                try:
                    no_log = a_module['no_log']
                    task['no_log'] = no_log
                except Exception as e:
                    print(str(e) + ' not found in task definition')
                    
                try:
                    register_out = a_module['register']
                    task['register'] = register_out
                except Exception as e:
                    print(str(e) + ' not found in task definition')

                task_counter = task_counter + 1

                if free_form_found:
                    module_name = a_module['module']
                    task[module_name] = a_module['input_fields']['free_form']
                else:
                    task['action'] = dict(module=a_module['module'], args=args)
                task['name'] = a_module['name']

                tasks.append(task)

            print('Constructing Play JSON')

            play_json = dict()

            for k, v in a_play.items():
                if k != 'input_fields' and k != 'modules' and k != 'name':
                    play_json[k] = v

            play_json['name']=play_name
            play_json['tasks']=tasks

            print('Intermediate Play JSON : '+str(play_json))

            plays.append(play_json)

        print('Constructing Consolidated Plays YAML from : ' + json.dumps(plays, indent=4))

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
    app.run(host="0.0.0.0", port=2020, debug=True)
