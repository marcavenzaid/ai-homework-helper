""" 
The purpose of definitions.py is to be able to define paths starting from project root (ROOT_DIR).
This file should be located in the top-level of the project.
Reference: https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure
"""

import os
import utilities.utilities as utilities

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFINITIONS_JSON_PATH = os.path.join(ROOT_DIR, "definitions.json")

definitions_json = utilities.read_file_json(DEFINITIONS_JSON_PATH)

# Replace ${ROOT_DIR} with the actual value of ROOT_DIR.
for key, value in definitions_json.items():
    if isinstance(value, str) and "${ROOT_DIR}" in value:
        value = value.replace("${ROOT_DIR}", ROOT_DIR)
        definitions_json[key] = value

CONFIG_PATH = definitions_json["CONFIG_PATH"]

BRAIN_CONFIG_PATH = definitions_json["BRAIN_CONFIG_PATH"]

INPUT_OUTPUT_PATH = definitions_json["INPUT_OUTPUT_PATH"]
CHAT_COMPLETION_OUTPUT_PKL_PATH = definitions_json["CHAT_COMPLETION_OUTPUT_PKL_PATH"]
CHAT_COMPLETION_MESSAGE_OUTPUT_PATH = definitions_json["CHAT_COMPLETION_MESSAGE_OUTPUT_PATH"]
ASSISTANT_MESSAGES_OUTPUT_PKL_PATH = definitions_json["ASSISTANT_MESSAGES_OUTPUT_PKL_PATH"]
ASSISTANT_RUN_STEPS_OUTPUT_PKL_PATH = definitions_json["ASSISTANT_RUN_STEPS_OUTPUT_PKL_PATH"]
ASSISTANT_MESSAGES_IMAGE_OUTPUT_DIR = definitions_json["ASSISTANT_MESSAGES_IMAGE_OUTPUT_DIR"]
MERGED_OUTPUT_CHAT_COMPLETION = definitions_json["MERGED_OUTPUT_CHAT_COMPLETION"]

IMAGES_INPUT_OUTPUT_PATH = definitions_json["IMAGES_INPUT_OUTPUT_PATH"]
IMAGES_OUTPUT_OUTPUT_PATH = definitions_json["IMAGES_OUTPUT_OUTPUT_PATH"]
AUDIO_PATH = definitions_json["AUDIO_PATH"]

# PREV_RESULT_BRAIN_USED_OUTPUT_PATH = definitions_json["PREV_RESULT_BRAIN_USED_OUTPUT_PATH"]
# PREV_RESULT_HAS_IMAGES_OUTPUT_PATH = definitions_json["PREV_RESULT_HAS_IMAGES_OUTPUT_PATH"]

LOG_OUTPUT_PATH = definitions_json["LOG_OUTPUT_PATH"]

STYLIZE_CODE_HTML_ELEM_OPENING_TAG = "<pre class='border bg-body-secondary'>"
STYLIZE_CODE_HTML_ELEM_CLOSING_TAG = "</pre>"