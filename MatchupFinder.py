import os, json
import requests as re

base_url = "https://pokeapi.co/api/v2"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

if __name__ == "__main__":
    pokemon1_name = "charizard"
    pokemon2_name = "blastoise"

    path = os.path.join(OUTPUT_DIR, "matchups.json")
    with open(path) as f:
        data = json.load(f)
    
    url = f"{base_url}/pokemon/{pokemon1_name}"
    response = re.get(url).json()

    pokemon1_id = str(response["id"])
    
    url = f"{base_url}/pokemon/{pokemon2_name}"
    response = re.get(url).json()
    pokemon2_id = str(response["id"])

    if pokemon1_id + "_vs_" + pokemon2_id in data.keys():
        print(data[pokemon1_id + "_vs_" + pokemon2_id])
    elif pokemon2_id + "_vs_" + pokemon1_id in data.keys():
        print(data[pokemon2_id + "_vs_" + pokemon1_id])
    else:
        print("matchup not yet stored")