import concurrent.futures
import json
import logging
import time
import xml.etree.ElementTree as ET
import definitions
import re

logger = logging.getLogger(__name__)


def stylize_codes_for_html(str):
    # Format the code block
    stylized_str = (
        definitions.STYLIZE_CODE_HTML_ELEM_OPENING_TAG
        + str
        + definitions.STYLIZE_CODE_HTML_ELEM_CLOSING_TAG
    )
    return stylized_str


def find_codes_then_stylize_for_html(output_str):
    start_pos = 0
    stylized_string = ""
    found_backtick = True

    # Find and format all occurrences of "```", then stylize it.
    while found_backtick:
        # Find the position of the next occurrence of "```"
        backtick_pos = output_str.find("```", start_pos)

        if backtick_pos == -1:
            # No more occurrences found, set the flag to False
            found_backtick = False
            stylized_string += output_str[start_pos:]
            break

        # Find the position of the next closing "```"
        closing_backtick_pos = output_str.find("```", backtick_pos + 3)

        if closing_backtick_pos == -1:
            # No closing backtick found, set the flag to False
            found_backtick = False
            stylized_string += output_str[start_pos:]
            break

        closing_backtick_end_pos = closing_backtick_pos + 3

        # Format the code block
        stylized_string += (
            output_str[start_pos:backtick_pos]
            + definitions.STYLIZE_CODE_HTML_ELEM_OPENING_TAG
            + output_str[backtick_pos:closing_backtick_end_pos]
            + definitions.STYLIZE_CODE_HTML_ELEM_CLOSING_TAG
        )

        # Update start_pos for the next iteration
        start_pos = closing_backtick_end_pos

    return stylized_string


def fix_windows_newline(input_str):
    """ 
    Replace '\r\n' with '\n'.
    https://stackoverflow.com/questions/15433188/what-is-the-difference-between-r-n-r-and-n
    https://stackoverflow.com/questions/66277932/why-does-python-file-write-unexpectedly-add-a-newline-to-every-line
    """
    # Replace "\r\n" with "\n", then replace "\r" with "\n".
    return input_str.replace("\r\n", "\n")


def string_to_html_paragraphs(str):
    # Split the str into paragraphs on the newlines.
    paragraphs = str.strip().split("\n")

    # Convert each paragraph to an HTML paragraph
    html_paragraphs = []  # An empty list to store the HTML paragraphs
    for p in paragraphs:
        # If the paragraph is not an empty string, create an HTML paragraph element. 
        # Else if empty, create an empty HTML paragraph, this serves as a newline when coupled with:
        # p:empty:before { content: " "; white-space: pre; }
        # in the css.
        # Reference: https://stackoverflow.com/questions/12378288/html-empty-p-p-tag-show-no-line-break
        if p:
            html_p = f"<p>{p}</p>"
            html_paragraphs.append(html_p)
        else:
            html_p = "<p></p>"
            html_paragraphs.append(html_p)
            

    joined_html_paragraphs = "".join(html_paragraphs)

    return joined_html_paragraphs


# def replace_double_backslash_to_single(input_string):
#     # Replace double backslashes with a single backslash
#     modified_string = input_string.replace("\\\\", "\\")
#     return modified_string


def read_xml_file_root_element_tree(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except Exception as e:
        logger.exception(f"An error occurred while reading the xml file: {e}")
        raise e


def read_file_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError as e:
        logger.exception(f"File '{file_path}' not found.")
        raise e
    except json.JSONDecodeError as e:
        logger.exception(f"Invalid JSON format in file '{file_path}'.")
        raise e
    except Exception as e:
        logger.exception(f"An error occurred while reading the json file: {e}")
        raise e


def update_file_json(file_path, key, new_value):
    logger.info(f"Updating JSON file: '{file_path}'..")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Update the value for the given key
        data[key] = new_value
        
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        
        logger.info(f"JSON file updated successfully in '{file_path}'.")
    except FileNotFoundError as e:
        logger.exception(f"File '{file_path}' not found.")
        raise e
    except json.JSONDecodeError as e:
        logger.exception(f"Invalid JSON format in file '{file_path}'.")
        raise e
    except Exception as e:
        logger.exception(f"An error occurred while updating the json file: {e}")
        raise e
    
    
class ExecutionTimeMeasurer():

    def start(self):
        self._start_time = time.time()


    def get_elapsed_time(self):
        self._end_time = time.time()
        self._elapsed_time = self._end_time - self._start_time
        return self._elapsed_time
    