import openai
import re
import os
import time
import json

# openai key
# openai.api_key = "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"

# ohmygpt key
openai.api_key = "sk-e5MVYsFp9C859A6010a7T3BlBkFJ90858EB3eF3d48dcB48a"

openai.api_base = "https://aigptx.top/v1"

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
                                      ```  \n \
                                      Example: numpy/numpy_23740There are several performance improvement points in this pull request. I will provide a few examples as follows: \n \
                                        1. Updating the meson version requirement \n \
                                        ``` \n \
                                        pr_id: 23740  \n \
                                        index_performance_boost_point: 1 \n \
                                        Optimization target: Specific build system dependencies, updating Meson version requirement, General build system optimization \n \
                                        Optimization method: Updated the Meson version from '>= 0.64.0' to '>= 1.1.0', Updating dependencies in the build system \n \
                                        Optimization effect: Improved compatibility and possibly utilities with newer version of Meson, Improved efficiency of build process \n \
                                        Generalizibility: Yes, similar updates to build system requirements can be made in other repositories with similar dependencies, like SciPy, TensorFlow \n \
                                        ``` \n \
                                        2. Adding Cython compiler check \n \
                                        ``` \n \
                                        pr_id: 23740 \n \
                                        index_performance_boost_point: 2 \n \
                                        Optimization target: Specific build system steps, checking if Cython version is 0.29.34 or greater, General build error reduction \n \
                                        Optimization method: Added Cython compiler version check, incorporating validation checks in the build process \n \
                                        Optimization effect: Prevents build errors related to compatible Cython version, Generally reduces potential for build errors \n \
                                        Generalizibility: Yes, adding version checks for compilers or dependencies can be done in other repos with similar software dependencies, like scikit-learn, pandas \n \
                                        ``` \n \
                                        \n \ "},
    ]

    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-32k",
        messages=messages,
        max_tokens=1000
    )

    return response.choices[0].message['content']




if __name__ == "__main__":
    # Define the file where data are stored
    file_path = "../data/collected_data/github_crawled_prs/merged_pull_requests_pandas-dev_pandas.json"

    # read the file

    with open(file_path, 'r') as f:
        read_data = json.load(f)


    # Define the record file
    rcdfile_path = "../data/collected_data/LLM_preprocess_result/LLM_preprocessd_pandas_gpt4_32k.txt"

    # 初始化一个空列表来存储pr_id
    pr_ids = []

    # read the rcdfile and check pr read before and store them into a list
    with open(rcdfile_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if "pr_id:" in line:  # 查找包含"pr_id:"的行
                pr_id = line.split(":")[1].strip()  # 提取pr_id的值
                pr_ids.append(int(pr_id))  # 添加到列表
        # 去重
        unique_pr_ids = list(set(pr_ids))



    counter = 0
    start_time = time.time()

    # Loop through all the issue files in the directory and categorize each one

    for pr in read_data:

        if pr['pr_number'] in unique_pr_ids:
            print('YES')
            pass
        else:
            result_each = categorize_issue(pr)

            # 对每个pr处理完直接写入
            if not os.path.exists(rcdfile_path):
                with open(rcdfile_path, 'w') as f:
                    f.write("\n\n" + pr['repo'] + '_' + str(pr['pr_number']) + result_each + "\n")
            else:
                with open(rcdfile_path, 'a', encoding='utf-8') as file:
                    file.write("\n\n" + pr['repo'] + '_' + str(pr['pr_number']) + result_each + "\n")
            # print(filename + ": " + category)

            # time sleep to ensure the limit is not interrputed
            counter += 1
            if counter % 2 == 0:
                elapsed_time = time.time() - start_time
                if elapsed_time < 10:
                    time.sleep(30 - elapsed_time)
                start_time = time.time()



