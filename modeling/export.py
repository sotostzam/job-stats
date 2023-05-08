from database import MongoDB
import json

db = MongoDB()
documents = list(db.find({'_id': 0,
                          'roles': 1,
                          'location': 1,
                          'type': 1,
                          'industry': 1,
                          'workplace': 1,
                          'level': 1}))

json_object = json.dumps(documents, indent=4, default=str)

with open("../reports/posts_a.json", "w") as f:
    f.write(json_object)