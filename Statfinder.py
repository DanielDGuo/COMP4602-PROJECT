import os, json

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

if __name__ == "__main__":
    path = os.path.join(CACHE_DIR, "matchups.json")
    with open(path) as f:
        data = json.load(f)
    move_appearance_rate_dict = {}
    for entry in data.keys():
        if data[entry]["3_best_move"] in move_appearance_rate_dict.keys():
            move_appearance_rate_dict[data[entry]["3_best_move"]] += 1
        else:
            move_appearance_rate_dict[data[entry]["3_best_move"]] = 1
    print(move_appearance_rate_dict)