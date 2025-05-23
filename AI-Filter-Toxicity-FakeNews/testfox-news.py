import requests
from bs4 import BeautifulSoup

def test_foxnews_articles():
    """Fetch latest foxnews articles and verify output."""
    url = "https://www.foxnews.com"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Adjust selector based on foxnews structure
            headlines = soup.find_all("h2", class_="article-title")  # Example class name

            if headlines:
                print("✅ Successfully retrieved foxnewsTV articles.")
                for i, headline in enumerate(headlines[:5]):  # Get top 5 articles
                    print(f"🔹 Article {i+1}: {headline.text.strip()}")
            else:
                print("❌ No headlines found. Check the selector.")
        else:
            print(f"❌ foxnews Scraper Error: {response.status_code}")
    except Exception as e:
        print(f"🚨 foxnews Scraper Request Error: {e}")

# Run the test function
test_foxnews_articles()
