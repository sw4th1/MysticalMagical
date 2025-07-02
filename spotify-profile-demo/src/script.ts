const clientId = "e9e55e345a0149749e73a7d958746e32";
const params = new URLSearchParams(window.location.search);
const code = params.get("code");

interface UserProfile {
  display_name: string;
  images: { url: string }[];
  id: string;
  email: string;
  uri: string;
  external_urls: { spotify: string };
  href: string;
}

interface Track {
  id: string;
  name: string;
  artist_names: string[];
  uri: string;
  image_url: string;
}

interface UserData {
  user_name: string;
  date_saved: string;
  track_count: number;
  tracks: { [key: string]: {
    name: string;
    artist_names: string[];
    uri: string;
    image_url: string;
  }};
}

(async () => {
  if (!code) {
    redirectToAuthCodeFlow(clientId);
  } else {
    try {
      const accessToken = await getAccessToken(clientId, code);
      const profile = await fetchProfile(accessToken);
      populateUI(profile);

      const btn = document.getElementById("fetchTopTracks")!;
      btn.addEventListener("click", async () => {
        try {
          const tracks = await fetchTopTracks(accessToken);
          renderTopTracks(tracks);
          saveTracksAsJSON(tracks, profile.display_name);
        } catch (error) {
          console.error("Error fetching top tracks:", error);
          alert("Failed to fetch top tracks. Please try again.");
        }
      });
    } catch (error) {
      console.error("Error loading profile:", error);
    }
  }
})();

export async function redirectToAuthCodeFlow(clientId: string) {
  const verifier = generateCodeVerifier(128);
  const challenge = await generateCodeChallenge(verifier);
  localStorage.setItem("verifier", verifier);

  const params = new URLSearchParams();
  params.append("client_id", clientId);
  params.append("response_type", "code");
  params.append("redirect_uri", "https://blendjam.vercel.app/callback");
  params.append("scope", "user-read-private user-read-email user-top-read");
  params.append("code_challenge_method", "S256");
  params.append("code_challenge", challenge);

  document.location = `https://accounts.spotify.com/authorize?${params.toString()}`;
}

function generateCodeVerifier(length: number) {
  let text = "";
  let possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

async function generateCodeChallenge(codeVerifier: string) {
  const data = new TextEncoder().encode(codeVerifier);
  const digest = await window.crypto.subtle.digest("SHA-256", data);
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

export async function getAccessToken(clientId: string, code: string): Promise<string> {
  const verifier = localStorage.getItem("verifier")!;
  const params = new URLSearchParams();
  params.append("client_id", clientId);
  params.append("grant_type", "authorization_code");
  params.append("code", code);
  params.append("redirect_uri", "https://blendjam.vercel.app/callback");
  params.append("code_verifier", verifier);

  const result = await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params,
  });

  const { access_token } = await result.json();
  localStorage.setItem("access_token", access_token);
  return access_token;
}

