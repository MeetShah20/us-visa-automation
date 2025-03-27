import undetected_chromedriver as uc
import json
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_config():
    with open("config.json", "r") as file:
        config = json.loads(file.read())

        return config


def create_driver():
    # Configure Chrome options
    options = uc.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode (optional)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize undetected ChromeDriver
    driver = uc.Chrome(options=options)

    return driver  # Returning driver in case further operations are needed

def main():
    config = open_config()
    driver = create_driver()
    time.sleep(1)
    driver.get(config["login_url"])
    input("Enter when login and captcha is completed: ")
    solve_questions(driver, config)

def solve_questions(driver, config):
    """
    Dynamically detects and solves the security questions by extracting the last word from the question text
    and entering it into the next input field as the password.

    :param driver: Selenium WebDriver instance
    """
    wait = WebDriverWait(driver, random.uniform(7, 12))  # Randomized wait time for human-like behavior

    try:
        # Find all question elements dynamically
        question_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.Paragraph")))
        
        for question_element in question_elements:
            try:
                # Locate the <p> tag containing the security question
                question_text_element = question_element.find_element(By.TAG_NAME, "p")
                question_text = question_text_element.text.strip()

                if question_text:
                    # Extract last word from question text (remove '?' if present)
                    answer = question_text.split()[-1].rstrip('?')

                    # Find the next input field (password field)
                    password_input = question_element.find_element(By.XPATH, "following-sibling::li//input")

                    # Type the extracted password with a typing delay
                    for char in answer:
                        password_input.send_keys(char)
                        time.sleep(random.uniform(0.1, 0.3))  # Simulate human typing

                    print(f"Solved question: {question_text} -> {answer}")

                    # Random delay before processing the next question
                    time.sleep(random.uniform(1.5, 3.5))

            except Exception as e:
                print("Error processing a question, skipping...")

    except Exception as e:
        print("No security questions found.")

    # Click the continue button
    try:
        continue_selector = config.get("continue_button_after_q&a")  # Read from config.json

        if continue_selector:
            continue_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, continue_selector)))
            
            time.sleep(random.uniform(1, 3))  # Random delay before clicking
            driver.execute_script("arguments[0].click();", continue_button)  # JS Click for reliability

            print("Clicked continue button.")

            # Wait for the next page to load before quitting
            time.sleep(random.uniform(5, 10))  # Allow transition time
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Ensure page has loaded

        else:
            print("Error: Continue button selector not found in config.json!")

    except Exception as e:
        print("Continue button not found or not clickable.")

    # **Do NOT quit the driver immediately**
    print("Waiting to ensure next page loads...")
    time.sleep(random.uniform(8, 12))  # Extra wait to avoid crashes




if __name__ == "__main__":
    main()