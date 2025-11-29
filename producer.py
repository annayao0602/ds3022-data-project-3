from quixstreams import Application
import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092")
#generated a github token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# edit if we change repos
REPO = "numpy/numpy"  
# max allowed bit github      
COMMITS_PER_PAGE = 100   


# initialize producer app and kafka topic
class GitHubCommitProducer:
    def __init__(self):
        self.app = Application(
            broker_address=KAFKA_BROKER,
            consumer_group="github-producer",
            producer_extra_config={
                "broker.address.family": "v4"
            }
        )
        # set topic name and serializer
        self.topic = self.app.topic(
            name="github-commits",
            value_serializer="json",
        )
        # print verification
        print(f"Connected to Kafka at {KAFKA_BROKER}")
        print(f"Producing to topic: {self.topic.name}")

        self.session = requests.Session()
        # token error handling
        if GITHUB_TOKEN:
            self.session.headers.update({"Authorization": f"Bearer {GITHUB_TOKEN}"})
        else:
            print("Warning: No GITHUB_TOKEN found.")

# fetch commits from github api
    def fetch_commits_page(self, page: int):
        url = f"https://api.github.com/repos/{REPO}/commits"
        params = {"page": page, 
                  "per_page": COMMITS_PER_PAGE}

        r = self.session.get(url, params=params)
        r.raise_for_status()
        return r.json()

#publish commit json to kafka
    def publish_to_kafka(self, commit: dict) -> bool:
        try:
            sha = commit.get("sha", "")
            serialized = self.topic.serialize(key=sha, value=commit)

            with self.app.get_producer() as producer:
                producer.produce(
                    topic=self.topic.name,
                    key=serialized.key,
                    value=serialized.value,
                )
            return True

        except Exception as e:
            print(f"Error producing commit {sha}: {e}")
            return False

# fetch all commits and publish
    def run(self):
        print(f"Fetching commits from GitHub repo: {REPO}")
        print("Press Ctrl+C to stop\n")

        all_commits_buffer = []
        page = 1
        # fetch loop
        try:
            while True:
                commits = self.fetch_commits_page(page)
                if not commits:
                    print("\nNo more commits. Done.")
                    break
                all_commits_buffer.extend(commits)
                page += 1
        except KeyboardInterrupt:
            print("\nStopping producer...")
            return
        # error handling
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            return
        print(f"Fetched {len(all_commits_buffer)} commits. \n")
        print("reversing order...")
        all_commits_buffer.reverse()

        print("Publishing commits to Kafka...")
        # publish loop
        for i, commit in enumerate(all_commits_buffer):
            sha = commit.get("sha")
            commit_info = commit.get("commit", {})
            author = commit_info.get("author", {}).get("name", "unknown")
            date = commit_info.get("author", {}).get("date", "unknown")
            message = commit_info.get("message", "").split("\n")[0]  # first line
            # log every 100 commits
            if i % 100 == 0:
                print(f"[{i+1}/{len(all_commits_buffer)}] {date} | {author}")
            self.publish_to_kafka(commit)

if __name__ == "__main__":
    producer = GitHubCommitProducer()
    producer.run()