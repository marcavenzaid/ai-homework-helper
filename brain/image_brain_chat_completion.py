import logging
from brain.brain import BrainConfig
import xml.etree.ElementTree as ET
import base64
# https://stackoverflow.com/a/69374234 (VSCode is not completely sure that it's a python. So, you have to explicitly clarify the library)
import pip._vendor.requests as requests
from werkzeug.utils import secure_filename
import os
import definitions

logger = logging.getLogger(__name__)

class ImageBrainChatCompletion:

    def __init__(self, client, brain_config: BrainConfig):
        self._client = client
        self._brain_config = brain_config
        self._image_brain_openai_chat_completion_tree = self._brain_config.get_image_brain_openai_chat_completion_tree()

        try:
            self._model = self._image_brain_openai_chat_completion_tree.find("model").text
            self._system_message = self._image_brain_openai_chat_completion_tree.find("messages")[0].find("content").text
            self._temperature = float(self._image_brain_openai_chat_completion_tree.find("temperature").text)
            self._max_tokens = int(self._image_brain_openai_chat_completion_tree.find("max_tokens").text)
            self._top_p = float(self._image_brain_openai_chat_completion_tree.find("top_p").text)
            self._frequency_penalty = float(self._image_brain_openai_chat_completion_tree.find("frequency_penalty").text)
            self._presence_penalty = float(self._image_brain_openai_chat_completion_tree.find("presence_penalty").text)
        except ET.ParseError:
            logger.debug("Error while parsing XML.")
        except ValueError as e:
            logger.debug(f"Value error: {e}")
        except AttributeError as e:
            logger.debug(f"Attribute error: {e}")
        except Exception as e:
            logger.debug(f"Unexpected error: {e}")


    def think_base64(self, message, image_files):
        logger.info(f"Brain is thinking..")

        try:
            chat_completion = self._gpt_chat_completion_base64(message, image_files)
        except Exception as e:
            raise e
        
        logger.info(f"chat_completion: {chat_completion}")

        return chat_completion
    

    def think(self, message, image_url):
        logger.info(f"Brain is thinking..")

        try:
            chat_completion = self._gpt_chat_completion(message, image_url)
        except Exception as e:
            raise e
        
        logger.info(f"chat_completion: {chat_completion}")

        return chat_completion
    

    def _gpt_chat_completion_base64(self, message, image_files):
        """
        Use this when you want to pass a local image.
        """

        base64_images = []
        for image_file in image_files:
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(definitions.IMAGES_INPUT_OUTPUT_PATH, filename)
            image_file.save(file_path)
            base64_image = self._encode_image_base64(file_path) # Encode into base64 string
            base64_images.append(base64_image)
            

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._client.api_key}"
        }

        content = [
            {
                "type": "text",
                "text": message
            }
        ]
        # Dynamically add images to the content list
        for base64_image in base64_images:
            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
            content.append(image_content)

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "top_p": self._top_p,
            "frequency_penalty": self._frequency_penalty,
            "presence_penalty": self._presence_penalty
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        except Exception as e:
            raise e

        return response.json()
    

    def _gpt_chat_completion(self, message, image_url):
        try:
            chat_completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": message
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                },
                            },
                        ],
                    }
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                top_p=self._top_p,
                frequency_penalty=self._frequency_penalty,
                presence_penalty=self._presence_penalty
            )
        except Exception as e:
            raise e

        return chat_completion
    

    # Function to encode the image
    def _encode_image_base64(self, image_url):
        with open(image_url, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


    def get_model(self):
        return self._model
    

    def get_system_message(self):
        return self._system_message