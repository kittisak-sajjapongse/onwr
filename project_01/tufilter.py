import json

def main():
    with open("merged.json") as f:
        merged = json.load(f)
    with open("filter.json") as f:
        filter = set()
        for title in json.load(f):
            filter.add(title["title"])

    filtered_merged = [entry for entry in merged if entry["title"] not in filter]
    print(f"{len(filtered_merged)}/{len(merged)}")

    with open("filtered_merged.json", "w") as f:
        json.dump(filtered_merged, f)

if __name__ == "__main__":
    main()