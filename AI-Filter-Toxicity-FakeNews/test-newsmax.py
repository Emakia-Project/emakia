import requests
from bs4 import BeautifulSoup

def test_newsmax_articles():
    """Fetch latest NewsmaxTV articles using enhanced request handling."""
    url = "https://www.newsmax.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)  # Add rotating headers
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Adjust selector based on site structure
            headlines = soup.select("a[href*='news']")  # Try finding actual news links

            if headlines:
                print("✅ Successfully retrieved NewsmaxTV articles.")
                for i, headline in enumerate(headlines[:5]):  # Get top 5 articles
                    print(f"🔹 Article {i+1}: {headline.text.strip()} - {headline['href']}")
            else:
                print("❌ No headlines found. Try a different selector.")
        else:
            print(f"❌ Newsmax Scraper Error: {response.status_code}")
    except requests.Timeout:
        print("🚨 Request timed out! NewsmaxTV might be blocking or responding too slowly.")
    except requests.exceptions.RequestException as e:
        print(f"🚨 Newsmax Scraper Request Error: {e}")

# Run the test function
test_newsmax_articles()
