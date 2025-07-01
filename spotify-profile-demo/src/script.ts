const clientId = "e9e55e345a0149749e73a7d958746e32";
const params = new URLSearchParams(window.location.search);
const code = params.get("code");

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
        const tracks = await fetchTopTracksFromAPI();
        renderTopTracks(tracks);
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

async function fetchTopTracksFromAPI() {
  const res = await fetch("https://blendjam.vercel.app/api/generate_top50/get_tracks");
  if (!res.ok) {
    console.error("Failed to fetch saved top tracks");
    return [];
  }
  const data = await res.json();
  return Object.values(data.tracks);
}

function renderTopTracks(tracks: any[]) {
  const list = document.getElementById("trackList")!;
  list.innerHTML = "";
  tracks.forEach((track) => {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${track.name}</strong> - ${track.artist_names.join(", ")}`;
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
