import os
import csv
import re
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip


def initialize_driver(chromedriver_path):
    current_directory = os.getcwd()
    chromedriver_path = os.path.join(current_directory, "chromedriver.exe")
    os.environ["PATH"] += os.pathsep + os.path.dirname(chromedriver_path)

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    return driver


def login(driver, user_name, pass_word):
    codeforces_url = "https://codeforces.com/"
    driver.get(codeforces_url)

    enter_btn = driver.find_element_by_css_selector('a[href="/enter?back=%2F"]')
    enter_btn.click()

    handle_or_email = driver.find_element_by_id("handleOrEmail")
    handle_or_email.clear()
    handle_or_email.send_keys(user_name)

    password = driver.find_element_by_id("password")
    password.clear()
    password.send_keys(pass_word)

    # remember_me = driver.find_element_by_id("remember")
    # remember_me.click()

    login_btn = driver.find_element_by_css_selector('input[type="submit"]')
    login_btn.click()


def navigate_to_submissions(driver, user):
    enter_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[href="/profile/{user}"'))
    )
    enter_btn.click()

    submissions_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[href="/submissions/{user}"]'))
    )
    submissions_btn.click()

    accepted_filter = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'option[value="OK"]'))
    )
    accepted_filter.click()

    apply = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
    )
    apply.click()


def get_tags(driver, url, attempts=0):
    try:
        driver.get(url)
        time.sleep(3)
        tag_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span[class="tag-box"]'))
        )
        problem_tags = [tag.text.strip() for tag in tag_elements]
        return problem_tags
    except Exception as e:
        if attempts < 3:
            print(f"An error occurred while getting tags for URL: {url}. Refreshing the page and retrying.")
            driver.refresh()
            time.sleep(2)
            return get_tags(driver, url, attempts + 1)
        else:
            print(f"Failed to get tags for URL: {url} after 3 attempts. Skipping this URL.")
            return []


def get_problem_name(driver, url, attempts=0):
    try:
        driver.get(url)
        time.sleep(3)
        title_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="title"]'))
        )
        name = title_element.text.strip()
        return re.sub(r'[\\/:*?"<>|]', '', name)
    except Exception as e:
        if attempts < 3:
            print(f"An error occurred while getting problem name for URL: {url}. Refreshing the page and retrying.")
            driver.refresh()
            time.sleep(2)
            return get_problem_name(driver, url, attempts + 1)
        else:
            print(f"Failed to get problem name for URL: {url} after 3 attempts. Skipping this URL.")
            return None


def get_solution_code(driver, attempts=0):
    try:
        last_submissions = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table[class="rtable smaller"]'))
        )
        # Get the first link (a tag)
        problem_solution_link = WebDriverWait(last_submissions, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )
        problem_solution_link.click()
        copy_btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.source-copier'))
        )
        copy_btn.click()
        code = pyperclip.paste()
        code = code.replace("\r", "")
        return code
    except Exception as e:
        if attempts < 3:
            print("An error occurred while getting solution code. Refreshing the page and retrying.")
            driver.refresh()
            time.sleep(2)
            return get_solution_code(driver, attempts + 1)
        else:
            print("Failed to get solution code after 3 attempts. Skipping this submission.")
            return None


def create_submission_directory(user):
    directory = f'{user}_Submissions/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def write_solution_to_file(directory, problem_name, extension, link, solution):
    filename = f'{directory}{problem_name}.{extension}'
    with open(filename, 'w', encoding='utf-8') as file:
        try:
            file.write("// " + link + "\n")
            file.write(solution)
            print(f"File '{problem_name}' created successfully in '{directory}' directory.")
        except Exception as e:
            print(f"Failed to write solution for problem '{problem_name}' to file.")


def write_problem_info_to_file(problem_name, link, tags_list):
    filename = 'problem_info.csv'
    rating = None

    if tags_list and tags_list[-1].isdigit():
        rating = int(tags_list.pop())

    try:
        with open(filename, 'a', newline='', encoding='utf-8') as info_file:
            csv_writer = csv.writer(info_file)
            row_data = [problem_name, link] + tags_list + [rating]
            csv_writer.writerow(row_data)
        print(f"Problem info for '{problem_name}' written to '{filename}' successfully.")
    except Exception as e:
        print(f"Failed to write problem info for '{problem_name}' to file.")


# uncomment this and comment the above function if you want to save the info just in a simple text file 
# def write_problem_info_to_file(problem_name, link, tags_list):
#     filename = 'problem_info.txt'
#     with open(filename, 'a', encoding='utf-8') as info:
#         try:
#             info.write(problem_name + "\n")
#             info.write(link + "\n")
#             info.write("→ Problem tags\n")
#             for tag in tags_list:
#                 info.write(tag + "\n")
#             info.write("--------------\n")
#         except Exception as e:
#             print(f"Failed to write problem info for '{problem_name}' to file.")


def get_submission_links(driver):
    while True:
        try:
            submissions_table_rows = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table[class="status-frame-datatable"'))
            ).find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
            with open('problems_links.txt', 'a', encoding='utf-8') as file:
                for row in submissions_table_rows[1:]:
                    try:
                        link_element = row.find_elements_by_tag_name('td')[3].find_element_by_tag_name('a')
                        problem_link = link_element.get_attribute('href')
                        if ("/gym/" in problem_link) or ("/edu/course/" in problem_link):
                            continue
                        file.write(problem_link + "\n")
                    except Exception:
                        continue
            file.close()
            try:
                driver.find_element_by_link_text('→').click()
                time.sleep(2)
            except Exception:
                print("No More Pages\n")
                break
        except selenium.common.exceptions.NoSuchWindowException:
            print("The browser window was closed by user.")
        except Exception:
            print("Error occurred while fetching submissions")
            continue


def main():
    user = input("Enter Your Handle: ")
    pass_key = input("Enter Your Password: ")
    extension = input("Enter The Extension You Want To Save The Files By: ")

    chromedriver_path = "chromedriver.exe"
    driver = initialize_driver(chromedriver_path)

    login(driver, user, pass_key)

    time.sleep(1)

    navigate_to_submissions(driver, user)

    get_submission_links(driver)

    directory = create_submission_directory(user)

    with open('problems_links.txt', 'r', encoding='utf-8') as links_file:
        for link in links_file:
            tags_list = get_tags(driver, link)
            problem_name = get_problem_name(driver, link)
            print(problem_name)
            solution = get_solution_code(driver)

            write_solution_to_file(directory, problem_name, extension, link, solution)
            write_problem_info_to_file(problem_name, link, tags_list)

    print("Task Completed")
    time.sleep(3)
    driver.quit()


if __name__ == "__main__":
    try:
        main()
    except selenium.common.exceptions.NoSuchWindowException:
        print("The browser window was closed by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
