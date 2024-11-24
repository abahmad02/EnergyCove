import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import datetime

def get_bill_info(reference_number):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option(
        "prefs", {
            # block image loading
            "profile.managed_default_content_settings.images": 2,
        }
    )

    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://bill.pitc.com.pk/mepcobill"
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchTextBox")))

        reference_input = driver.find_element(By.ID, "searchTextBox")
        reference_input.send_keys(reference_number)
        
        ru_code_select = driver.find_element(By.ID, "ruCodeTextBox")
        ru_code_select.send_keys('U')

        search_button = driver.find_element(By.ID, "btnSearch")
        search_button.click()

        WebDriverWait(driver, 10).until(EC.url_changes(url))

        print(f"URL after form submission: {driver.current_url}")

        subdivision = extract_subdivision(driver)

        bill_info = {
            'Name': extract_name(driver),
            'Payable Within Due Date': extract_payable_within_due_date(driver),
            'Units Consumed': extract_units_consumed(driver),
            'Issue Date': extract_issue_date(driver),
            'Due Date': extract_due_date(driver),
            'Subdivision': subdivision
        }

        # Generate the array of months
        if bill_info['Issue Date'] != "Not found":
            bill_info['Year Data'] = generate_year_data(bill_info['Issue Date'])
            bill_info['Monthly Units'] = extract_monthly_units(driver, bill_info['Year Data'])
            bill_info['Total Yearly Units'] = calculate_total_units(driver, bill_info['Monthly Units'])
            bill_info['Max Units'] = calculate_max_units(driver, bill_info['Monthly Units'])

        return bill_info

    finally:
        driver.quit()

def calculate_max_units(driver, monthly_units):
    try:
        max_units = max(int(units) for units in monthly_units.values() if units.isdigit())
        print(f"Max units: {max_units}")
        return max_units
    except Exception as e:
        print(f"Error calculating max units: {e}")
        return "Error"

def extract_name(driver):
    try:
        name_address_section = driver.find_element(By.XPATH, "//span[contains(text(), 'NAME & ADDRESS')]/following-sibling::span[1]")
        name = name_address_section.text.strip()
        return name
    except Exception as e:
        print(f"Error extracting name: {e}")
        return "Not found"

def extract_payable_within_due_date(driver):
    try:
        payable_section = driver.find_element(By.XPATH, "//td[contains(b, 'PAYABLE WITHIN DUE DATE')]/following::td[1]")
        payable_amount = payable_section.text.strip()
        return payable_amount
    except Exception as e:
        print(f"Error extracting payable amount: {e}")
        return "Not found"

def extract_solar_radiance_data(data):
    try:
        parameter_data = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        radiance_data = [(month, value) for month, value in parameter_data.items()]
        return radiance_data
    except KeyError as e:
        print(f"Key error: {e}")
        return None

def extract_units_consumed(driver):
    try:
        units_section = driver.find_element(By.XPATH, "//td[contains(b, 'UNITS CONSUMED')]/following::td[1]")
        units_consumed = units_section.text.strip()
        return units_consumed
    except Exception as e:
        print(f"Error extracting units consumed: {e}")
        return "Not found"

def extract_issue_date(driver):
    try:
        issue_date_section = driver.find_element(By.XPATH, "//table[@class='maintable']//tr[@class='content']/td[6]")
        issue_date = issue_date_section.text.strip()
        return issue_date
    except Exception as e:
        print(f"Error extracting issue date: {e}")
        return "Not found"

def extract_due_date(driver):
    try:
        due_date_section = driver.find_element(By.XPATH, "//table[@class='maintable']//tr[@class='content']/td[7]")
        due_date = due_date_section.text.strip()
        return due_date
    except Exception as e:
        print(f"Error extracting due date: {e}")
        return "Not found"

def extract_subdivision(driver):
    try:
        subdivision_section = driver.find_element(By.XPATH, "//td[h4[text()='SUB DIVISION']]/following-sibling::td")
        subdivision = subdivision_section.text.strip()
        return subdivision
    except Exception as e:
        print(f"Error extracting subdivision: {e}")
        return "Not found"

def get_nasa_power_monthly_data(lat, lon, start_date, end_date, parameters):
    url = f"https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        'latitude': lat,
        'longitude': lon,
        'start': start_date,
        'end': end_date,
        'parameters': parameters,
        'format': 'JSON',
        'community': 'RE'
    }
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None

def get_coordinates(address):
    api_key = 'AIzaSyCBteKYA9OvszQ0Q1MoUHtlPQJGdP0l-IY'
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data['results']:
            latitude = data['results'][0]['geometry']['location']['lat']
            longitude = data['results'][0]['geometry']['location']['lng']
            return latitude, longitude
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error requesting coordinates: {e}")
        return None, None

def generate_year_data(issue_date_str):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    try:
        issue_date = datetime.datetime.strptime(issue_date_str, "%d %b %y")
        start_month_index = issue_date.month - 1
        start_year = issue_date.year - 1
        year_data = []

        for i in range(12):
            month = months[(start_month_index + i) % 12]
            year = start_year if (start_month_index + i) < 12 else start_year + 1
            year_data.append(f"{month}{year % 100:02d}")

        return year_data
    except Exception as e:
        print(f"Error generating year data: {e}")
        return []

def extract_monthly_units(driver, year_data):
    try:
        monthly_units = {}
        rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'nested6')]//tr")
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 2:
                month = cells[0].text.strip()[:3] + cells[0].text.strip()[-2:]  # e.g., "Jun23"
                units = cells[1].text.strip()
                monthly_units[month] = units
        # Match with year_data
        monthly_units[year_data[-1]] = extract_units_consumed(driver)
        #print(f"Monthly units: {monthly_units}")
        return {month: monthly_units.get(month, "0") for month in year_data}
    except Exception as e:
        print(f"Error extracting monthly units: {e}")
        return {month: "0" for month in year_data}

def calculate_total_units(driver, monthly_units):
    try:
        total_units = sum(int(units) for units in monthly_units.values() if units.isdigit())
        consumed_units = extract_units_consumed(driver)
        if consumed_units.isdigit():
            total_units += int(consumed_units)
        return total_units
    except Exception as e:
        print(f"Error calculating total units: {e}")
        return "Error"

def bill_reader(reference_number):
    bill_info = get_bill_info(reference_number)
    print(bill_info)
    print("Done")
    return(bill_info)
    # Call the function from invoicemaker.py
    # create_invoice_from_bill_info(bill_info)

if __name__ == '__main__':
    reference_number = '04151722337322'  # Replace with the actual reference number
    bill_reader(reference_number)
