
import requests
import json
from http.client import RemoteDisconnected
import time
import random

def GPT_dhai_request(prompt, model_name='gpt-3.5-turbo-1106', test_prompt=None):
    post_url = 'http://42.186.26.19:17802/infer_LLM'
    uid = 'dhai'  # 用户所在项目代号  dhai/unisdk/g78
    poj = 'StanfordAITown'  # 调用LLM的项目 PrimeFixer
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@????', len(prompt))
    req_prompt = [{'role': 'user', 'content': prompt}]
    if test_prompt:
        req_prompt = test_prompt
    param = {
        'uid': uid,
        'project': poj,
        'prompt': req_prompt,
        'model_name': model_name,
       # 'extra_params': {'response_format': {'type': "json_object"}},
    }
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r = requests.post(post_url, json=param)
            res = json.loads(r.content)
            return res['message']
        except requests.exceptions.ConnectionError as e:
            if isinstance(e.args[0].args[1], RemoteDisconnected):
                time.sleep(random.random()*3)
                print(f"Connection aborted. Retrying {attempt + 1}/{max_retries}...")
            else:
                raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
    raise Exception("Max retries exceeded")
    # if r.status_code != 200:
    #     print('status_code: %s. res: %s.' % (r.status_code, res))
    # else:
    #     print('res: %s' % res)

# debug 4o
def GPT_request(prompt, model_name='gpt-3.5-turbo-1106', test_prompt=None):
    """
    Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
    server and returns the response.
    ARGS:
      prompt: a str prompt
      gpt_parameter: a python dictionary with the keys indicating the names of
                     the parameter and the values indicating the parameter
                     values.
    RETURNS:
      a str of GPT-3's response.
    """

    return GPT_dhai_request(prompt, model_name, test_prompt=test_prompt)
    # response = openai.Completion.create(
    #     model=gpt_parameter["engine"],
    #     prompt=prompt,
    #     temperature=gpt_parameter["temperature"],
    #     max_tokens=gpt_parameter["max_tokens"],
    #     top_p=gpt_parameter["top_p"],
    #     frequency_penalty=gpt_parameter["frequency_penalty"],
    #     presence_penalty=gpt_parameter["presence_penalty"],
    #     stream=gpt_parameter["stream"],
    #     stop=gpt_parameter["stop"], )
    # return response.choices[0].text

if __name__ == '__main__':
    a = """

(1) 到公司完成下午的工作任务（13:00 - 17:00）
(2) 在公司整理出差所需文件（17:00 - 18:00）
(3) 在公司安排明天出差的行程和细节（18:00 - 19:00）
(4) 回家与家人共进晚餐（19:30 - 20:30）
(5) 在家放松休息（20:30 - 21:30）
(6) 在家准备明天的行李和个人物品（21:30 - 22:30）
(7) 在家阅读一些轻松的书籍（22:30 - 23:00）
(8) 在家睡觉休息（23:00 - 07:00）
将上面的所有句子
拆分语义,按照以下数据格式分解,:
data.get('str') # 句子内容
data.get('start_time') # 开始时间
data.get('end_time') # 结束时间
data.get('location') # 地点
data.get('subject') # 主语
data.get('verb') # 谓语
data.get('object') # 宾语
data.get('sub_clause') # 从句
data.get('predicate') # 表语

输出示例:
[
{
"str": "进行午餐休息与休息时间",
"start_time": "12:00",
"end_time": "13:00",
"location": null,
"subject": null,
"verb": "进行",
"object": "午餐休息与休息时间",
"sub_clause": null,
"predicate": null
},
{
"str": "准备明天出差所需文件",
"start_time": "13:00",
"end_time": "14:30",
"location": null,
"subject": null,
"verb": "准备",
"object": "明天出差所需文件",
"sub_clause": null,
"predicate": null
},
{
"str": "开会讨论新项目的战略规划",
"start_time": "14:30",
"end_time": "16:00",
"location": null,
"subject": null,
"verb": "开会讨论",
"object": "新项目的战略规划",
"sub_clause": null,
"predicate": null
}
]

输出以 [ 作为开头"""
    b = GPT_request(a)
    print(type(b))
    c = json.loads(b)
    print(c)