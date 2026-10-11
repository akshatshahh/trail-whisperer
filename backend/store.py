import os, sqlite3, json
from pathlib import Path
from contextlib import contextmanager

class Store:
    """SQLite without optional keys; Atlas when explicitly configured in basecamp."""
    def __init__(self, directory, mode):
        self.path = Path(directory) / 'trail.sqlite3'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.mongo = None
        self.cloud_calls = 0
        if mode == 'basecamp' and os.getenv('MONGODB_URI'):
            from pymongo import MongoClient
            import certifi
            self.mongo = MongoClient(os.environ['MONGODB_URI'], tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000).get_database('trail_whisperer')
            for name in ('sightings', 'species', 'trips'):
                self.cloud_calls += 1
                self.mongo[name].create_index('id', unique=True)
        with self.connection() as db:
            db.execute('CREATE TABLE IF NOT EXISTS records (collection TEXT, id TEXT, body TEXT, PRIMARY KEY(collection,id))')
    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path, timeout=20)
        try:
            with conn:
                yield conn
        finally:
            conn.close()
    def put(self, collection, record):
        if self.mongo is not None:
            self.cloud_calls += 1
            self.mongo[collection].replace_one({'id': record['id']}, record, upsert=True)
        else:
            with self.connection() as db:
                db.execute('INSERT OR REPLACE INTO records VALUES (?,?,?)', (collection,record['id'],json.dumps(record)))
        return record
    def get(self, collection, id):
        if self.mongo is not None:
            self.cloud_calls += 1
            r = self.mongo[collection].find_one({'id': id}, {'_id': 0})
            return r
        with self.connection() as db:
            r = db.execute('SELECT body FROM records WHERE collection=? AND id=?',(collection,id)).fetchone()
        return json.loads(r[0]) if r else None
    def all(self, collection):
        if self.mongo is not None:
            self.cloud_calls += 1
            return list(self.mongo[collection].find({}, {'_id': 0}))
        with self.connection() as db:
            rows = db.execute('SELECT body FROM records WHERE collection=?',(collection,)).fetchall()
        return [json.loads(r[0]) for r in rows]
