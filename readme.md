## Codeforces Solution Scraper

### Description:
This project is a Python script that allows users to download their Codeforces submissions along with problem information. It uses Selenium to interact with the Codeforces website and fetches the accepted submissions of a user. The script saves the solutions to individual files and records problem information in a csv file.

### Requirements:
- Python
- Chromedriver (included in the project directory)
- selenium, pyperclip modules

### Installation:
1. Ensure that the Chromedriver executable is present in the project directory.
2. Double-click the `Required_Modules.bat` batch file in the project directory. This batch file will install the required Python modules.
3. If there is an installation error, try running the batch file using a virtual environment and then retry installing the modules.

### Inspiration:
This project is inspired by the repository created by [Mohak](https://github.com/mohakkhowal/CFdownloader) thanks to him.

### How to Use:
1. Open the script in your IDE or text editor and run the script.

### Program Execution:
1. The script will prompt you to enter your Codeforces handle and password.
2. Enter the file extension (e.g., cpp, py, java) for the code files to be saved with.
3. The script will automatically log in to your Codeforces account and fetch your accepted submissions.
4. The solutions will be saved in a directory named "<your_handle>_Submissions" within the project directory.
5. Problem information, including tags, will be recorded in the "problem_info.csv" file in the project directory.

### Note:
1. The `chromedriver.exe` file is present in the project directory. This file is required for Selenium to automate the Chrome browser (version `115.0.5790.110`). If your version is different, please download the compatible driver for your version.You can download it from the [ChromeDriver website](https://sites.google.com/chromium.org/driver/).
2. The script may take some time to fetch and download all your submissions, depending on the number of submissions you have.
3. Regarding the file extension just type the extension name without '`.`' (e.g., `cpp`) and not (e.g., `.cpp`).

### Disclaimer:
This project is intended for educational purposes only. Use it on your responsibility and consider the Codeforces terms of service before using this script. I am not responsible for any misuse of this script.