from quixstreams import Application
import os
import json
from datetime import datetime

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092")

class GitHubCommitConsumer:
    def __init__(self):
        self.app = Application(
            broker_address=KAFKA_BROKER,
            consumer_group="github-consumer",
            consumer_extra_config={"auto.offset.reset": "earliest"},
        )
        self.topic = self.app.topic(
            name="github-commits",
            value_deserializer="json",
        )
        self.consumer = self.app.get_consumer()
        self.consumer.subscribe([self.topic.name])

        print(f"Connected to Kafka at {KAFKA_BROKER}")
        print(f"Subscribed to topic: {self.topic.name}")

    def run(self):
        print("Listening for commit messages...\n")

        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    print("Consumer error:", msg.error())
                    continue
                
                sha = msg.key().decode("utf-8") if msg.key() else None
                #current 
                commit_bytes = msg.value()
                commit = json.loads(commit_bytes.decode("utf-8"))
                author = commit["commit"]["author"]["name"]
                date_str = commit["commit"]["author"]["date"]
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                
                message = commit["commit"]["message"].split("\n")[0]

                print(f"Commit from {date} with {sha[:7]} by {author}: {message}")

        except KeyboardInterrupt:
            print("\nStopping consumer...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    consumer = GitHubCommitConsumer()
    consumer.run()