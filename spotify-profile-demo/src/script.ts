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
  user_id: string;
  tracks: { [key: string]: {
    name: string;
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
          saveTracksAsJSON(tracks);
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
  const result = await fetch("https://api.spotify.com/v1/me/top/tracks?limit=24&time_range=short_term", {
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

function saveTracksAsJSON(tracks: Track[]): void {
  try {
    const sanitizedTracks: { [key: string]: any } = {};
    
    tracks.forEach(track => {
      sanitizedTracks[track.id] = {
        name: sanitizeString(track.name),
        uri: sanitizeString(track.uri),
        image_url: sanitizeString(track.image_url)
      };
    });

    const userData: UserData = {
      user_id: "1",
      tracks: sanitizedTracks
    };

    const payload = {
      type: 'data',
      payload: userData
    };

    console.log("🎵 Sending Top Tracks Data:");
    console.log("Payload size:", JSON.stringify(payload).length, "characters");
    
    const jsonString = JSON.stringify(payload, null, 2);
    console.log("✅ JSON validation passed");
    console.log(jsonString);

    postDataToServer(payload);
    
    // download
    addDownloadButton(payload);
  } catch (error) {
    console.error("❌ Error preparing data:", error);
    
    // error message
    const message = document.createElement("div");
    message.style.cssText = "margin: 10px 0; padding: 15px; background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 5px;";
    message.textContent = `Error preparing data: ${error instanceof Error ? error.message : 'Unknown error'}`;
    
    const tracksSection = document.getElementById("topTracks")!;
    tracksSection.insertBefore(message, tracksSection.firstChild);
  }
}

// sanitize string maybe ...?
function sanitizeString(str: any): string {
  if (typeof str !== 'string') {
    return String(str || '');
  }
  
  return str
    .replace(/[\u0000-\u001F\u007F-\u009F]/g, '') 
    .replace(/"/g, '\\"') 
    .replace(/\\/g, '\\\\') 
    .trim();
}

async function postDataToServer(data: any): Promise<void> {
  console.log("data being sent");
  
  try {
    // check characters
    const jsonString = JSON.stringify(data);
    console.log("data size:", jsonString.length, "characters");
    
    if (jsonString.length > 1000000) { // too large
      throw new Error("Data too large - consider reducing track count");
    }
        
    const response = await fetch('https://801f-2a09-bac5-7a4b-1cd2-00-2df-e5.ngrok-free.app', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
        'Accept': 'application/json'
      },
      body: jsonString
    });

    console.log("response status:", response.status);
    console.log("response headers:", Object.fromEntries(response.headers.entries()));

    if (response.ok) {
      let responseData;
      const contentType = response.headers.get('content-type');
      
      try {
        if (contentType && contentType.includes('application/json')) {
          responseData = await response.json();
        } else {
          responseData = await response.text();
        }
      } catch (parseError) {
        console.warn("Could not parse response:", parseError);
        responseData = "Response received but could not parse";
      }
      
      console.log("data sent successfully!", responseData);
      
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
      console.error("Server error response:", errorText);
      throw new Error(`Server responded with status: ${response.status}. Response: ${errorText}`);
    }
    
  } catch (error) {
    console.error("❌ POST failed:", error);
    
    let errorMessage = 'Unknown error occurred';
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      errorMessage = 'Network/CORS error - Cannot reach server';
    } else if (error instanceof SyntaxError) {
      errorMessage = 'JSON parsing error - check for special characters in track data';
    } else if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    const message = document.createElement("div");
    message.style.cssText = "margin: 10px 0; padding: 15px; background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 5px;";
    message.textContent = `❌ Error sending data: ${errorMessage}`;
    
    const tracksSection = document.getElementById("topTracks")!;
    tracksSection.insertBefore(message, tracksSection.firstChild);
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

function addDownloadButton(data: any): void {
  const existingButton = document.getElementById("downloadJson");
  if (existingButton) {
    existingButton.remove();
  }

  const downloadButton = document.createElement("button");
  downloadButton.id = "downloadJson";
  downloadButton.textContent = "📥 Download JSON";
  downloadButton.style.cssText = `
    margin: 10px 0; 
    padding: 10px 20px; 
    background: #1db954; 
    color: white; 
    border: none; 
    border-radius: 25px; 
    cursor: pointer; 
    font-weight: bold;
    font-size: 14px;
    transition: background-color 0.3s;
  `;

  downloadButton.addEventListener("mouseenter", () => {
    downloadButton.style.backgroundColor = "#1ed760";
  });

  downloadButton.addEventListener("mouseleave", () => {
    downloadButton.style.backgroundColor = "#1db954";
  });

  downloadButton.addEventListener("click", () => {
    downloadJSON(data);
  });

  const tracksSection = document.getElementById("topTracks")!;
  tracksSection.insertBefore(downloadButton, tracksSection.firstChild);
}

function downloadJSON(data: any): void {
  try {
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.href = url;
    link.download = `spotify-top-tracks-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    console.log("✅ JSON file downloaded successfully");
  } catch (error) {
    console.error("❌ Error downloading JSON:", error);
    alert("Failed to download JSON file. Please try again.");
  }
}