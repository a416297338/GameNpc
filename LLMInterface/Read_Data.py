import os

def get_file_path(file_name):
    return current_path+'/'+"prompt_template/" + file_name

def list_to_string(list):
    re_str = ""
    for str in list:
        str+="(1) "
        if type(str) == type("string"):
            re_str += str
        else:
            re_str += not str.get_string()
        str+="\n"

current_path = os.path.dirname(__file__)

def generate_prompt(curr_input, prompt_lib_file):
    """
    Takes in the current input (e.g. comment that you want to classifiy) and
    the path to a prompt file. The prompt file contains the raw str prompt that
    will be used, which contains the following substr: !<INPUT>! -- this
    function replaces this substr with the actual curr_input to produce the
    final promopt that will be sent to the GPT3 server.
    ARGS:
      curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                  INPUT, THIS CAN BE A LIST.)
      prompt_lib_file: the path to the promopt file.
    RETURNS:
      a str prompt that will be sent to OpenAI's GPT server.
    """
    if type(curr_input) == type("string"):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]
    file_path = get_file_path(prompt_lib_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        prompt = f.read()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    return prompt.strip()

