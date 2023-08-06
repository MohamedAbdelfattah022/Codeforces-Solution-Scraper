import os
import csv
import re
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pyperclip


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    options.add_argument('--window-size=1920x1080')
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
    return driver


def login(driver, user_name, pass_word, attempts=0):
    try:
        codeforces_url = "https://codeforces.com/"
        driver.get(codeforces_url)

        enter_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/enter?back=%2F"]'))
        )
        enter_btn.click()

        handle_or_email = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "handleOrEmail"))
        )
        handle_or_email.clear()
        handle_or_email.send_keys(user_name)

        password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password.clear()
        password.send_keys(pass_word)

        # remember_me = WebDriverWait(driver, 10).until(
        #      EC.element_to_be_clickable((By.ID, "remember"))
        #  )
        # remember_me.click()

        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
        )
        login_btn.click()
    except Exception as e:
        print(f"an error happened while Logging in. retrying")
        if attempts < 3:
            login(driver, user_name, pass_word, attempts + 1)
        else:
            print(f"Failed to login after 3 attempts. closing program. \n{e}")
            driver.quit()
            exit(1)


def navigate_to_submissions(driver, user, attempts=0):
    try:
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
    except Exception as e:
        if attempts<3:
            print(f"an error happened while navigating to submissions. retrying...")
            navigate_to_submissions(driver, user, attempts+1)
        else:
            print(f"Failed to go to submission page. exiting")
            exit(1)


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
            time.sleep(0.25)
            return get_tags(driver, url, attempts + 1)
        else:
            print(f"Failed to get tags for URL: {url} after 3 attempts. Skipping this URL. \n{e}")
            return []


def get_problem_name(driver, url, attempts=0):
    try:
        driver.get(url)
        time.sleep(1)
        title_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="title"]'))
        )
        name = title_element.text.strip()
        return re.sub(r'[\\/:*?"<>|]', '', name)
    except Exception as e:
        if attempts < 3:
            print(f"An error occurred while getting problem name for URL: {url}. Refreshing the page and retrying.")
            driver.refresh()
            time.sleep(0.25)
            return get_problem_name(driver, url, attempts + 1)
        else:
            print(f"Failed to get problem name for URL: {url} after 3 attempts. Skipping this URL.\n{e}")
            return "None"


def get_solution_code(driver, url, attempts=0):
    try:
        time.sleep(0.25)
        last_submissions = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table[class="rtable smaller"]'))
        )
        # Get the first link (a tag)
        problem_solution_link = WebDriverWait(last_submissions, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )
        problem_solution_link.click()
        solution_code_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'pre[class="prettyprint lang-cpp linenums program-source prettyprinted"]')
            )
        )
        code = solution_code_element.text.strip()
        code = code.replace("\r", "")
        return code
    except Exception as e:
        if attempts < 3:
            print("An error occurred while getting solution code. Refreshing the page and retrying.")
            driver.refresh()
            time.sleep(15)
            driver.get(url)
            return get_solution_code(driver, url, attempts + 1)
        else:
            print(f"Failed to get solution code after 3 attempts. Skipping this submission. \n{e}")
            return "// error while getting the submission"


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
            print(f"Failed to write solution for problem '{problem_name}' to file.\n{e}")


def is_csv_empty(filename):
    return os.path.getsize(filename) == 0


def write_problem_info_to_csv_file(problem_name, link, tags_list):
    filename = 'problem_info.csv'
    rating = 0
    if tags_list and tags_list[-1].strip().startswith('*') and tags_list[-1][1:].isdigit():
        rating = int(tags_list.pop()[1:])
    header = ["Problem Name", "Problem Link", "Tags", "Rate"]
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as info_file:
            csv_writer = csv.writer(info_file)
            if is_csv_empty(filename):
                csv_writer.writerow(header)
            tags_str = ",".join(tags_list)
            csv_writer.writerow([problem_name, link, tags_str, rating])
        print(f"Problem info for '{problem_name}' written to '{filename}' successfully.")
    except Exception as e:
        print(f"Failed to write problem info for '{problem_name}' to file.\n{e}")


def write_problem_info_to_text_file(problem_name, link, tags_list):
    filename = 'problem_info.txt'
    with open(filename, 'a', encoding='utf-8') as info:
        try:
            info.write(problem_name + "\n")
            info.write(link)
            info.write("→ Problem tags\n")
            for tag in tags_list:
                info.write(tag + "\n")
            info.write("--------------\n")
        except Exception as e:
            print(f"Failed to write problem info for '{problem_name}' to file.\n{e}")


def get_submission_links(driver, number_of_problems=0):
    problem_counter = 0
    processed_links = set()
    while True:
        try:
            if number_of_problems != 0 and problem_counter == number_of_problems:
                break
            submissions_table_rows = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table[class="status-frame-datatable"'))
            ).find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
            with open('problems_links.txt', 'a', encoding='utf-8') as file:
                for row in submissions_table_rows[1:]:
                    try:
                        if number_of_problems != 0 and problem_counter == number_of_problems:
                            break
                        link_element = row.find_elements_by_tag_name('td')[3].find_element_by_tag_name('a')
                        problem_link = link_element.get_attribute('href')

                        if ("/gym/" in problem_link) or ("/edu/course/" in problem_link) or (
                                problem_link in processed_links):
                            continue

                        processed_links.add(problem_link)
                        file.write(problem_link + "\n")
                        problem_counter += 1
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
            break
        except Exception as e:
            print(f"Error occurred while fetching submissions message: {e}")
            continue


def main():
    try:
        user = input("Enter Your Handle: ")
        pass_key = input("Enter Your Password: ")
        extension = input("Enter The Extension You Want To Save The Files By: ")
        problems_option = input(
            "Enter 1 To Get All Problems"
            "\n"
            "Enter 2 To Get just Some Problems\n"
        )
        number_of_problems = 0
        if problems_option.strip() == "2":
            number_of_problems = int(input("Enter The Number Of Problems: ").strip())

        info_option = input("Choose the file format to store problems info (csv, txt): ")

        driver = initialize_driver()
        print("Logging in...")
        login(driver, user, pass_key)

        time.sleep(1)
        print("Going to submissions...")

        navigate_to_submissions(driver, user)

        print("Fetching Accepted links...")
        open('problems_links.txt', 'w').close()
        if problems_option == "2":
            get_submission_links(driver, int(number_of_problems))
        else:
            get_submission_links(driver)

        directory = create_submission_directory(user)

        with open('problems_links.txt', 'r', encoding='utf-8') as links_file:
            for link in links_file:
                tags_list = get_tags(driver, link)
                problem_name = get_problem_name(driver, link)
                print(problem_name)
                solution = get_solution_code(driver, link)
                if info_option.strip() == "csv":
                    write_problem_info_to_csv_file(problem_name, link, tags_list)
                else:
                    write_problem_info_to_text_file(problem_name, link, tags_list)
                write_solution_to_file(directory, problem_name, extension, link, solution)

        print("Task Completed")
        time.sleep(3)
        driver.quit()
    except selenium.common.exceptions.NoSuchWindowException:
        print("The browser window was closed by user.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
