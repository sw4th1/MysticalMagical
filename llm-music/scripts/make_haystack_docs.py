import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_mood_description(track):
    prompt = (
        f"Give a short description (1 or 2 sentences) of the song describing the mood, genre, energy, and vibe"
        f"'{track['title']}' by {', '.join(track['artist_names'])}."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def convert_to_haystack_docs():
    with open("data/processed_tracks.json") as f:
        tracks = json.load(f)

    docs = []
    for track in tracks:
        description = get_mood_description(track)
        docs.append({
            "content": f"{track['title']} by {', '.join(track['artist_names'])}. {description} Liked by {len(track['liked_by'])} users.",
            "meta": track
        })

    with open("data/haystack_docs.json", "w") as f:
        json.dump(docs, f, indent=2)