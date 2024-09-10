import pandas as pd
import time
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

# URL of the website to scrape
urls = [
    "https://www.orami.co.id/shopping/category/aktifitas-hiburan-bayi?_shouldResolveHref=true",
    "https://www.orami.co.id/shopping/category/gendongan-bayi-aksesoris?_shouldResolveHref=true",
    "https://www.orami.co.id/shopping/category/kereta-bayi-aksesoris?_shouldResolveHref=true",
    "https://www.orami.co.id/shopping/category/aksesoris-kereta-bayi-2?_shouldResolveHref=true",
    "https://www.orami.co.id/shopping/category/kursi-mobil-bayi-aksesoris?_shouldResolveHref=true",
    "https://www.orami.co.id/shopping/category/aksesoris-kursi-mobil-bayi-anak?_shouldResolveHref=true"
]

# Initialize the ChromeOptions
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run headless (without opening a browser window)

all_unique_data = set()

for url in urls:
    # Initialize the ChromeDriver for each URL
    driver = webdriver.Chrome(options=options)
    try:
        # Open the webpage
        driver.get(url)

        # Initialize an empty list to store the script content
        script_content_list = []

        # Scroll down to load content
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Find and store script elements containing the desired data
        for script in driver.find_elements(By.TAG_NAME, "script"):
            script_content = script.get_attribute("innerHTML")
            if "window.dataLayer.push({" in script_content and not '{"ecommerce":null}' in script_content:
                script_content_list.append(script_content)

        # Process the script content
        if script_content_list:
            for script_content in script_content_list:
                try:
                    # Extract JSON data from the script content
                    json_data_str = script_content.split("window.dataLayer.push(")[1].split(")")[0]
                    json_data = json.loads(json_data_str)

                    # Access the impressions data
                    impressions = json_data.get('ecommerce', {}).get('impressions', [])

                    # Extract brand name and category, and add to the set
                    for item in impressions:
                        brand = item.get('brand', 'N/A')
                        category = item.get('category', 'N/A')
                        all_unique_data.add((brand, category))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

    # Add a delay between requests to avoid being flagged as a bot
    time.sleep(5)

# Convert the set to a DataFrame
df = pd.DataFrame(list(all_unique_data), columns=['Brand', 'Category'])

# Generate the timestamp in the JKT (Jakarta) timezone
jakarta_timezone = pytz.timezone('Asia/Jakarta')
timestamp = datetime.now(jakarta_timezone).strftime('%Y-%m-%d-%H%M')

# Save the results to a CSV file
csv_filename = f'Orami_scrape_{timestamp}.csv'
df.to_csv(csv_filename, index=False)
print(f'Results saved to {csv_filename}')
