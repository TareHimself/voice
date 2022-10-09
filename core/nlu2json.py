import re
import json
def nlu2dict(file_stream):
	lines = file_stream.readlines()
	result = {
		"nlu" : []
	}

	while len(lines) > 0:
		line = lines.pop(0)
		match = re.match(r"(?:-)?(?:\s+)?([a-zA-Z0-9 ]+|)(?:\s+)?:(?:\s+)?([a-zA-Z\d_\".| ]+)?(?:\s+)?$",line)
		if match:
			key, value = match.groups()
			if key.lower() == 'version':
				result[key] = value[1:][:-1]
			elif key.lower() == 'intent' or key.lower() == 'regex':
				intent = {key : value}
				examples = []
				lines.pop(0)
				example_line = lines.pop(0)
				while example_line and len(example_line.strip()) > 0:
					examples.append(example_line.strip()[1:].strip())
					example_line = lines.pop(0)
				intent['examples'] = examples
				result['nlu'].append(intent)
	return result

def dict2nlu(json_dict):
	result = ""
	data = json_dict
	result = result + "{}: \"{}\"\n\n{}:\n".format('version',data['version'],'nlu')

	for item in json_dict['nlu']:
		l_keys = list(item.keys())
		result = result + "- {}: {}\n  examples: |\n".format(l_keys[0],item[l_keys[0]])
		for examp in item['examples']:
			result = result + "    - {}\n".format(examp)
		result = result + '\n'
	
	return result
