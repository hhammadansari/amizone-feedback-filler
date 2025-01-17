import sys
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console

console = Console()

def pprint(*args, **kwargs):
    console.print(*args, **kwargs)

# User input
uid = input("Enter your Amizone ID: ")
passw = input("Enter your password: ")
comments = input("Enter your comments: ")
rating = int(input("Enter your rating (5=Strongly agree ... 1=Strongly disagree): "))

# Set up WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)
driver.maximize_window()

def visit_amizone():
    """Visit Amizone and log in."""
    driver.get("https://www.amizone.net")
    wait.until(EC.presence_of_element_located((By.NAME, '_UserName'))).send_keys(uid)
    driver.find_element(By.NAME, '_Password').send_keys(passw)
    driver.find_element(By.CLASS_NAME, 'login100-form-btn').click()

def verify_login():
    """Verify if login was successful."""
    try:
        wait.until(EC.url_contains('s.amizone.net/Home'))
        pprint('Login Successful!', style='b green')
    except:
        driver.quit()
        pprint("Login Failed! Please check your ID/Password!", style='b red')
        sys.exit()

def close_popups():
    """Close any pop-ups that might appear."""
    try:
        sleep(2)
        popups = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'close'))
        )
        pprint(f"{len(popups)} Pop-ups found!", style='b yellow')
        for close_btn in popups:
            try:
                close_btn.click()
                pprint('✔', style='b green', end=' ')
            except:
                pprint('✘', style='b red', end=' ')
    except:
        pprint("No Pop-ups found!", style='b green')

def select_my_faculty():
    """Navigate to the faculty feedback section."""
    try:
        faculty_button = wait.until(EC.element_to_be_clickable((By.ID, 'M27')))
        faculty_button.click()
    except:
        pprint('No Faculty Feedback Exists for you!', style='b green')

def fill():
    """Fill rating for a subject."""
    script = (
        f"var items = document.querySelectorAll('input[value=\"{rating}\"]');"
        "for (var i = 0; i < items.length; i++) {items[i].click();}"
    )
    driver.execute_script(script)

def yesno():
    """Answer yes/no questions."""
    for i in range(1, 4):
        driver.execute_script(f"document.querySelectorAll('input[id=\"rdbQuestion{i}\"]')[0].click();")

def comment():
    """Enter comments."""
    comment_box = wait.until(EC.presence_of_element_located((By.ID, 'FeedbackRating_Comments')))
    comment_box.send_keys(comments)

def submit():
    """Submit feedback."""
    submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'btnSubmit')))
    submit_button.click()

def scroll_to_top():
    """Scroll back to the top of the page."""
    driver.execute_script("window.scrollTo(0, 0);")
    sleep(1) 

def fill_feedback():
    """Fill feedback for all subjects."""
    filled_subjects = set()  

    while True:  
        try:
            # Get the list of subjects
            subjects = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'subject')))
            unfilled_feedback_found = False  

            for subj in subjects:
                sleep(1)  
                subj.click()  
                sleep(1)  

                subj_name = subj.text  
                if subj_name in filled_subjects:
                    continue  

                try:
                    # Attempt to find and click the feedback link
                    feedback_link = driver.find_element(By.CSS_SELECTOR, 
                                                        '[title="Please click here to give faculty feedback"]')
                    feedback_link.click()
                    sleep(1)  
                    fill()  
                    yesno()  
                    comment()  
                    submit()  
                    pprint(f"Feedback submitted for {subj_name}!", style='b green')
                    filled_subjects.add(subj_name)  
                    unfilled_feedback_found = True  
                    sleep(2)  

                    # Scroll to the top after submission to detect remaining subjects
                    scroll_to_top()

                except Exception as e:
                    # Log the error but continue processing the next subject
                    pprint(f"Error while processing feedback for {subj_name}: {e}", style='b red')
                    continue  

            # If no new feedback was filled during this iteration, check if we should exit
            if not unfilled_feedback_found:
                pprint("All feedbacks (if available) have been submitted!", style='b green')
                break  

        except Exception as e:
            # Log the error and continue the loop without exiting
            pprint(f"Unexpected error while processing subjects: {e}", style='b red')
            sleep(2)  

def main():
    """Main function to execute the script."""
    try:
        visit_amizone()
        verify_login()
        close_popups()
        select_my_faculty()
        fill_feedback()
    except Exception as e:
        pprint(f"An unexpected error occurred: {e}", style='b red')
    finally:
        driver.quit()
        pprint('Feedback Successfully filled! Please verify manually.', style='b green')
        pprint('[NOTE]: If some faculties are left, you can re-run the script.', style='b yellow')

if __name__ == "__main__":
    main()