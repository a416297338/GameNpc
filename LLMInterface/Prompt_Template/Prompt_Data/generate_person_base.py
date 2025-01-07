import LLMApi
import concurrent.futures
import json
import time
max_length = 8000

def split_text(text, max_length, delimiter = '.'):
    chunks = []
    current_chunk = []
    current_length = 0

    for char in text:
        char_length = 1  # 每个字符的长度为1
        current_chunk.append(char)
        current_length += char_length

        if char == delimiter and current_length >= max_length:
            chunks.append(''.join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks

def chat_with_gpt(user_input):
    # 将用户输入添加到对话历史
    # 调用 OpenAI API 生成回复
    response = LLMApi.GPT_request(user_input, 'gpt-4o')
    # 获取 GPT 的回复
    gpt_reply = response
    return gpt_reply

def process_text_chunk(text_chunk, prompt_format):
    input_list = [text_chunk]
    for count, i in enumerate(input_list):
        prompt = prompt_format.replace(f"!<INPUT {count}>!", i)
    for i in range(10):
        re_data = chat_with_gpt(prompt)
        try:
            re_data = json.loads(re_data)
            if isinstance(re_data, list):
                return re_data
        except Exception as e:
            print(re_data)
        time.sleep(5)
        print("re_try: " + str(i) + " times")
    return []

def get_data_from_test_chunk(test_chunk_list, prompt_format):
    person_data_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_text_chunk, text_chunk, prompt_format) for text_chunk in test_chunk_list]
        for future in concurrent.futures.as_completed(futures):
            try:
                re_data = future.result()
                person_data_list += re_data
            except Exception as e:
                print(f"Error processing chunk: {e}")
    return person_data_list

def generate_person_base(text_path, prompt_path, save_path):
    with open(text_path, 'r',encoding='utf-8') as file:
        # 读取文件内容
        text_content = file.read()
    text_content = text_content.replace(" ", "").replace("\n", ".")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_format = f.read()
    test_chunk_list = split_text(text_content, max_length)
    person_data_list = get_data_from_test_chunk(test_chunk_list[:20], prompt_format)

    filename = 'my_list.json'
    person_dict = {}
    for person in person_data_list:
        if person['name'] not in person_dict:
            person_dict[person['name']] = person
        else:
            for msg in ['age', 'occupation', 'religious']:
                if msg in person and person[msg] != None:
                    person_dict[person['name']][msg] = person[msg]
            for msg in ['background', 'belief', 'personality', 'speaking']:
                if msg in person and person[msg] != None:
                    if msg not in person_dict[person['name']]:
                        person_dict[person['name']][msg] = []
                    person_dict[person['name']][msg] += person[msg]


    # 将列表写入JSON文件
    with open(filename, 'w', encoding='utf-8') as f:
        # 确保指定ensure_ascii为False以支持中文字符
        json.dump(person_dict, f, ensure_ascii=False)

def generate_person_memory(text_path, prompt_path, save_path):
    with open(text_path, 'r',encoding='utf-8') as file:
        # 读取文件内容
        text_content = file.read()
    text_content = text_content.replace(" ", "").replace("\n", ".")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_format = f.read()
    test_chunk_list = split_text(text_content, max_length)
    person_memory_list = get_data_from_test_chunk(test_chunk_list[:2], prompt_format)
    filename = 'memory_list.json'
    person_memory_dict = {}
    for person_memory_dict_chunk in person_memory_list:
        for person_name, memory_list in person_memory_dict_chunk:
            if person_name in person_memory_dict:
                person_memory_dict[person_name] += memory_list
            else:
                person_memory_dict[person_name] = memory_list

    # 将列表写入JSON文件
    with open(filename, 'w', encoding='utf-8') as f:
        # 确保指定ensure_ascii为False以支持中文字符
        json.dump(person_dict, f, ensure_ascii=False)

if __name__ == "__main__":
    #generate_person_base(text_path = "test1.txt", prompt_path = "generate_person_base.txt", save_path = "person_data.json")
    generate_person_memory(text_path = "test1.txt", prompt_path = "generate_person_base.txt", save_path = "person_data.json")