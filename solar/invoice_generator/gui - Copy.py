import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from invoicemaker import generate_invoice


def generate_pdf():
    # Check if name, address, or contact fields are empty
    if not Name_entry.get().strip() or not Address_entry.get().strip() or not Contact_entry.get().strip():
        messagebox.showerror("Input Error", "Please ensure that Name, Address, and Contact fields are filled out.")
        return  # Stop execution if any of these fields are empty
    
    try:
        # Get the values from the entry fields in the right frame
        panel_quant = int(Panel_Count_entry.get())
        panel_cost = float(PV_Panel_entry.get())
        Inverter_cost = float(Inverter_entry.get())
        inverter_brand = selected_brand.get()
        frame_cost = float(Frame_entry.get())
        cable_cost = float(Cable_entry.get())
        balance_cost = float(Balance_entry.get())
        installation_cost = float(Installation_entry.get())
        net_metering_cost = float(Net_Metering_entry.get())
        panel_power = float(panel_watt_entry.get())
        system_size = float(system_size_entry.get()) * 1000
        pricePerWatt = float(price_per_watt_entry.get())
        total_price = pricePerWatt * system_size
        customerName = Name_entry.get().strip()
        customerAddress = Address_entry.get().strip()
        customerContact = Contact_entry.get().strip()

        # Success message before generating the invoice
        messagebox.showinfo("Success", "Invoice is generating and will open soon. Press OK to continue. Invoice will be saved in the Documents folder.")
        
        # Function call to generate invoice
        generate_invoice(system_size, panel_quant, panel_power, Inverter_cost, inverter_brand, panel_cost, net_metering_cost, installation_cost, cable_cost, frame_cost, balance_cost, total_price, customerName, customerAddress, customerContact)
    
    except ValueError as e:
        # This captures errors related to invalid numerical input
        messagebox.showerror("Input Error", "Please ensure all fields are filled out correctly with appropriate numbers.")
        return  # Stop execution if conversion fails


def calculate_cost():
    try:
        pricePerWatt = int(price_per_watt_entry.get())
        system_size = int(system_size_entry.get()) * 1000
        panel_watt = int(panel_watt_entry.get())
        number_panels = round(system_size / panel_watt)
        Price_per_watt_panels = int(price_per_watt_panels_entry.get())
        price_per_panel = panel_watt * Price_per_watt_panels
        total_panel_cost = number_panels * price_per_panel
        inverter_brand = selected_brand.get()
        inverter_count = int(inverter_count_entry.get())
        inverter_cost = int(inverter_cost_entry.get())
        labor_cost = int(labor_cost_entry.get()) * system_size
        num_frames = round(number_panels / 2)
        frame_per_watt = int(frame_per_watt_entry.get())
        total_cost_frame = system_size * frame_per_watt
        net_metering_cost = int(net_metering_cost_entry.get())

        # Print variable values before calculations
        print("Before Calculations:")
        print(f"Price per Watt: {pricePerWatt}")
        print(f"System Size: {system_size}")
        print(f"Panel Watt: {panel_watt}")
        print(f"Number of Panels: {number_panels}")
        print(f"Price per Watt (Panels): {Price_per_watt_panels}")
        print(f"Price per Panel: {price_per_panel}")
        print(f"Inverter Brand: {inverter_brand}")
        print(f"Inverter Count: {inverter_count}")
        print(f"Inverter Cost: {inverter_cost}")
        print(f"Labor Cost: {labor_cost}")
        print(f"Number of Frames: {num_frames}")
        print(f"Frame per Watt: {frame_per_watt}")
        print(f"Net Metering Cost: {net_metering_cost}")

        # Calculate the total cost
        total_cost = total_cost_frame + total_panel_cost + (inverter_cost * inverter_count) + labor_cost + net_metering_cost
        Price_quoted = pricePerWatt * system_size
        cost_of_material = Price_quoted - total_cost

        # Print variable values after calculations
        print("\nAfter Calculations:")
        print(f"Total Panel Cost: {total_panel_cost}")
        print(f"Total Cost of Frame: {total_cost_frame}")
        print(f"Total Cost: {total_cost}")
        print(f"Price Quoted: {Price_quoted}")
        print(f"Cost of Material: {cost_of_material}")

        # Update the result labels
        price_quoted_result.configure(text=f"Price Quoted: {Price_quoted} PKR")
        total_cost_result.configure(text=f"Total Cost: {cost_of_material} PKR")
        PV_Panel_entry.delete(0, "end")  # Clear existing text
        PV_Panel_entry.insert(0, total_panel_cost)
        Panel_Count_entry.delete(0, "end")  # Clear existing text
        Panel_Count_entry.insert(0, number_panels)
        Inverter_entry.delete(0, "end")  # Clear existing text
        Inverter_entry.insert(0, inverter_cost * inverter_count)
        Frame_entry.delete(0, "end")  # Clear existing text
        Frame_entry.insert(0, total_cost_frame)
        Net_Metering_entry.delete(0, "end")  # Clear existing text
        Net_Metering_entry.insert(0, net_metering_cost)
    except ValueError as e:
        messagebox.showerror("Input Error", "Please ensure all fields are filled out correctly.")
        return  # Stop execution of the rest of this function



