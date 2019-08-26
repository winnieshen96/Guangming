# Guangming
Web-crawling Guangming Daily

* This is a project dedicated to crawl the articles of Guangming Daily for textual analysis.

* The project began in April, 2018, and has been improved by me from time to time.

# Usage

1. Download the guangming.py file.

2. Run Configuration: Install requests, beautifulsoup4, pandas

   If you don't have pip, follow the instructions on https://pip.pypa.io/en/stable/installing/ to install pip on your computer.

   After you have pip, type in the following commands in cmd to install these packages.
   pip install requests
   pip install beautifulsoup4
   pip install pandas

   If you are choosing pycharm to run guangming.py, the latest version of pycharm can intelligently set up the installing process for you.

3. Run guangming.py, input in the info as required by the program.

4. That's it! The program will scrape the information from Guangming Daily according to your input.

# Update Log 08/25/2019

Recent added features include:

1. Improved the efficiency of writing file, taking less memory while running.

2. Developed an interface to get the following input from user.
   Ask the user to input date range, instead of making the date range embedded in the code.
   Ask the user to input the gap time for each crawl, adding flexibility to the crawling process.
   Ask the user to input the path they want, and create the path for the user, avoiding "DirectoryNotFound" errors.
