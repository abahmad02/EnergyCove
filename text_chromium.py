from selenium import webdriver

# Since ChromeDriver is in the system's PATH, no need to specify the path
driver = webdriver.Chrome()

# Example of opening a webpage
driver.get("https://www.google.com")