# Create the GUI window
ctk.set_appearance_mode("light")
# Create the main window
window = ctk.CTk()
window.title("SolarCove Solar Panel Cost Calculator")

# Create the left frame (Calculator)
left_frame = ctk.CTkFrame(window)
left_frame.grid(row=0, column=0, padx=15, pady=10, sticky="w")

# Title for the left frame
left_frame_title = ctk.CTkLabel(left_frame, text="Calculator", font=("Helvetica", 20, "bold"))
left_frame_title.grid(row=0, column=0, columnspan=2, pady=10, padx=15)

# Function to dynamically create entry fields
def create_entry_field(frame, label, row, column=0, padx=15, pady=10, width=200):
    lbl = ctk.CTkLabel(frame, text=label)
    lbl.grid(row=row, column=column, padx=padx, pady=pady, sticky="w")
    entry = ctk.CTkEntry(frame, width=width)
    entry.grid(row=row, column=column+1, padx=padx, pady=pady, sticky="w")
    return entry

# Create input labels and entry fields in the left frame using the helper function
price_per_watt_entry = create_entry_field(left_frame, "Estimate per watt:", 1)
system_size_entry = create_entry_field(left_frame, "System Size (KW):", 2)
panel_watt_entry = create_entry_field(left_frame, "Panel Wattage:", 3)
price_per_watt_panels_entry = create_entry_field(left_frame, "Price per watt (panels):", 4)
inverter_count_entry = create_entry_field(left_frame, "Inverter Count:", 6)
inverter_cost_entry = create_entry_field(left_frame, "Inverter Cost:", 7)
labor_cost_entry = create_entry_field(left_frame, "Labor Cost:", 8)
frame_per_watt_entry = create_entry_field(left_frame, "Frame per Watt:", 9)
net_metering_cost_entry = create_entry_field(left_frame, "Net Metering Cost:", 10)

# Dropdown for Inverter Brand
inverter_brand_label = ctk.CTkLabel(left_frame, text="Inverter Brand:")
inverter_brand_label.grid(row=5, column=0, padx=15, pady=10, sticky="w")

inverter_brands = ["Brand A", "Brand B", "Brand C"]
selected_brand = ctk.StringVar(value=inverter_brands[0])

inverter_brand_dropdown = ctk.CTkComboBox(left_frame, values=inverter_brands)
inverter_brand_dropdown.grid(row=5, column=1, padx=15, pady=10, sticky="w")
price_quoted_result = ctk.CTkLabel(left_frame, text="Price Quoted:")
price_quoted_result.grid(row=11, column=0, padx=15, pady=10, sticky="w")

total_cost_result = ctk.CTkLabel(left_frame, text="Total Cost:")
total_cost_result.grid(row=12, column=0, padx=15, pady=10, sticky="w")
# Create a button to calculate the cost
calculate_button = ctk.CTkButton(left_frame, text="Calculate", command=calculate_cost)
calculate_button.grid(row=13, column=0, columnspan=2, padx=15, pady=10, sticky="w")
# Create the right frame (Preview)
right_frame = ctk.CTkFrame(window)
right_frame.grid(row=0, column=1, padx=15, pady=10, sticky="w")

