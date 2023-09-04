import json

# 读取JSON文件
with open('../data/collected_data/github_crawled_prs/merged_pull_requests_numpy_without_comments.json', 'r') as f:
    data = json.load(f)

# 删除所有的'reviews'元素
for item in data:
    if 'reviews' in item:
        del item['reviews']

# 写回JSON文件
with open('../data/collected_data/github_crawled_prs/merged_pull_requests_numpy_without_comments.json', 'w') as f:
    json.dump(data, f, indent=4)
