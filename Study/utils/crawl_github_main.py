from crawler_github import GitHubCrawler
from threading import Thread
import json
import os

def threaded_fetch(crawler, repo):
    crawler.fetch_reviews(repo)

if __name__ == "__main__":
    token_pool = ['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', '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', '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']
    
    # read repo names
    # with open('/Users/yanghaowen/科研/projects/Code_review/data/original_data/repo_names_from_csv.json','r') as f:
    #     json_data = json.load(f)
    # repos = json_data.get("repo_names",[])

    # directly set repos manually
    repos = ['keras-team/keras', 'numpy/numpy', 'pandas-dev/pandas', 'tensorflow/tensorflow', 'RaRe-Technologies/gensim']
    crawler = GitHubCrawler(token_pool)

    # first-run flag
    first_run = True

    for repo in repos:
        if first_run:
            crawler.fetch_pull_requests(repo, 0)
            first_run = False
        else:
            latest_checkpoint, checkindex = crawler.checkpoint('../data/collected_data')
            if repos.index(repo) < repos.index(latest_checkpoint["repo"]):
                print(repos.index(latest_checkpoint["repo"]))
                pass
            else:
                print(repo)
                crawler.fetch_pull_requests(repo, checkindex)

