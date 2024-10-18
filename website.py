import os
import time
from datetime import datetime
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

# Set the path to your local GeckoDriver
geckodriver_path = os.path.join(os.getcwd(), 'geckodriver.exe')  # Use the current working directory

# Set the path to the Firefox binary (adjust this path if needed)
firefox_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'  # Update if Firefox is in a different location

# Set up Selenium WebDriver for Firefox in headless mode
options = Options()
options.binary_location = firefox_binary_path  # Set the Firefox binary path
options.headless = True  # Enable headless mode
driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)

# Function to remove the bottom 1100 pixels from the screenshot
def remove_bottom(image):
    width, height = image.size
    cropped_image = image.crop((0, 0, width, height - 1725))  # Crop the image to remove the bottom 1100 pixels
    return cropped_image

# Function to take a full screenshot of the article
def take_full_page_screenshot(article_url, date, index, folder):
    driver.get(article_url)
    time.sleep(3)  # Allow time for the page to load
    # Take full-page screenshot as PNG
    png = driver.get_full_page_screenshot_as_png()
    image = Image.open(io.BytesIO(png))  # Convert PNG to Image
    # Convert to RGB to remove alpha channel
    image = image.convert('RGB')
    
    # Remove the bottom 1100 pixels of the image
    image = remove_bottom(image)

    # Format the date to YYYY-MM-DD for sorting purposes
    formatted_date = datetime.strptime(date, "%a, %b %d, %Y").strftime("%Y-%m-%d")
    # Create a unique filename using formatted date and index
    screenshot_name = os.path.join(folder, f"{formatted_date}_{index}.jpg")
    
    image.save(screenshot_name, "JPEG")  # Save as JPG
    print(f"Screenshot saved as {screenshot_name}")

# Function to fetch articles and take screenshots from a given URL
def fetch_articles_and_screenshots(url, div_class, folder):
    page_number = 1
    while True:
        driver.get(f"{url}?page={page_number}")
        time.sleep(3)  # Allow time for the page to load
        
        # Parse the HTML content
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Check if the page is valid by looking for a specific element (modify as needed)
        if "Page doesn't exist" in driver.page_source:
            print(f"No more pages available after page {page_number}.")
            break

        # Dictionary to count occurrences of dates
        date_count = {}

        # Find all relevant divs
        divs = soup.find_all('div', class_=div_class)

        if not divs:  # If no divs are found, exit the loop
            print(f"No articles found on page {page_number}.")
            break

        for div in divs:
            # Extract the date from the small element
            date_tag = div.find('small', class_='has-text-grey')
            link_tag = div.find('a', class_='button is-link')
            
            if date_tag and link_tag:
                date = date_tag.get_text(strip=True)
                article_link = f"https://www.tsu.edu.ph{link_tag['href']}"
                
                # Increment the count for this date
                if date in date_count:
                    date_count[date] += 1
                else:
                    date_count[date] = 1
                
                # Use the count as the index for the filename
                index = date_count[date]
                
                print(f"Found article: {article_link} on date: {date}")
                take_full_page_screenshot(article_link, date, index, folder)

        page_number += 1  # Move to the next page

# Create folders if they don't exist
news_folder = "news"
announcement_folder = "announcements"
os.makedirs(news_folder, exist_ok=True)
os.makedirs(announcement_folder, exist_ok=True)

# URLs and their corresponding div classes
urls_and_classes = [
    ("https://www.tsu.edu.ph/news/2024-news/", "column is-6-tablet is-3-desktop", news_folder),
    ("https://www.tsu.edu.ph/announcements/2024-announcements/", "column is-4", announcement_folder),
]

# Process each URL
for url, div_class, folder in urls_and_classes:
    fetch_articles_and_screenshots(url, div_class, folder)

# Close the driver
driver.quit()
