from quixstreams import Application
import os
import json
import duckdb
from datetime import datetime

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092")
# local duckdb 
DB_PATH = "commits.duckdb"
# batching to help w/ speed
BATCH_SIZE = 100  

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

        # Connect to DuckDB
        self._init_db()

        # Batch buffer
        self.buffer = []
        print(f"Connected to Kafka at {KAFKA_BROKER}")
        print(f"Subscribed to topic: {self.topic.name}")
        print("Using DuckDB at:", DB_PATH)


    def _init_db(self):
        #creates table and closes conn immediately to release lock
        conn = duckdb.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS commits (
                date TIMESTAMP,
                sha TEXT,
                author TEXT,
                message TEXT
            )
        """)
        conn.close()

    def _flush_batch(self):
        if not self.buffer:
            return
        
        print(f"Writing batch of {len(self.buffer)} commits to DuckDB...")

        try:
            conn = duckdb.connect(DB_PATH)
            conn.executemany("""
                INSERT INTO commits (date, sha, author, message)
                VALUES (?, ?, ?, ?)
            """, self.buffer)

            conn.close()
            self.buffer.clear()
        except Exception as e:
            print("Error writing to DuckDB:", e)


    def run(self):
        print("Listening for commit messages...\n")

        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    if len(self.buffer) > 0:
                        self._flush_batch()
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

                self.buffer.append((date, sha, author, message))
                if len(self.buffer) >= BATCH_SIZE:
                    self._flush_batch()
                    self.consumer.store_offsets(msg)

        except KeyboardInterrupt:
            print("\nStopping consumer...")
        finally:
            self._flush_batch()
            self.consumer.close()

if __name__ == "__main__":
    consumer = GitHubCommitConsumer()
    consumer.run()