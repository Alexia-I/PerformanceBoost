from github import Github, RateLimitExceededException
import json
import time
import requests

class GitHubCrawler:
    def __init__(self, token):
        self.github = Github(token)
        self.data = []

    def fetch_pull_requests(self, repo_name):
        try:
            repo = self.github.get_repo(repo_name)
            pull_requests = repo.get_pulls(state='closed', sort='updated', direction='desc')

            for pr in pull_requests:

                # 初始化关键字检测标志
                keyword_found = False

                # 检查 PR 的 title 和 body 中是否包含关键字 "performance"
                if pr.merged and ("performance" in (pr.title if pr.title else '').lower() or "performance" in (pr.body if pr.body else '').lower()):
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

                    # 获取 PR 的 diff
                    diff_url = pr.diff_url
                    response = requests.get(diff_url)
                    if response.status_code == 200:
                        diff = response.text
                    else:
                        diff = "Could not fetch diff"

                    pr_data = {
                        'repo': repo_name,
                        'pr_number': pr.number,
                        'body': body,
                        'changed_files': changed_files,
                        'diff': diff,
                        'reviews': reviews,  # 包含 code reviews
                        'comments': comments  # 包含 issue comments
                    }
                    self.data.append(pr_data)

        except RateLimitExceededException:
            print("Rate limit exceeded. Sleeping for 60 seconds.")
            time.sleep(60)

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=4)

if __name__ == "__main__":
    token = "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"
    repos = ['keras-team/keras', 'numpy/numpy', 'pandas-dev/pandas']
    crawler = GitHubCrawler(token)

    for repo in repos:
        print(f"Fetching data for repo: {repo}")
        crawler.fetch_pull_requests(repo)

    crawler.save_to_file("merged_pull_requests.json")
