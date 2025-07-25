import json
from collections import defaultdict
import os 

def reformat_spotify_data():
    """
    Reformats Spotify user track data to a simplified structure and saves as JSON.
    """
    track_dict = defaultdict(lambda: {
        "title": "",
        "artist": "",
        "liked_by": [],
        "uri": "",
        "image_url": ""
    })

    base_dir = os.path.dirname(__file__)
    raw_path = os.path.join(base_dir, "..", "data", "raw_data.json")
    with open(raw_path, "r") as file:
        input_data = json.load(file)

    for user in input_data:
        user_id_formatted = f"user_{user['user_id'].zfill(3)}"
        for track_id, track_info in user["tracks"].items():
            if track_dict[track_id]["title"] == "":
                track_dict[track_id]["title"] = track_info["name"]
                track_dict[track_id]["artist"] = track_info["artist_names"][0]
                track_dict[track_id]["uri"] = track_info["uri"]
                track_dict[track_id]["image_url"] = track_info["image_url"]
            track_dict[track_id]["liked_by"].append(user_id_formatted)

    output = list(track_dict.values())

    output_path = os.path.join(base_dir, "..", "data", "processed_data.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
