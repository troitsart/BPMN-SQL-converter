import xml.etree.ElementTree as ET
import json

def parser_to_json(bpmn_file_path, output_file_path):
    """Парсит BPMN-файл и сохраняет данные в JSON-формате."""

    tree = ET.parse(bpmn_file_path)
    root = tree.getroot()

    data = []

    namespaces = {
        'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'camunda': 'http://camunda.org/schema/1.0/bpmn'
    }

    tasks = root.findall('.//bpmn:task', namespaces) + root.findall('.//bpmn:serviceTask', namespaces)
    participant = root.findall('.//bpmn:participant', namespaces)
    collaboration = root.findall('.//bpmn:collaboration', namespaces)

    operation_name = participant[0].get('name')
    operation_id = collaboration[0].get('id')
    data.append({'operation_name': operation_name, 'collaboration_id': operation_id})

    for task in tasks:
        task_data = {
            'name': task.get('name'),
            'id': task.get('id'),
            'input_parameters': []
        }

        input_parameters = task.findall('.//camunda:inputParameter', namespaces)

        for param in input_parameters:
            param_data = {
                'name': param.get('name'),
                'value': param.text
            }
            task_data['input_parameters'].append(param_data)

        data.append(task_data)

    with open(output_file_path, 'w') as f:
        json.dump(data, f, indent=4)