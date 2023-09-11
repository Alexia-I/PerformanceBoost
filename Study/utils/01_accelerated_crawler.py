from github import Github, RateLimitExceededException
import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from github import Github, RateLimitExceededException
import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import os


class GitHubCrawler:
    def __init__(self, token_pool, fetched_pr_numbers=set()):
        self.token_pool = token_pool
        self.current_token_index = 0
        self.github = Github(self.token_pool[self.current_token_index])
        self.data = []
        self.fetched_pr_numbers = fetched_pr_numbers
        self.lock = Lock()

    def switch_token(self):
        with self.lock:
            self.current_token_index = (self.current_token_index + 1) % len(self.token_pool)
            self.github = Github(self.token_pool[self.current_token_index])

    def fetch_pull_requests(self, repo_name):
        try:
            print(f"Starting to fetch data for repo: {repo_name}")
            repo = self.github.get_repo(repo_name)
            pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')

            for pr in pulls:

                # 跳过已经爬取过的repos
                if pr.number in self.fetched_pr_numbers:
                    continue

                # 初始化关键字检测标志
                keyword_found = False

                # 检查 PR 的 title 和 body 中是否包含关键字 "performance"
                if pr.body is not None:
                    if pr.merged and ("performance" in pr.title.lower() or "performance" in pr.body.lower()):
                        keyword_found = True

                # 检查 code reviews 中是否包含关键字 "performance"
                reviews = []
                for review in pr.get_reviews():
                    review_body = review.body if review.body else "No comment"
                    if "performance" in review_body.lower():
                        keyword_found = True
                    reviews.append({
                        'reviewer': review.user.login if review.user else "Unknown",
                        'state': review.state,
                        'body': review_body
                    })

                # 检查 issue comments 中是否包含关键字 "performance"
                comments = []
                for comment in pr.get_issue_comments():
                    comment_body = comment.body if comment.body else "No comment"
                    if "performance" in comment_body.lower():
                        keyword_found = True
                    comments.append({
                        'commenter': comment.user.login if comment.user else "Unknown",
                        'body': comment_body
                    })

                # 如果在任何部分找到了关键字，则保存 PR 数据
                if keyword_found:
                    print("PAUSE")
                    print(f"Fetching PR number: {pr.number}")

                    # 获取 PR 的 body
                    body = pr.body if pr.body else "None"

                    # 获取改变的文件
                    changed_files = []
                    for pr_file in pr.get_files():
                        patch = pr_file.patch if pr_file.patch else "No changes"
                        changed_files.append({
                            'filename': pr_file.filename,
                            'patch': patch
                        })

                    pr_data = {
                        'repo': repo_name,
                        'pr_number': pr.number,
                        'body': body,
                        'changed_files': changed_files,
                        'reviews': reviews,  # 包含 code reviews
                        'comments': comments  # 包含 issue comments
                    }
                    self.data.append(pr_data)

                    if len(self.data) >= 1:
                        self.save_to_file(f"merged_pull_requests_{repos[0].replace('/','_')}.json")



        except RateLimitExceededException:
            print("Rate limit exceeded. Switching token.")
            self.switch_token()

    def load_fetched_pr_numbers(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                for pr in data:
                    self.fetched_pr_numbers.add(pr['pr_number'])
        except FileNotFoundError:
            print("No existing data found. Starting fresh.")

    def save_to_file(self, filename):
        existing_data = []
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            open(filename, 'w').close()
            pass  # 如果文件不存在，existing_data 将保持为空列表

        existing_data.extend(self.data)  # 添加新数据

        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=4)

        self.data = []  # 清空 self.data


if __name__ == "__main__":
    token_pool = ['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', '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',
                  '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']
    # Repos needed to crawl, one at a time
    repos = ['pandas-dev/pandas']
    crawler = GitHubCrawler(token_pool)

    # Load already fetched PR numbers
    crawler.load_fetched_pr_numbers(f"merged_pull_requests_{repos[0].replace('/','_')}.json")

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(crawler.fetch_pull_requests, repos))

    # 最后扫个尾，如果还剩1-4之间的数据的话，就保存下来
    crawler.save_to_file(f"merged_pull_requests_{repos[0].replace('/','_')}.json")
