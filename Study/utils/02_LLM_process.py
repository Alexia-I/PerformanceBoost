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
        model="gpt-4",
        messages=messages,
        max_tokens=1000
    )

    return response.choices[0].message['content']


if __name__ == "__main__":
    # Define the file where data are stored
    file_path = "./merged_pull_requests.json"

    # read the file

    with open(file_path, 'r') as f:
        read_data = json.load(f)

    # Define the checkpoint file path
    checkpoint_file = "../data/downloaded_issues_need_comments_processing/checkpoint.md"
    if not os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'w') as f:
            # 写入文件内容
            f.write('This is a tmd checkpoint file. \n.')

    counter = 0
    start_time = time.time()

    # Loop through all the issue files in the directory and categorize each one
    for pr in read_data:

            category = categorize_issue(pr)

            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(filename + ": " + category + "\n")
            # print(filename + ": " + category)

            # time sleep to ensure the limit is not interrputed
            counter += 1
            if counter % 3 == 0:
                elapsed_time = time.time() - start_time
                if elapsed_time < 60:
                    time.sleep(60 - elapsed_time)
                start_time = time.time()
