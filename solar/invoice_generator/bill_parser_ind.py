import datetime
from bs4 import BeautifulSoup

def generate_year_data(issue_date_str):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    try:
        # Parse the issue date. Example: "11 NOV 24"
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

def extract_monthly_units(soup, year_data):
    try:
        # Locate all tables and find the one containing the monthly data
        tables = soup.find_all("table")
        target_table = None
        
        for table in tables:
            headers = [td.get_text(strip=True).upper() for td in table.find_all("td")]
            #print(f"Headers found: {headers}")  # Debug: Print headers to verify structure
            
            # Check if the table has months and KWH UNITS columns
            if "MONTH" in headers and "KWH UNITS" in headers:
                target_table = table
                break

        if not target_table:
            #print("Monthly units table not found.")
            return {month: "0" for month in year_data}

        # Extract rows from the table
        rows = target_table.find_all("tr")
        monthly_units = {}

        # Debugging: Print all rows to understand the table structure
        #print("Table rows:")
        #for row in rows:
            #print([td.get_text(strip=True) for td in row.find_all("td")])

        # Iterate over the rows (skip the header row)
        for row in rows[1:]:
            cells = row.find_all("td")
            # Check if the row has the expected number of columns (MONTH, MDI, KWH UNITS, etc.)
            if len(cells) >= 3:
                # Extract the month column (0th index)
                month_text = cells[0].get_text(strip=True).upper()
                if len(month_text) >= 5:  # Check if month is in the expected format (e.g., Nov23)
                    # Normalize month format (e.g., NOV23 becomes Nov23)
                    month = month_text[:3].capitalize() + month_text[-2:]

                    # Now find the index of the month in year_data
                    if month in year_data:
                        month_index = year_data.index(month)
                        
                        # Extract the corresponding KWH UNITS (2 columns after the month)
                        if len(cells) > 2:
                            units = cells[2].get_text(strip=True)
                            monthly_units[month] = units if units.isdigit() else "0"

        print(f"Extracted Monthly Units: {monthly_units}")

        # Ensure all months in year_data are covered
        return {month: monthly_units.get(month, "0") for month in year_data}
    
    except Exception as e:
        print(f"Error extracting monthly units: {e}")
        return {month: "0" for month in year_data}



def parse_electricity_bill_industrial(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    name_section = soup.find(string=lambda s: "NAME & ADDRESS" in s if s else False)
    name = name_section.find_next("td").get_text(strip=True).replace("\n", "") if name_section else "Not Found"

    print(f"Name extracted: {name}")

    # Extract Payable Within Due Date
    payable_due_date = "Not Found"
    payable_section = soup.find(string=lambda s: "PAYABLE WITHIN DUE DATE" in s if s else False)
    if payable_section:
        parent_td = payable_section.find_parent("td")
        if parent_td:
            payable_due_date = parent_td.find_next_sibling("td").get_text(strip=True)
    else:
        print("Payable Within Due Date section not found")

    print(f"Payable Within Due Date extracted: {payable_due_date}")

    # Extract Units Consumed (Current month)
    units_consumed = "Not Found"
    units_section = soup.find(string=lambda s: "UNITS CONSUMED" in s if s else False)
    if units_section:
        # The units consumed is in 'b' tag inside the 'td'
        parent_td = units_section.find_parent("td")
        if parent_td:
            b_tag = parent_td.find("b")
            if b_tag:
                units_consumed = b_tag.get_text(strip=True)
    else:
        print("Units Consumed section not found")

    print(f"Units Consumed extracted: {units_consumed}")

    # Locate the header row containing "ISSUE DATE" and "DUE DATE"
    issue_date = "Not Found"
    due_date = "Not Found"
    header_row = None
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        texts = [td.get_text(strip=True).upper() for td in tds]
        if "ISSUE DATE" in texts and "DUE DATE" in texts:
            header_row = tr
            print(f"Header row found: {texts}")
            break

    if header_row:
        data_row = header_row.find_next_sibling("tr")
        if data_row:
            data_tds = data_row.find_all("td")
            header_texts = [td.get_text(strip=True).upper() for td in header_row.find_all("td")]
            try:
                issue_idx = header_texts.index("ISSUE DATE")
                due_idx = header_texts.index("DUE DATE")
                if len(data_tds) > due_idx:
                    issue_date = data_tds[issue_idx].get_text(strip=True)
                    due_date = data_tds[due_idx].get_text(strip=True)
            except ValueError as e:
                print(f"Error finding column indices: {e}")
    else:
        print("Header row with ISSUE DATE and DUE DATE not found")


    print(f"Issue Date extracted: {issue_date}, Due Date extracted: {due_date}")

    # Extract Subdivision
    subdivision = "Not Found"
    subdivision_section = soup.find(string=lambda s: "SUB DIVISION" in s if s else False)
    if subdivision_section:
        parent_td = subdivision_section.find_parent("td")
        if parent_td:
            subdivision = parent_td.find_next_sibling("td").get_text(strip=True)
    else:
        print("Subdivision section not found")

    print(f"Subdivision extracted: {subdivision}")

    # Generate Year Data
    year_data = generate_year_data(issue_date)
    print(f"Year Data generated: {year_data}")

    # Extract Monthly Units
    monthly_units = extract_monthly_units(soup, year_data)

    # Extract Total Yearly Units and Max Units
    try:
        total_yearly_units = sum(int(units) for units in monthly_units.values())
    except ValueError as e:
        print(f"Error converting units to int: {e}")
        total_yearly_units = 0

    try:
        max_units = max(int(units) for units in monthly_units.values()) if monthly_units else 0
    except ValueError as e:
        print(f"Error converting units to int: {e}")
        max_units = 0
    except Exception as e:
        print(f"Error calculating max units: {e}")
        max_units = 0

    # Construct the result
    result = {
        "Name": name,
        "Payable Within Due Date": payable_due_date,
        "Units Consumed": units_consumed,
        "Issue Date": issue_date,
        "Due Date": due_date,
        "Monthly Units": monthly_units,
        "Total Yearly Units": total_yearly_units,
        "Max Units": max_units,
    }

    return result

# Example Usage:
if __name__ == "__main__":
    with open("text.txt", "r", encoding="utf-8") as file:
        html_content = file.read()
    result = parse_electricity_bill(html_content)
    print(result)