async function fetchProfile(token: string): Promise<UserProfile> {
  const result = await fetch("https://api.spotify.com/v1/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await result.json();
}

async function fetchTopTracks(token: string): Promise<Track[]> {
  const result = await fetch("https://api.spotify.com/v1/me/top/tracks?limit=50&time_range=short_term", {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!result.ok) {
    throw new Error(`Failed to fetch top tracks: ${result.status}`);
  }

  const data = await result.json();
  const tracks = data.items || [];

  return tracks.map((track: any): Track => ({
    id: track.id,
    name: track.name,
    artist_names: track.artists.map((artist: any) => artist.name),
    uri: track.uri,
    image_url: track.album?.images?.find((img: any) => img.height === 300)?.url || 
               track.album?.images?.[0]?.url || "N/A"
  }));
}

function saveTracksAsJSON(tracks: Track[], userName: string): void {
  const userData: UserData = {
    user_name: userName,
    date_saved: new Date().toISOString(),
    track_count: tracks.length,
    tracks: {}
  };

  // Convert tracks to object format
  tracks.forEach(track => {
    userData.tracks[track.id] = {
      name: track.name,
      artist_names: track.artist_names,
      uri: track.uri,
      image_url: track.image_url
    };
  });

  // Wrap in the required format
  const payload = {
    type: 'data',
    payload: userData
  };

  // Log the JSON
  console.log("🎵 Sending Top Tracks Data:");
  console.log(JSON.stringify(payload, null, 2));

  // POST to your ngrok URL
  postDataToServer(payload);
}

async function postDataToServer(data: any): Promise<void> {
  // Log the data for debugging
  console.log("📦 Spotify Data being sent:");
  console.log(JSON.stringify(data, null, 2));
  
  try {
    console.log("🚀 Sending to HTTPS ngrok server...");
    
    const response = await fetch('https://936a-66-253-203-14.ngrok-free.app', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data)
    });

    console.log("📡 Response status:", response.status);

    if (response.ok) {
      let responseData;
      try {
        responseData = await response.json();
      } catch {
        responseData = await response.text();
      }
      console.log("✅ Data sent successfully!", responseData);
      
      // Show success message
      const message = document.createElement("div");
      message.style.cssText = "margin: 10px 0; padding: 10px; background: #d4edda; color: #155724; border: 1px solid #c3e6cb; border-radius: 5px; text-align: center;";
      message.textContent = "✅ Top tracks data sent successfully to your server!";
      
      const tracksSection = document.getElementById("topTracks")!;
      tracksSection.insertBefore(message, tracksSection.firstChild);
      
      setTimeout(() => {
        if (message.parentNode) {
          message.parentNode.removeChild(message);
        }
      }, 5000);
      
    } else {
      const errorText = await response.text();
      throw new Error(`Server responded with status: ${response.status}. Response: ${errorText}`);
    }
    
  } catch (error) {
    console.error("❌ POST failed:", error);
    
    let errorMessage = 'Unknown error occurred';
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      errorMessage = 'Network/CORS error - Cannot reach server';
    } else if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    // Show error message with copy option
    const message = document.createElement("div");
    message.style.cssText = "margin: 10px 0; padding: 15px; background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 5px;";
    message.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 10px;">❌ Failed to send data: ${errorMessage}</div>
      <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; margin: 10px 0;">
        <strong>💡 Fallback:</strong> Your data is logged to the console - you can copy it manually.
      </div>
      <button id="copyDataBtn" style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
        📋 Copy Data to Clipboard
      </button>
    `;
    
    const tracksSection = document.getElementById("topTracks")!;
    tracksSection.insertBefore(message, tracksSection.firstChild);
    
    // Add copy functionality
    const copyBtn = message.querySelector('#copyDataBtn');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(JSON.stringify(data, null, 2)).then(() => {
          copyBtn.textContent = '✅ Copied!';
          setTimeout(() => {
            copyBtn.textContent = '📋 Copy Data to Clipboard';
          }, 2000);
        });
      });
    }
    
    setTimeout(() => {
      if (message.parentNode) {
        message.parentNode.removeChild(message);
      }
    }, 10000);
  }
}

function renderTopTracks(tracks: Track[]): void {
  const list = document.getElementById("trackList")!;
  list.innerHTML = "";
  
  if (!tracks || tracks.length === 0) {
    list.innerHTML = "<li>No tracks found</li>";
    document.getElementById("topTracks")!.style.display = "block";
    return;
  }

  tracks.forEach((track, index) => {
    const li = document.createElement("li");
    li.style.cssText = "display: flex; align-items: center; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 8px;";
    
    const imageHtml = track.image_url && track.image_url !== "N/A" 
      ? `<img src="${track.image_url}" alt="${track.name}" style="width: 60px; height: 60px; margin-right: 15px; border-radius: 6px;">`
      : `<div style="width: 60px; height: 60px; margin-right: 15px; background: #ddd; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px;">No Image</div>`;
    
    li.innerHTML = `
      ${imageHtml}
      <div>
        <div style="font-weight: bold; margin-bottom: 5px;">${index + 1}. ${track.name}</div>
        <div style="color: #666; font-size: 14px;">${track.artist_names.join(", ")}</div>
      </div>
    `;
    list.appendChild(li);
  });
  
  document.getElementById("topTracks")!.style.display = "block";
}

function populateUI(profile: UserProfile) {
  document.getElementById("displayName")!.innerText = profile.display_name;
  if (profile.images[0]) {
    const profileImage = new Image(200, 200);
    profileImage.src = profile.images[0].url;
    document.getElementById("avatar")!.appendChild(profileImage);
  }
  document.getElementById("id")!.innerText = profile.id;
  document.getElementById("email")!.innerText = profile.email;
  document.getElementById("uri")!.innerText = profile.uri;
  document.getElementById("uri")!.setAttribute("href", profile.external_urls.spotify);
  document.getElementById("url")!.innerText = profile.href;
  document.getElementById("url")!.setAttribute("href", profile.href);
  document.getElementById("imgUrl")!.innerText = profile.images[0]?.url ?? "(no profile image)";
}