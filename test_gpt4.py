import LLMApi

conversation_history = []


def chat_with_gpt(user_input):
    # 将用户输入添加到对话历史
    conversation_history.append({"role": "user", "content": user_input})

    # 调用 OpenAI API 生成回复
    response = LLMApi.GPT_request(user_input, 'gpt-4o-mini', test_prompt=conversation_history)

    # 获取 GPT 的回复
    gpt_reply = response

    # 将 GPT 的回复添加到对话历史
    conversation_history.append({"role": "assistant", "content": gpt_reply})

    return gpt_reply


# 示例对话
# user_input="""
# 写一个python 的示例,代码用来支持 gpt4-o 模型阅读 pdf格式 论文 并进行总结
#     """
user_input="""if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    config = init(args)
    # TODO checkpoint 保存目录弄到远程路径，如：S3
    checkpoint_config = air.CheckpointConfig(
        checkpoint_frequency=args.checkpoint,   
        checkpoint_at_end=True
    )
    tuner = tune.Tuner(
        PajAlgorithm,
        run_config=train.RunConfig(
            # stop={"env_runners/episode_return_mean": 150},
            checkpoint_config=checkpoint_config,
        ),
        param_space=config,
        # raise_on_failed_trial=True
    )
    tuner.fit()
    解释代码
"""
while True:
    if user_input.lower() in ['exit', 'quit']:
        break
    gpt_reply = chat_with_gpt(user_input)
    print(f"GPT: {gpt_reply}")
    user_input = input("You: ")


