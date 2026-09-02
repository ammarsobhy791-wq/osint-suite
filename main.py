import sys
import asyncio
import aiohttp
import networkx as nx
from pyvis.network import Network
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# --- 1. Email Recon ---
CHECK_SERVICES = {
    "Imgur": "https://imgur.com/signin/check_email",
    "Adobe": "https://auth.services.adobe.com/signin/v2/users",
    "Pinterest": "https://www.pinterest.com/_ng_l/v3/login/handshake/"
}

async def check_email_site(session, site, url, email, G):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with session.post(url, data={"email": email}, headers=headers, timeout=5) as resp:
            if resp.status in [200, 400]:
                print(f"[+] Match found on {site}")
                G.add_node(site, group="Service")
                G.add_edge(email, site, label="Associated")
    except Exception:
        pass

async def email_recon():
    email = input("\nEnter Target Email: ").strip()
    G = nx.Graph()
    G.add_node(email, group="Target", size=30)
    print(f"[*] Scanning {email}...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [check_email_site(session, site, url, email, G) for site, url in CHECK_SERVICES.items()]
        await asyncio.gather(*tasks)

    net = Network(height="750px", width="100%", bgcolor="#1a1a1a", font_color="white", cdn_resources='remote')
    net.from_nx(G)
    net.save_graph("email_results.html")
    print("[✔] Saved to email_results.html")

# --- 2. Photo Forensics ---
def photo_recon():
    path = input("\nEnter Image Path: ").strip()
    try:
        img = Image.open(path)
        exif = img._getexif()
        if not exif:
            print("[-] No EXIF metadata found.")
            return
        
        G = nx.Graph()
        G.add_node("Image", title=path, size=30)
        data = {TAGS.get(k, k): v for k, v in exif.items()}
        
        for k in ['Make', 'Model', 'DateTimeOriginal', 'Software']:
            if k in data:
                val = str(data[k])
                print(f"[+] {k}: {val}")
                G.add_node(val, group="Metadata")
                G.add_edge("Image", val, label=k)

        net = Network(height="750px", width="100%", bgcolor="#1a1a1a", font_color="white", cdn_resources='remote')
        net.from_nx(G)
        net.save_graph("photo_results.html")
        print("[✔] Saved to photo_results.html")
    except Exception as e:
        print(f"[-] Error: {e}")

# --- Main Menu ---
def main():
    print("="*30)
    print("   Defensive OSINT Suite   ")
    print("="*30)
    print("1. Email Reconnaissance")
    print("2. Photo Metadata Analyzer")
    print("3. Exit")
    
    choice = input("\nSelect Option (1-3): ").strip()
    if choice == '1':
        asyncio.run(email_recon())
    elif choice == '2':
        photo_recon()
    else:
        sys.exit()

if __name__ == "__main__":
    main()
