import damage_calculator as dcalc
import requests as re
import json, os

base_url = "https://pokeapi.co/api/v2"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

#fetches pokemon by id
def fetch_pokemon(pokemon_id):
    if int(pokemon_id) < 1 or int(pokemon_id) > 1025:
        raise ValueError("Pokemon ID must be between 1 and 1025.")
    #fetch URL
    url = f"{base_url}/pokemon/{pokemon_id}"
    #create the cache directory for pokemon
    os.makedirs(os.path.join(CACHE_DIR, "pokemon_by_id"), exist_ok=True)

    #set the path for the json file
    path = os.path.join(CACHE_DIR, "pokemon_by_id", "pokemon_" + pokemon_id + ".json")

    #if it exists, it's been fetched before. Get the file from the cache instead of making an API request
    if os.path.exists(path):
        with open(path) as f:
            print("file found in cache")
            return json.load(f)

    #make an API request for the pokemon
    print("file fetched")
    response = re.get(url)

    if response.status_code == 200:
        #format the data before dumping it into the file
        data = response.json()
        remove_keys = ["base_experience", "cries", "forms", "game_indices", "height", "held_items", "is_default", "location_area_encounters", "order", "past_abilities", "past_stats", "past_types", "sprites"]
        for key in remove_keys:
            data.pop(key, None)

        for move in data["moves"]:
            move.pop("version_group_details")


        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return data
    else:
        #pokemon doesn't exist, return an error message
        raise re.exceptions.HTTPError("PokemonAPI endpoint not found. Name error. Error " + str(response.status_code))

#fetches pokemon by id. Alt forms need to inherit some values from their base form.
#need to be inherited: moves, abilities, 
def fetch_alt_form_pokemon(pokemon_id):
    if int(pokemon_id) < 10001 or int(pokemon_id) > 10325:
        raise ValueError("Pokemon alternate form ID must be between 10001 and 10325.")
    #fetch URL
    url = f"{base_url}/pokemon/{pokemon_id}"
    #create the cache directory for pokemon
    os.makedirs(os.path.join(CACHE_DIR, "pokemon_by_id"), exist_ok=True)

    #set the path for the json file
    path = os.path.join(CACHE_DIR, "pokemon_by_id", "pokemon_" + pokemon_id + ".json")

    #if it exists, it's been fetched before. Get the file from the cache instead of making an API request
    if os.path.exists(path):
        with open(path) as f:
            print("file found in cache")
            return json.load(f)

    #make an API request for the pokemon
    print("file fetched")
    response = re.get(url)

    if response.status_code == 200:
        #format the data before dumping it into the file
        data = response.json()
        remove_keys = ["base_experience", "cries", "forms", "game_indices", "height", "held_items", "is_default", "location_area_encounters", "order", "past_abilities", "past_stats", "past_types", "sprites"]
        for key in remove_keys:
            data.pop(key, None)

        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return data
    else:
        #pokemon doesn't exist, return an error message
        raise re.exceptions.HTTPError("PokemonAPI endpoint not found. Name error. Error " + str(response.status_code))


#get stats at lv100
#returns a dict
def calculate_stats(pokemon_id):
    max_stats = {}
    base_stats = fetch_pokemon(pokemon_id)["stats"]
    for stat in base_stats:
        match stat["stat"]["name"]:
            case "hp":
                max_stats["hp"] = 110 + (2*stat["base_stat"] + 31)
            case "attack":
                max_stats["atk"] = 5 + (2*stat["base_stat"] + 31)
            case "defense":
                max_stats["def"] = 5 + (2*stat["base_stat"] + 31)
            case "special-attack":
                max_stats["spa"] = 5 + (2*stat["base_stat"] + 31)
            case "special-defense":
                max_stats["spd"] = 5 + (2*stat["base_stat"] + 31)
            case "speed":
                max_stats["spe"] = 5 + (2*stat["base_stat"] + 31)
    if len(max_stats) < 6:
        raise ValueError("Some stats not found for pokemon with id " + str(pokemon_id) + ". Stats received: " + str(max_stats.keys()))
    return max_stats

if __name__ == "__main__":
    #fetch all 1025 pokemon with ids 1 to 1025
    print(calculate_stats("1"))
    #diancie
    # fetch_pokemon("719")
    #fetch alternate forms with ids 10001 to 10325
    #mega-diancie
    # fetch_alt_form_pokemon("10075")
    #need to store abilities, forms, id, moves, name, stats, type, weight