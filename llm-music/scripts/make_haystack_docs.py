import json
import requests
import os

def get_mood_description(track):
    prompt = (
        f"Give a short description (1 or 2 sentences) of the song describing the mood, genre, energy, and vibe of "
        f"'{track['title']}' by {track['artist']}."
    )

    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "llama3",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    })

    if response.ok:
        return response.json()["message"]["content"].strip()
    else:
        print("Ollama Error:", response.text)
        return "Description unavailable."

def convert_to_haystack_docs():
    base_dir = os.path.dirname(__file__)
    input_path = os.path.join(base_dir, "..", "data", "processed_data.json")
    output_path = os.path.join(base_dir, "..", "data", "haystack_docs.json")
    with open(input_path) as f:
        tracks = json.load(f)

    docs = []
    for track in tracks:
        description = get_mood_description(track)
        docs.append({
            "content": f"{track['title']} by {track['artist']}. {description} Liked by {len(track['liked_by'])} users.",
            "meta": track
        })

    with open(output_path, "w") as f:
        json.dump(docs, f, indent=2)