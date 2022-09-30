from rasa.model_training import train_nlu

import yaml

with open('./rasa/nlu.yml','r') as yml_file:
    print(yaml.safe_load(yml_file))

#print(train_nlu(config='./rasa/config.yml',nlu_data='./rasa/nlu.yml',output='./',fixed_model_name='nlp'))

