def chat_with_gpt(user_input):
    # 将用户输入添加到对话历史
    conversation_history.append({"role": "user", "content": user_input})

    # 调用 OpenAI API 生成回复
    response = LLMApi.GPT_request(user_input, 'gpt-4o', test_prompt=conversation_history)

    # 获取 GPT 的回复
    gpt_reply = response

    # 将 GPT 的回复添加到对话历史
    conversation_history.append({"role": "assistant", "content": gpt_reply})

    return gpt_reply