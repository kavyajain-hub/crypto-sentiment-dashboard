import os
import urllib.request
import re
import time

def download_file_from_google_drive(file_id, destination):
    url = f"https://docs.google.com/uc?export=download&id={file_id}"
    print(f"Downloading {file_id} to {destination}...", flush=True)
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            html_peek = response.read(65536) # Peek at the first 64KB
            
            # Check if we got a confirmation page
            if b"confirm=" in html_peek or b"download_warning" in html_peek:
                html_str = html_peek.decode('utf-8', errors='ignore')
                match = re.search(r'confirm=([a-zA-Z0-9_]+)', html_str)
                if match:
                    confirm_code = match.group(1)
                    confirm_url = f"https://docs.google.com/uc?export=download&confirm={confirm_code}&id={file_id}"
                    print(f"Found confirmation code: {confirm_code}, downloading from {confirm_url}...", flush=True)
                    req_confirm = urllib.request.Request(
                        confirm_url,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    with urllib.request.urlopen(req_confirm) as confirm_response, open(destination, 'wb') as out_file:
                        # Write the peeked data? No, the confirm response is a new request, so we stream it entirely
                        download_stream(confirm_response, out_file)
                else:
                    print("Could not find confirmation code, writing peeked and remaining HTML directly.", flush=True)
                    with open(destination, 'wb') as out_file:
                        out_file.write(html_peek)
                        out_file.write(response.read())
            else:
                # Direct download, write peeked and stream the rest
                with open(destination, 'wb') as out_file:
                    out_file.write(html_peek)
                    download_stream(response, out_file)
        print(f"Download complete: {destination}", flush=True)
    except Exception as e:
        print(f"Error occurred during download: {e}", flush=True)

def download_stream(response, out_file):
    chunk_size = 1024 * 1024 # 1MB
    bytes_downloaded = 0
    start_time = time.time()
    
    # Get total size if available
    total_size = response.getheader('Content-Length')
    if total_size:
        total_size = int(total_size)
        print(f"Total size: {total_size / (1024*1024):.2f} MB", flush=True)
    
    while True:
        chunk = response.read(chunk_size)
        if not chunk:
            break
        out_file.write(chunk)
        bytes_downloaded += len(chunk)
        elapsed = time.time() - start_time
        speed = (bytes_downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        if total_size:
            pct = (bytes_downloaded / total_size) * 100
            print(f"Downloaded {bytes_downloaded / (1024*1024):.2f} MB ({pct:.1f}%) - Speed: {speed:.2f} MB/s", end='\r', flush=True)
        else:
            print(f"Downloaded {bytes_downloaded / (1024*1024):.2f} MB - Speed: {speed:.2f} MB/s", end='\r', flush=True)
    print(f"\nFinished stream download: {bytes_downloaded / (1024*1024):.2f} MB downloaded total in {elapsed:.1f}s", flush=True)

if __name__ == "__main__":
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    # Historical Trader Data: 1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs
    # Fear Greed Index: 1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf
    download_file_from_google_drive("1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs", "historical_trader_data.csv")
    download_file_from_google_drive("1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf", "fear_greed_index.csv")
