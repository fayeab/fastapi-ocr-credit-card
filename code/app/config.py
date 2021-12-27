import os
import yaml
config = {'path_file_password': 'passwords.json',
          'default_username': os.environ['USERNAME'], 
          'default_password': os.environ['PWD']}

with open("config_logging.yaml") as file:
    config_logging = yaml.load(file, Loader=yaml.FullLoader)