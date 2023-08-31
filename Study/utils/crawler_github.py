from github import Github, RateLimitExceededException
import json
import time
from threading import Thread
import os

class GitHubCrawler:
    def __init__(self, token_pool):
        self.token_pool = token_pool
        self.current_token_index = 0
        self.reviews_data = []
        self.batch_size = 10
        self.batch_count = 1

    def switch_token(self):
        self.current_token_index = (self.current_token_index + 1) % len(self.token_pool)


    def fetch_pull_requests(self, repo_name, checkindex):
        try:
            g = Github(self.token_pool[self.current_token_index])
            repo = g.get_repo(repo_name)
            
            #选取closed，merged，含有keywords（performance）的pr
            pull_requests = repo.get_pulls(state='closed', sort='updated', direction='desc') 

            # 插入None检查
            pull_requests = [pr for pr in pull_requests 
                 if (pr.title if pr.title else '') or 
                    (pr.body if pr.body else '')]

            pull_requests = [pr for pr in pull_requests if pr.merged_at is not None and ('performance' in pr.title.lower() or 'performance' in pr.body.lower())]
            
            for pr in pull_requests:
  

                print(f"Fetching PR number: {pr.number}")

                # 获取comments
                comments = pr.get_review_comments()
                    
                # 获取diff
                diff = pr.get_diff()
                    
                result = {
                    'repo': repo_name,
                    'pr_number': pr.number,
                    'title': pr.title,
                    'comments': [c.body for c in comments], 
                    'diff': diff
                }
                    
                self.reviews_data.append(result)
                print(len(self.reviews_data))

                if len(self.reviews_data) >= self.batch_size:
                    self.save_to_file(f'../data/collected_data/github_prs_{self.batch_count+checkindex}.json')
                    self.reviews_data = []
                    self.batch_count += 1

        except RateLimitExceededException:
            print("Rate limit exceeded. Switching token and sleeping.")
            self.switch_token()
            time.sleep(60) 

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.reviews_data, f, indent=4)

    # 断点续传
    # input: dir_path, file stored path
    # output: last review metadata

    def checkpoint(self, dir_path):
        max_x=1
        for filename in os.listdir(dir_path):
            print(filename)
            if filename.startswith("github_prs_"):
                x = int(filename.split('_')[-1].split('.')[0])
                print(f"x:{x}")
                max_x = max(max_x, x)
        last_file = f"github_prs_{max_x}.json"

        with open(os.path.join(dir_path, last_file), 'r') as f:
            data = json.load(f)

        return data[-1] if data else None, max_x


