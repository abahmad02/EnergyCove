import customtkinter as ctk
from invoicemaker import generate_invoice


def generate_pdf():
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
    customerName = Name_entry.get()
    customerAddress = Address_entry.get()
    customerContact = Contact_entry.get()

    generate_invoice(system_size, panel_quant, panel_power, Inverter_cost, inverter_brand, panel_cost, net_metering_cost, installation_cost, cable_cost, frame_cost, balance_cost, total_price, customerName, customerAddress, customerContact)


def calculate_cost():
    pricePerWatt = int(price_per_watt_entry.get())
    system_size = int(system_size_entry.get()) * 1000
    # Calculations for system sizing
    # The Yearly average units are calculated using the history of units in the bill
   ''' yearly_units_average = 15000  # this will be calculated from the history of the bill
    system_size_kw = (yearly_units_average / 365) / 4  # In Pakistan, 1 kW produces around 4 units
    system_size_recommended = system_size_kw * 1.3  # 40% bump to provided recommended
    system_size_larger = system_size_kw * 1.6  # 60% bump to provided recommended
    system_size_recommended = math.ceil(system_size_recommended)
    system_size_larger = math.ceil(system_size_larger)
    '''


    
    # This wattage is based on the wattage based in inventory of panels
    panel_watt = int(panel_watt_entry.get()) 
    number_panels = round(system_size / panel_watt)
    # Manual input from company side panel
    Price_per_watt_panels = int(price_per_watt_panels_entry.get())

    price_per_panel = panel_watt * Price_per_watt_panels
    total_panel_cost = number_panels * price_per_panel
    # These will be based on inventory from company side
    inverter_brand = selected_brand.get()
    # This inverter Count will be done based on system sizing automatically
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




# Create the GUI window
ctk.set_appearance_mode("light")
window = ctk.CTk()
window.title("Solar System Quotation")

# Create the left frame (Calculator)
left_frame = ctk.CTkFrame(window)
left_frame.grid(row=0, column=0, padx=15, pady=10, sticky="w")

# Title for the left frame
left_frame_title = ctk.CTkLabel(left_frame, text="Calculator", font=("Helvetica", 20, "bold"))
left_frame_title.grid(row=0, column=0, columnspan=2, pady=10, padx=15)

# Create input labels and entry fields in the left frame
price_per_watt_label = ctk.CTkLabel(left_frame, text="Estimate per watt:")
price_per_watt_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
price_per_watt_entry = ctk.CTkEntry(left_frame, width=200)
price_per_watt_entry.grid(row=1, column=1, padx=15, pady=10, sticky="w")

system_size_label = ctk.CTkLabel(left_frame, text="System Size (KW):")
system_size_label.grid(row=2, column=0, padx=15, pady=10, sticky="w")
system_size_entry = ctk.CTkEntry(left_frame, width=200)
system_size_entry.grid(row=2, column=1, padx=15, pady=10, sticky="w")

panel_watt_label = ctk.CTkLabel(left_frame, text="Panel Wattage:")
panel_watt_label.grid(row=3, column=0, padx=15, pady=10, sticky="w")
panel_watt_entry = ctk.CTkEntry(left_frame, width=200)
panel_watt_entry.grid(row=3, column=1, padx=15, pady=10, sticky="w")

# Add more input labels and entry fields for the remaining variables
price_per_watt_panels_label = ctk.CTkLabel(left_frame, text="Price per watt (panels):")
price_per_watt_panels_label.grid(row=4, column=0, padx=15, pady=10, sticky="w")
price_per_watt_panels_entry = ctk.CTkEntry(left_frame, width=200)
price_per_watt_panels_entry.grid(row=4, column=1, padx=15, pady=10, sticky="w")

inverter_brand_label = ctk.CTkLabel(left_frame, text="Inverter Brand:")
inverter_brand_label.grid(row=5, column=0, padx=15, pady=10, sticky="w")

# Create a dropdown menu (Combobox) for inverter brands
inverter_brands = ["Brand A", "Brand B", "Brand C"]  # Replace with your actual inverter brands
selected_brand = ctk.StringVar()
selected_brand.set(inverter_brands[0])  # Set default selection

inverter_brand_dropdown = ctk.CTkComboBox(left_frame, values=inverter_brands)
inverter_brand_dropdown.grid(row=5, column=1, padx=15, pady=10, sticky="w")
inverter_brand_dropdown.configure(variable=selected_brand, width=200)

inverter_count_label = ctk.CTkLabel(left_frame, text="Inverter Count:")
inverter_count_label.grid(row=6, column=0, padx=15, pady=10, sticky="w")
inverter_count_entry = ctk.CTkEntry(left_frame, width=200)
inverter_count_entry.grid(row=6, column=1, padx=15, pady=10, sticky="w")

inverter_cost_label = ctk.CTkLabel(left_frame, text="Inverter Cost:")
inverter_cost_label.grid(row=7, column=0, padx=15, pady=10, sticky="w")
inverter_cost_entry = ctk.CTkEntry(left_frame, width=200)
inverter_cost_entry.grid(row=7, column=1, padx=15, pady=10, sticky="w")

labor_cost_label = ctk.CTkLabel(left_frame, text="Labor Cost:")
labor_cost_label.grid(row=8, column=0, padx=15, pady=10, sticky="w")
labor_cost_entry = ctk.CTkEntry(left_frame, width=200)
labor_cost_entry.grid(row=8, column=1, padx=15, pady=10, sticky="w")

frame_per_watt_label = ctk.CTkLabel(left_frame, text="Frame per Watt:")
frame_per_watt_label.grid(row=9, column=0, padx=15, pady=10, sticky="w")
frame_per_watt_entry = ctk.CTkEntry(left_frame, width=200)
frame_per_watt_entry.grid(row=9, column=1, padx=15, pady=10, sticky="w")

net_metering_cost_label = ctk.CTkLabel(left_frame, text="Net Metering Cost:")
net_metering_cost_label.grid(row=10, column=0, padx=15, pady=10, sticky="w")
net_metering_cost_entry = ctk.CTkEntry(left_frame, width=200)
net_metering_cost_entry.grid(row=10, column=1, padx=15, pady=10, sticky="w")

price_quoted_result = ctk.CTkLabel(left_frame, text="Price Quoted:")
price_quoted_result.grid(row=11, column=0, padx=15, pady=10, sticky="w")

total_cost_result = ctk.CTkLabel(left_frame, text="Total Cost:")
total_cost_result.grid(row=12, column=0, padx=15, pady=10, sticky="w")

# Create a button to calculate the cost
calculate_button = ctk.CTkButton(left_frame, text="Calculate", command=calculate_cost)
calculate_button.grid(row=13, column=0, padx=15, pady=10, sticky="w")

# Create the right frame (Preview)
right_frame = ctk.CTkFrame(window)
right_frame.grid(row=0, column=1, padx=15, pady=10, sticky="w")

# Title for the right frame
right_frame_title = ctk.CTkLabel(right_frame, text="Preview", font=("Helvetica", 20, "bold"))
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
