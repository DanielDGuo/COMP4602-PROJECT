import os, json

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

if __name__ == "__main__":
    pokemon_id = "3"
    moves_used_by = {}
    moves_used_against = {}

    path = os.path.join(CACHE_DIR, "matchups.json")
    with open(path) as f:
        data = json.load(f)
    for entry in data.keys():
        if pokemon_id + "_best_move" in data[entry].keys():
            if data[entry]["pokemon_1_id"] == pokemon_id:
                #tick up the counter for the pokemon's move
                if data[entry][pokemon_id + "_best_move"] in moves_used_by.keys():
                    moves_used_by[data[entry][pokemon_id + "_best_move"]] += 1
                else:
                    moves_used_by[data[entry][pokemon_id + "_best_move"]] = 1

                #tick up the counter for the pokemon's opponent's move
                if data[entry][data[entry]["pokemon_2_id"] + "_best_move"] in moves_used_against.keys():
                    moves_used_against[data[entry][data[entry]["pokemon_2_id"] + "_best_move"]] += 1
                else:
                    moves_used_against[data[entry][data[entry]["pokemon_2_id"] + "_best_move"]] = 1
            elif data[entry]["pokemon_2_id"] == pokemon_id:
                #tick up the counter for the pokemon's move
                if data[entry][pokemon_id + "_best_move"] in moves_used_by.keys():
                    moves_used_by[data[entry][pokemon_id + "_best_move"]] += 1
                else:
                    moves_used_by[data[entry][pokemon_id + "_best_move"]] = 1

                #tick up the counter for the pokemon's opponent's move
                if data[entry][data[entry]["pokemon_1_id"] + "_best_move"] in moves_used_against.keys():
                    moves_used_against[data[entry][data[entry]["pokemon_1_id"] + "_best_move"]] += 1
                else:
                    moves_used_against[data[entry][data[entry]["pokemon_1_id"] + "_best_move"]] = 1

    print(sorted(moves_used_by.items(), key=lambda x: x[1], reverse=True))
    print(sorted(moves_used_against.items(), key=lambda x: x[1], reverse=True))