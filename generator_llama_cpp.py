from llama_cpp import Llama
import os
import json

n_ctx=4096
seed=0
n_gpu_layers=32

telegram_llm_model_path_file = "model_path.txt"

with open(telegram_llm_model_path_file, "r") as model_path_file:
    data = model_path_file.read().rstrip()
    llm_generator: Llama = Llama(model_path=data, n_ctx=n_ctx, seed=seed, n_gpu_layers=n_gpu_layers)


    def get_answer(
            prompt,
            eos_token,
            stopping_strings,
            turn_template='',
            **kwargs):
        # Preparing, add stopping_strings

        answer = llm_generator.create_completion(
            prompt=prompt,
            max_tokens=0,
        )
        try:
            answer = answer["choices"][0]["text"].replace(prompt, "")
            for event in answer:
                event_text = json.loads(json.dumps(event))["choices"][0]["text"]
                print(event_text, end='', flush=True)
        except Exception as exception:
            print("generator_wrapper get answer error ", exception)
        return answer


    def tokens_count(text: str):
        return len(llm_generator.tokenize(text.encode(encoding="utf-8", errors="strict")))


def get_model_list():
    bins = []
    for i in os.listdir("models"):
        if i.endswith(".bin"):
            bins.append(i)
    return bins