# Title for the right frame
right_frame_title = ctk.CTkLabel(right_frame, text="Generate PDF", font=("Helvetica", 20, "bold"))
right_frame_title.grid(row=0, column=0, columnspan=2, pady=10, padx=15)

PV_Panel_label = ctk.CTkLabel(right_frame, text="PV Panels cost:")
PV_Panel_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
PV_Panel_entry = ctk.CTkEntry(right_frame, width=200)
PV_Panel_entry.grid(row=1, column=1, padx=15, pady=10, sticky="w")

Panel_Count_label = ctk.CTkLabel(right_frame, text="Panel Quantity:")
Panel_Count_label.grid(row=2, column=0, padx=15, pady=10, sticky="w")
Panel_Count_entry = ctk.CTkEntry(right_frame, width=200)
Panel_Count_entry.grid(row=2, column=1, padx=15, pady=10, sticky="w")

Inverter_label = ctk.CTkLabel(right_frame, text="Inverter & Accessories:")
Inverter_label.grid(row=3, column=0, padx=15, pady=10, sticky="w")
Inverter_entry = ctk.CTkEntry(right_frame, width=200)
Inverter_entry.grid(row=3, column=1, padx=15, pady=10, sticky="w")

Frame_label = ctk.CTkLabel(right_frame, text="PV Panels Structure / Frame:")
Frame_label.grid(row=4, column=0, padx=15, pady=10, sticky="w")
Frame_entry = ctk.CTkEntry(right_frame, width=200)
Frame_entry.grid(row=4, column=1, padx=15, pady=10, sticky="w")

Cable_label = ctk.CTkLabel(right_frame, text="DC / AC Cable & Accessories:")
Cable_label.grid(row=5, column=0, padx=15, pady=10, sticky="w")
Cable_entry = ctk.CTkEntry(right_frame, width=200)
Cable_entry.grid(row=5, column=1, padx=15, pady=10, sticky="w")

Balance_label = ctk.CTkLabel(right_frame, text="Balance of System:")
Balance_label.grid(row=6, column=0, padx=15, pady=10, sticky="w")
Balance_entry = ctk.CTkEntry(right_frame, width=200)
Balance_entry.grid(row=6, column=1, padx=15, pady=10, sticky="w")

Installation_label = ctk.CTkLabel(right_frame, text="Installation & Commissioning:")
Installation_label.grid(row=7, column=0, padx=15, pady=10, sticky="w")
Installation_entry = ctk.CTkEntry(right_frame, width=200)
Installation_entry.grid(row=7, column=1, padx=15, pady=10, sticky="w")

Net_Metering_label = ctk.CTkLabel(right_frame, text="Net Metering Cost:")
Net_Metering_label.grid(row=8, column=0, padx=15, pady=10, sticky="w")
Net_Metering_entry = ctk.CTkEntry(right_frame, width=200)
Net_Metering_entry.grid(row=8, column=1, padx=15, pady=10, sticky="w")

Name_label = ctk.CTkLabel(right_frame, text="Customer Name:")
Name_label.grid(row=9, column=0, padx=15, pady=10, sticky="w")
Name_entry = ctk.CTkEntry(right_frame, width=200)
Name_entry.grid(row=9, column=1, padx=15, pady=10, sticky="w")

Address_label = ctk.CTkLabel(right_frame, text="Customer Address:")
Address_label.grid(row=10, column=0, padx=15, pady=10, sticky="w")
Address_entry = ctk.CTkEntry(right_frame, width=200)
Address_entry.grid(row=10, column=1, padx=15, pady=10, sticky="w")

Contact_label = ctk.CTkLabel(right_frame, text="Customer Contact:")
Contact_label.grid(row=11, column=0, padx=15, pady=10, sticky="w")
Contact_entry = ctk.CTkEntry(right_frame, width=200)
Contact_entry.grid(row=11, column=1, padx=15, pady=10, sticky="w")

gen_pdf = ctk.CTkButton(right_frame, text="Generate Quote", command=generate_pdf)
gen_pdf.grid(row=13, column=0, padx=15, pady=10, sticky="w")

window.mainloop()