from brain.brain import Brain
import os
import logging
import definitions
import pickle
import json
import re
import utilities.utilities as utilities
from werkzeug.utils import secure_filename
import base64
import copy

logger = logging.getLogger(__name__)

class Processor():

    def __init__(self):
        self._brain: Brain = Brain()


    def get_brain(self):
        return self._brain


    def process_thinking(self, input_message, input_images):

        # Check how many images are passed.
        valid_images = []
        for image in input_images:
            if image.filename and image.content_type.startswith('image/'):
                valid_images.append(image)
        print("len(valid_images):", len(valid_images))
        has_images = False
        if len(valid_images) > 0:
            has_images = True

        # Save the input in the output folder.
        with open(definitions.INPUT_OUTPUT_PATH, "w", encoding="utf-8") as file:
            input_message = utilities.fix_windows_newline(input_message)
            file.write(input_message)

        base64_images = []
        if has_images:
            base64_images = self.process_image_base64(input_images)

        try:
            # Think, then save response to output folder.
            chat_completion, assistant_messages, assistant_run_steps, merged_output_chat_completion = self._brain.get_chat_completion_and_assistant().think(input_message, base64_images)
        except Exception as e:
            raise e

        # Save chat_completion output.
        with open(definitions.CHAT_COMPLETION_OUTPUT_PKL_PATH, "wb") as file:
            pickle.dump(chat_completion, file)

        # Save chat_completion message output.
        if has_images:
            chat_completion_message = chat_completion["choices"][0]["message"]["content"]
        else:
            chat_completion_message = chat_completion.choices[0].message.content
        with open(definitions.CHAT_COMPLETION_MESSAGE_OUTPUT_PATH, "w", encoding="utf-8") as file:
            file.write(chat_completion_message)

        assistant_messages_data = assistant_messages.data

        # Save assistant message data.
        with open(definitions.ASSISTANT_MESSAGES_OUTPUT_PKL_PATH, "wb") as file:
            pickle.dump(assistant_messages_data, file)

        # Save assistant run steps data.
        assistant_run_steps_data = assistant_run_steps.data
        with open(definitions.ASSISTANT_RUN_STEPS_OUTPUT_PKL_PATH, "wb") as file:
            pickle.dump(assistant_run_steps_data, file)

        # Save merged chat completion output.
        with open(definitions.MERGED_OUTPUT_CHAT_COMPLETION, "wb") as file:
            pickle.dump(merged_output_chat_completion, file)


    def process_image_base64(self, input_images):

        def encode_image_base64(image_url):
            with open(image_url, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        
        # Save the input images.
        base64_images = []
        for image_file in input_images:
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(definitions.IMAGES_INPUT_OUTPUT_PATH, filename)
            image_file.save(file_path)
            base64_image = encode_image_base64(file_path) # Encode into base64 string
            base64_images.append(base64_image)  

        return base64_images


    def read_saved_outputs(self):
        input_message = None
        openai_chat_completion_obj = None
        openai_assistant_messages_data_obj = None
        openai_assistant_run_steps_data_obj = None
        merged_output_chat_completion = None

        try:
            # Read the last saved input.
            if os.path.exists(definitions.INPUT_OUTPUT_PATH):
                with open(definitions.INPUT_OUTPUT_PATH, "r", encoding="utf-8") as file:
                    input_message = file.read()

            # Read the last saved openai_chat_completion pkl output.
            if os.path.exists(definitions.CHAT_COMPLETION_OUTPUT_PKL_PATH):
                with open(definitions.CHAT_COMPLETION_OUTPUT_PKL_PATH, "rb") as file:
                    openai_chat_completion_obj = pickle.load(file)

            # Read the last saved openai assistant message output.
            if os.path.exists(definitions.ASSISTANT_MESSAGES_OUTPUT_PKL_PATH):
                with open(definitions.ASSISTANT_MESSAGES_OUTPUT_PKL_PATH, "rb") as file:
                    openai_assistant_messages_data_obj = pickle.load(file)

            # Read the last saved openai assistant run steps output.
            if os.path.exists(definitions.ASSISTANT_RUN_STEPS_OUTPUT_PKL_PATH):
                with open(definitions.ASSISTANT_RUN_STEPS_OUTPUT_PKL_PATH, "rb") as file:
                    openai_assistant_run_steps_data_obj = pickle.load(file)

            # Read the last saved openai_chat_completion pkl output.
            if os.path.exists(definitions.MERGED_OUTPUT_CHAT_COMPLETION):
                with open(definitions.MERGED_OUTPUT_CHAT_COMPLETION, "rb") as file:
                    merged_output_chat_completion = pickle.load(file)

        except Exception as e:
            raise e
        
        return input_message, openai_chat_completion_obj, openai_assistant_messages_data_obj, openai_assistant_run_steps_data_obj, merged_output_chat_completion


    def format_outputs_for_html(self, input_message, merged_output_chat_completion):
        if input_message is not None:
            logger.debug(f"Last saved input_message: {input_message}")
            input_message = utilities.string_to_html_paragraphs(input_message) # Format the input for HTML display.

        if merged_output_chat_completion is not None:
            logger.debug(f"Last saved chat_completion_message: {merged_output_chat_completion.choices[0].message.content}")

            # Format the brain outputs for HTML display.
            # merged_output_chat_completion.choices[0].message.content = utilities.replace_double_backslash_to_single(merged_output_chat_completion.choices[0].message.content)
            merged_output_chat_completion.choices[0].message.content = self._fix_latex_format(merged_output_chat_completion.choices[0].message.content)
            merged_output_chat_completion.choices[0].message.content = self._change_single_backslash_to_double(merged_output_chat_completion.choices[0].message.content)
            # merged_output_chat_completion.choices[0].message.content = utilities.string_to_html_paragraphs(merged_output_chat_completion.choices[0].message.content)
            # merged_output_chat_completion.choices[0].message.content = utilities.find_codes_then_stylize_for_html(merged_output_chat_completion.choices[0].message.content)
            
        # Here. add attaching image based on the image name placeholder.

        return input_message, merged_output_chat_completion
    

    def _change_single_backslash_to_double(self, str):
        str = str.replace("\\[", "\\\\[")
        str = str.replace("\\]", "\\\\]")

        str = str.replace("\\(", "\\\\(")
        str = str.replace("\\)", "\\\\)")

        return str


    def _fix_latex_format(self, str):
        """ 
        Remove whitespaces (including newlines) between the brackets/parenthesis and the expression. 
        This is to fix broken formated latexes where there are unnecessary whitespaces (including newlines) between 
        the brackets/parenthesis and the expression especially newlines which affects some processes such as 
        converting latex code to latex (in the KaTeX delimiters). 
        """
        latex_in_brackets_matches, latex_in_parentheses_matches = self._get_latexes(str)

        # Remove whitespaces between the brackets and the expression.
        for match in latex_in_brackets_matches:
            whitespace_matches = re.sub(r"(?<=\\\[)\s+(?=\S)|(?<=\S)\s+(?=\\\])", "", match) # Match the whitespaces between the brackets and the expressions.
            str = str.replace(match, whitespace_matches) # Remove the whitespaces.

        # Remove whitespaces between the parentheses and the expression.
        for match in latex_in_parentheses_matches:
            whitespace_matches = re.sub(r"(?<=\\\()\s+(?=\S)|(?<=\S)\s+(?=\\\))", "", match) # Match the whitespaces between the parenthesis and the expressions.
            str = str.replace(match, whitespace_matches) # Remove the whitespaces.

        str = self._concatenate_latex_equations(str)

        return str
    

    # Change the newlines into "inline concatenation", to avoid where markdown-it separates a multi-line equation into 2 paragraphs,
    # therefore the mathjax cannot render it properly.
    def _concatenate_latex_equations(self, text):
        # Patterns for detecting LaTeX block and inline equations
        block_pattern = re.compile(r'\\\[([\s\S]*?)\\\]', re.MULTILINE)
        inline_pattern = re.compile(r'\\\(([\s\S]*?)\\\)', re.MULTILINE)
        
        def transform_to_single_line(match):
            equation = match.group(1)
            # Remove newlines and excessive spaces, while preserving meaningful spaces
            single_line_equation = " ".join(equation.split())
            return single_line_equation
        
        # Replace multi-line block equations with single-line versions
        text = block_pattern.sub(lambda match: '\\[' + transform_to_single_line(match) + '\\]', text)
        
        # Replace multi-line inline equations with single-line versions
        text = inline_pattern.sub(lambda match: '\\(' + transform_to_single_line(match) + '\\)', text)
        
        return text


    def _get_latexes(self, str):
        """ 
        Get all latexes encapsulated in single backslash + brackets or parentheses ( "\\\[ x \\\]" or "\\\( x \\\)" ) from a given string.
        """

        # Find all expressions encapsulated by "\[" and "\]".
        latex_in_brackets_matches = re.findall(r'(\\\[.*?\\\])', str, re.DOTALL)

        # Find all expressions encapsulated by "\(" and "\)".
        latex_in_parentheses_matches = re.findall(r'(\\\(.*?\\\))', str, re.DOTALL)

        return latex_in_brackets_matches, latex_in_parentheses_matches
    

    def extract_answer_step_by_step_solution(self, merged_output_chat_completion_message):
        # Define a regex pattern to match and capture the parts
        pattern = r'\[Answer\](.*?)\[Step-by-step solution\](.*)'
        
        # Use re.search to find the pattern in the input string
        match = re.search(pattern, merged_output_chat_completion_message, re.DOTALL)
        
        if match:
            answer = match.group(1).strip()
            step_by_step_solution = match.group(2).strip()
            logger.debug(f"answer: {answer}")
            logger.debug(f"step_by_step_solution: {step_by_step_solution}")
            return answer, step_by_step_solution
        else:
            return None, None

    