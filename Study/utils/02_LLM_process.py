import openai
import re
import os
import time
import json

openai.api_key = "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"

def categorize_issue(pr):
    print(f"###{pr['pr_number']}###")

    # Prompt construction
    # 1
    messages = [
        {"role": "system",
         "content": "You are a professional senior programmer in data science and deep learning and familiar with Github and pull requests."},
        {"role": "user",
         "content": f"Given the following pull request description, read it and check each performance boost point in it, and anaylze each point with the following three perspectives : \
                               (1) identify the optimization target(<specific>, <general>).(2) identify the optimization method used(<specific>, <general>).(3) identify the optimization effect(<specific>, <general>).  \n \
                               The content of the pull request:{pr} \n \
                               Your answer's output format should be strictly in this format: \n \
                                        \n \
                                      ```\n \
                                      pr_id: {pr['pr_number']} \n \
                                      index_performance_boost_point: \n \
                                      Optimization target: <specific tgt in this pr>, <an example for this target>, <general tgt>\n \
                                      Optimization method: <specific method in this pr>, <an example for this method>, <general method>\n \
                                      Optimization effect: <specific effect in this pr>, <general effect>\n \
                                      Generalizibility(Could this optimization method be used in other similar repo for similar target): <yes or no>, <an example for generalization>  \n \
                                      ```\n \ "},
    ]

    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-4",
        messages=messages,
        max_tokens=1000
    )

    return response.choices[0].message['content']


def checkpoint(checkpoint_file):
    if not os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'w') as f:
            # 写入文件内容
            f.write('This is a tmd checkpoint file. \n.')



if __name__ == "__main__":
    # Define the file where data are stored
    file_path = "./merged_pull_requests.json"

    # read the file

    with open(file_path, 'r') as f:
        read_data = json.load(f)

    # Define the checkpoint file path
    checkpoint_file = "../data/collected_data/LLM_preprocess_result/checkpoint.md"
    checkpoint(checkpoint_file)

    # Define the record file
    rcdfile_path = "../data/collected_data/LLM_preprocess_result/LLM_preprocessd_01_gpt-4-32k.txt"

    counter = 0
    start_time = time.time()

    # Loop through all the issue files in the directory and categorize each one

    for pr in read_data:

        result_each = categorize_issue(pr)

        # 对每个pr处理完直接写入
        if not os.path.exists(rcdfile_path):
            with open(rcdfile_path, 'w') as f:
                f.write("\n\n" + pr['repo'] + '_' + str(pr['pr_number']) + result_each + "\n")
        else:
            with open(rcdfile_path, 'a', encoding='utf-8') as file:
                file.write("\n\n" + pr['repo'] + '_' +str(pr['pr_number']) + result_each + "\n")
        # print(filename + ": " + category)

        # time sleep to ensure the limit is not interrputed
        counter += 1
        if counter % 3 == 0:
            elapsed_time = time.time() - start_time
            if elapsed_time < 60:
                time.sleep(60 - elapsed_time)
            start_time = time.time()
