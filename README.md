# 🎵 MixSpace

MixSpace is a dynamic, community-powered music curation system that transforms shared spaces like gyms, cafes, or retail stores into immersive audio environments tailored to the people currently inside.

### 🚀 What It Does
MixSpace bridges the gap between public music systems and individual taste. Using Spotify’s API and personal top tracks, MixSpace creates a real-time, crowd-sourced playlist that adapts to the preferences of everyone in the room.

### 🔁 The Problem
Most public spaces play music selected by a single person—or worse, a generic playlist. This often leaves customers listening to music they don’t enjoy. MixSpace was built to fix that by letting everyone in the space contribute passively to what’s playing.

### 🎤 How It Works
Scan to Join
Users scan a QR code to authenticate with their Spotify account.

Pull Top Tracks
Once authenticated, MixSpace automatically fetches each user's Top 50 Spotify tracks.

Host Sets the Mood
A designated host or "DJ" sets a theme prompt (e.g., "chill vibes," "hype workout," or "coffeehouse acoustics").

Smart Playlist Generation
MixSpace filters users’ top tracks to match the vibe of the current prompt using genre, mood, and tempo. It combines them into a randomized, rotating playlist.

Live Playlist Evolution
As more users scan in, the playlist evolves. The host controls how frequently songs shuffle and how much influence new users have over the current playlist.

### 🧠 Key Features
Spotify Integration – Leverages real listening history from Spotify for personalized curation.

QR Code Authentication – Frictionless entry with no sign-up or app install required.

Theme-Based Filtering – Host picks the vibe, MixSpace picks the tracks.

Dynamic Shuffle System – Rotating song selection that adapts as new users join.

Host Control Panel – Customize prompt, shuffle frequency, and playback behavior.

### 🛠️ Tech Stack
Frontend: HTML, CSS, TypeScript, Python

Backend: Python

APIs: Spotify Web API (OAuth 2.0, Top Tracks, Track Metadata)

Authentication: Spotify Authentication

### 💡 Use Cases
Gyms: Energize the space with songs your members ACTUALLY listen to.

Cafes: Create a relaxing vibe that reflects the crowd.

Social Events: Let your guests help build the atmosphere.
