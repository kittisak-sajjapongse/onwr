import json
import sys

from typing import List

def main(result_files: List):
    result_keys = set()
    results = []
    total_results = 0
    results_small = []
    for file in result_files:
        print(file)
        with open(file, "r") as f:
            result_entries = json.load(f)
        for entry in result_entries:
            key = entry["_doc_page_url"]
            total_results += 1
            if not key in result_keys:
                result_keys.add(key)
                results.append(entry)
                results_small.append({
                    "title": entry["title"],
                })
    print(f"Merged {len(results)}/{total_results} results")
    with open("merged.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open("merged_small.json", "w") as f:
        json.dump(results_small, f, ensure_ascii=False, indent=2)
    print("Write to merged.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{sys.argv[0]} [RESULT_JSON_0] ...")
        sys.exit(-1)
    result_files = sys.argv[1:(len(sys.argv))]
    main(result_files)