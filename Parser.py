import damage_calculator as dcalc
import requests as re
import json, os

base_url = "https://pokeapi.co/api/v2"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

def fetch_pokemon(name):
    url = f"{base_url}/pokemon/{name}"
    print(url)
    os.makedirs(CACHE_DIR, exist_ok=True)

    path = os.path.join(CACHE_DIR, "pokemon_" + name + ".json")

    if os.path.exists(path):
        with open(path) as f:
            print("file found in cache")
            return json.load(f)

    response = re.get(url)

    if response.status_code == 200:
        print("file fetched")
        with open(path, "w") as f:
            json.dump(response.json(), f)
        return response.json()
    else:
        print("PokemonAPI endpoint not found. Name error. Error " + response.status_code)
        return
    

if __name__ == "__main__":
    fetch_pokemon("pikachu")