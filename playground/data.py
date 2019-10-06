from pathlib_mate import Path
import json


data = json.loads(Path("data.json").read_text())

print(json.dumps(json.loads(data["body"]), indent=4))