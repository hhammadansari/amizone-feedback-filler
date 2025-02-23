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
    max_attempts = 5
    for _ in range(max_attempts):
        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, '.close, [data-dismiss="modal"], .modal-close')
            overlays = driver.find_elements(By.CSS_SELECTOR, '.modal-backdrop.fade.in')
            
            if not close_buttons and not overlays:
                break

            for btn in close_buttons:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    pprint(f"🗙 Closed popup: {btn.text[:20]}...", style='b yellow')
                    sleep(0.5)
                except:
                    continue

            # Remove modal backdrops
            for overlay in overlays:
                driver.execute_script("arguments[0].remove();", overlay)

            sleep(1)  # Allow new popups to appear

        except Exception as e:
            pprint(f"Popup error: {str(e)}", style='b red')
            break

    try:
        driver.execute_script("""
            document.querySelectorAll('.modal-backdrop').forEach(e => e.remove());
            document.querySelectorAll('.modal').forEach(e => e.remove());
        """)
    except:
        pass

    pprint("All popups cleared!", style='b green')

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
    """Answer all yes/no questions (4 questions)."""
    question_ids = [1, 2, 4, 5]
    for q_id in question_ids:
        try:
            script = f"""
                var radios = document.querySelectorAll('input[id="rdbQuestion{q_id}"][value="1"]');
                if (radios.length > 0) radios[0].click();
            """
            driver.execute_script(script)
            sleep(0.5)
        except Exception as e:
            pprint(f"Error answering question {q_id}: {e}", style='b red')

def comment():
    try:
        comment_box = wait.until(EC.element_to_be_clickable((By.ID, 'FeedbackRating_Comments')))
        comment_box.clear()
        comment_box.send_keys(comments)
        sleep(0.5)
    except Exception as e:
        pprint(f"Error filling comments: {e}", style='b red')

def submit():
    """Submit feedback and wait for confirmation."""
    try:
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'btnSubmit')))
        submit_button.click()
        wait.until(EC.invisibility_of_element_located((By.ID, 'btnSubmit')))
        sleep(2)
    except Exception as e:
        pprint(f"Error submitting feedback: {e}", style='b red')

def scroll_to_top():
    driver.execute_script("window.scrollTo(0, 0);")
    sleep(1) 

def fill_feedback():
    """Fill feedback for all subjects."""
    filled_subjects = set()

    while True:
        try:
            subjects = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'subject')))
            unfilled_feedback_found = False

            for index in range(len(subjects)):
                try:
                    # Re-fetch subject element each time
                    current_subj = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'subject')))[index]
                    subj_name = current_subj.text
                    
                    if subj_name in filled_subjects:
                        continue

                    current_subj.click()
                    sleep(1)

                    try:
                        feedback_link = wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, '[title="Please click here to give faculty feedback"]')
                        ))
                        feedback_link.click()
                        sleep(2)

                        # Fill the feedback
                        fill()
                        yesno()
                        comment()
                        submit()
                        
                        pprint(f"Feedback submitted for {subj_name}!", style='b green')
                        filled_subjects.add(subj_name)
                        unfilled_feedback_found = True
                        
                        select_my_faculty()
                        sleep(2)
                        scroll_to_top()

                    except Exception as e:
                        pprint(f"Error processing {subj_name}: {str(e)}", style='b red')
                        continue

                except Exception as e:
                    pprint(f"Error accessing subject {index}: {str(e)}", style='b red')
                    continue

            if not unfilled_feedback_found:
                pprint("All feedback submitted successfully!", style='b green')
                break

        except Exception as e:
            pprint(f"Error in main loop: {str(e)}", style='b red')
            sleep(2)
            break
        
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