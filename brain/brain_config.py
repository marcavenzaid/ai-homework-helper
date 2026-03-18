import definitions
import yaml

class BrainConfig:

    def __init__(self):
        self._tutor_brain_to_use = None
        self._tutor_brain = None
        self._full_name = None
        self._name = None

        self._openai_chat_completion_and_assistant = None
        
        self.load_brain_config(definitions.BRAIN_CONFIG_PATH)
        

    def get_tutor_brain_to_use(self):
        return self._tutor_brain_to_use
    

    def get_tutor_brain_full_name(self):
        return self._full_name


    def get_tutor_brain_name(self):
        return self._name


    def get_openai_chat_completion_and_assistant(self):
        return self._openai_chat_completion_and_assistant


    def load_brain_config(self, config_file):
        with open(config_file, 'r') as file:
            config_data = yaml.safe_load(file)
            
            self._tutor_brain_to_use = config_data.get('tutor_brain_to_use')
            self._tutor_brain = config_data.get(self._tutor_brain_to_use)
            self._full_name = self._tutor_brain.get('full_name')
            self._name = self._tutor_brain.get('name')
            self._openai_chat_completion_and_assistant = self._tutor_brain.get('openai_chat_completion_and_assistant')
