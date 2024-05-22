from my_selenium import driver_setup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import redis
import os
import time

#Global list to hold driver instances
drivers = [driver_setup() for _ in range(5)]


# Function to capture screenshot of captcha image
def capture_screenshot(url, output_dir):
    try:
        # Get a driver instance from the list (round-robin)
        driver = drivers.pop(0)
        drivers.append(driver)  # Put the driver instance back to the list after usage

        driver.get(url)

        # Wait for captcha image to load
        captcha_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[style="flex-direction: column;"]>img'))
        )

        # Capture screenshot of the captcha image
        screenshot_filename = os.path.join(output_dir, f'{uuid.uuid4()}.png')
        captcha_img.screenshot(screenshot_filename)
        print('Captcha screenshot captured successfully', f'{uuid.uuid4()}.png')

    except Exception as e:
        print(f'Error occurred while capturing screenshot of captcha')
        pass


# Function to fetch URLs from Redis and distribute to drivers
def fetch_and_distribute(redis_conn, output_dir):
    executor = ThreadPoolExecutor(max_workers=5)
    while True:
        # Pop a URL from the Redis queue
        url = redis_conn.rpop('elect:start_urls')
        time.sleep(.5)
        if url:
            url = url.decode('utf-8')  # Decode bytes to string
            # Submit the task to capture screenshot
            executor.submit(capture_screenshot, url, output_dir)
        else:
            # If queue is empty, sleep for some time
            time.sleep(1)


# Main function
def main():
    # Output directory to save captcha screenshots
    output_dir = "/Users/aakashmahawar/Downloads/captcha_screenshots"

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Connect to Redis
    redis_conn = redis.Redis(host='localhost', port=6379, db=0)

    # Start the fetch and distribute process
    fetch_and_distribute(redis_conn, output_dir)


if __name__ == "__main__":
    main()
    [driver.quit() for driver in drivers]
