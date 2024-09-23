import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap import Style

table = None

class House:
    def __init__(self):
        self.data = None
        self.value = None
        self.kWh = None

class Expenses:
    @staticmethod
    def validate_data(data):
        date_pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        return bool(date_pattern.match(data))

    @staticmethod
    def visualize_previous_expenses(frame3):
        # Clear any existing widgets in frame3
        for widget in frame3.winfo_children():
            widget.destroy()

        # Check if the CSV file exists
        if not os.path.exists('electricity_bill_history.csv'):
            messagebox.showinfo("Notice", "No data found.")
            return

        try:
            # Load the data from the CSV file using Pandas
            df = pd.read_csv('electricity_bill_history.csv')

            # Check if the DataFrame is empty
            if df.empty:
                messagebox.showinfo("Notice", "No data found.")
                return

            # Adjust reading the 'Date' column to consider 'YYYY-MM-DD' format
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%Y-%m-%d')

            # Filter out rows where conversion failed (incorrect values or 'Date' in the header)
            df = df.dropna(subset=['Date'])

            # Sort the data by date
            df = df.sort_values(by='Date')

            # Group by month and year
            grouped_df = df.groupby(df['Date'].dt.to_period("M")).agg({'Value': 'sum', 'kWh': 'sum'}).reset_index()

            # Create a graph with two lines
            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Plot Value line
            ax1.plot(grouped_df['Date'].dt.strftime('%m-%Y'), grouped_df['Value'], marker='o', color='b', label='Currency')
            ax1.set_xlabel('Month and Year')
            ax1.set_ylabel('Total Value', color='b')
            ax1.tick_params('y', colors='b')

            # Create a second y-axis for kWh
            ax2 = ax1.twinx()
            ax2.plot(grouped_df['Date'].dt.strftime('%m-%Y'), grouped_df['kWh'], marker='s', color='r', label='kWh')
            ax2.set_ylabel('Total kWh', color='r')
            ax2.tick_params('y', colors='r')

            # Set labels and title
            ax1.set_title('Evolution in Currency and kWh Consumption')
            ax1.set_xticks(grouped_df['Date'].dt.strftime('%m-%Y'))
            ax1.set_xticklabels(grouped_df['Date'].dt.strftime('%m-%Y'), rotation=45, ha='right')

            # Add grid
            ax1.grid(True)

            # Add legend
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')

            # Display the graph
            plt.tight_layout()

            # Create FigureCanvasTkAgg object and add to frame3
            canvas = FigureCanvasTkAgg(fig, master=frame3)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        except Exception as e:
            messagebox.showinfo("Error", f"Error displaying previous expenses: {str(e)}")

    @staticmethod
    def save_history(entry_date, value_box, kWh_box):
        try:
            # Get values from the input widgets
            bill_date = entry_date.get()
            bill_value = value_box.get()
            kWh_value = kWh_box.get()

            if not Expenses.validate_data(bill_date):
                messagebox.showinfo("Error", "Invalid date format. Use DD/MM/YYYY.")
                return

            # Create the DataFrame if the CSV file exists
            if os.path.exists('electricity_bill_history.csv'):
                df = pd.read_csv('electricity_bill_history.csv')
            else:
                df = pd.DataFrame(columns=['Date', 'Value', 'kWh'])

            # Add new entry to the DataFrame only if all values are present
            if bill_date and bill_value and kWh_value:
                new_entry = pd.DataFrame({'Date': [pd.to_datetime(bill_date, format='%d/%m/%Y', errors='coerce').strftime('%Y-%m-%d')],
                                          'Value': [float(bill_value)],
                                          'kWh': [float(kWh_value)]})
                df = pd.concat([df, new_entry], ignore_index=True)

            # Save the DataFrame back to the CSV file
            df.to_csv('electricity_bill_history.csv', index=False)

            messagebox.showinfo("Success", "Data saved successfully.")

            # Update the table
            Expenses.display_table(frame2, table)

            # Update the graph
            Expenses.visualize_previous_expenses(frame3)

        except Exception as e:
            messagebox.showinfo("Error", f"Error saving data: {str(e)}")

    @staticmethod
    def display_table(frame2, table):
        # Check if the CSV file exists
        if not os.path.exists('electricity_bill_history.csv'):
            messagebox.showinfo("Notice", "No data found.")
            return

        try:
            # Load the data from the CSV file using Pandas
            df = pd.read_csv('electricity_bill_history.csv')

            # Check if the DataFrame is empty
            if df.empty:
                messagebox.showinfo("Notice", "No data found.")
                return

            # Adjust reading the 'Date' column to consider 'YYYY-MM-DD' format
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%Y-%m-%d')

            # Filter out rows where conversion failed (incorrect values or 'Date' in the header)
            df = df.dropna(subset=['Date'])

            # Sort the data by date
            df = df.sort_values(by='Date')

            # Destroy existing widgets in frame2, except the first two (indices 2 and above)
            for widget in frame2.winfo_children()[2:]:
                widget.destroy()

            # Create the table in frame2
            table = ttk.Treeview(frame2, columns=['Date', 'Value', 'kWh'], show='headings')

            delete_button = tk.Button(frame2, text='Delete Selected', command=lambda: Expenses.delete_data(table, df))
            delete_button.pack(pady=10)

            modify_button = tk.Button(frame2, text='Modify Selected', command=lambda: Expenses.modify_data(table, df))
            modify_button.pack(pady=10)

            # Define headers
            table.heading('Date', text='Date')
            table.heading('Value', text='Value')
            table.heading('kWh', text='kWh')

            # Add data to the table
            for index, row in df.iterrows():
                table.insert("", "end", values=(row['Date'].strftime('%d/%m/%Y'), row['Value'], row['kWh']))

            # Add the table to frame2
            table.pack(padx=10, pady=10)

             # Add buttons to delete or alter data, if they don't exist yet
            if not any(isinstance(widget, tk.Button) for widget in frame2.winfo_children()):
                delete_button = tk.Button(frame2, text='Delete Selected', command=lambda: Expenses.delete_data(table, df))
                delete_button.pack(pady=10)

                modify_button = tk.Button(frame2, text='Modify Selected', command=lambda: Expenses.modify_data(table, df))
                modify_button.pack(pady=10)

        except Exception as e:
            messagebox.showinfo("Error", f"Error displaying table: {str(e)}")

    @staticmethod
    def delete_data(table,df):
        # Get the selected item in the table
        selected_item = table.selection()
        if not selected_item:
            messagebox.showinfo("Notice", "No item selected.")
            return

        # Get the index of the selected item
        index = table.index(selected_item)

        # Remove the corresponding row in the DataFrame
        df = df.drop(index, axis=0)

        # Save the updated DataFrame back to the CSV file
        df.to_csv('electricity_bill_history.csv', index=False)

        # Remove item from the table
        table.delete(selected_item)

        messagebox.showinfo("Success", "Item successfully deleted.")

    @staticmethod
    def modify_data(table, df, frame2, visualize_previous_expenses):
        # Get the selected item in the table
        selected_item = table.selection()
        if not selected_item:
            messagebox.showinfo("Notice", "No item selected.")
            return

        # Get the index of the selected item
        index = table.index(selected_item)

        # Open a window for editing
        edit_window = tk.Toplevel(root)

        # Add fields for editing
        tk.Label(edit_window, text="New Date:").grid(row=0, column=0)
        new_date_entry = tk.Entry(edit_window)
        new_date_entry.grid(row=0, column=1)

        tk.Label(edit_window, text="New Value:").grid(row=1, column=0)
        new_value_entry = tk.Entry(edit_window)
        new_value_entry.grid(row=1, column=1)

        # Populate the edit fields with the current values
        new_date_entry.insert(0, df.at[index, 'Date'].strftime('%d/%m/%Y'))
        new_value_entry.insert(0, df.at[index, 'Value'])

        # Function to apply the changes
        def apply_changes():
            # Get the new values
            new_date = new_date_entry.get()
            new_value = new_value_entry.get()

            # Validate the date
            if not Expenses.validate_data(new_date):
                messagebox.showinfo("Error", "Invalid date format. Use DD/MM/YYYY.")
                return
            
            # Convert new date to datetime
            new_date = pd.to_datetime(new_date, format='%d/%m/%Y', errors='coerce')

            # Verification if the date is valid
            if pd.isnull(new_date):
                messagebox.showinfo("Error", "Invalid date.")
                return
            
            # Update the DataFrame
            df.at[index, 'Date'] = new_date
            df.at[index, 'Value'] = float(new_value)

            # Update the table
            table.item(selected_item, values=(new_date.strftime('%d/%m/%Y'), new_value))

            # Save the updated DataFrame back to the CSV file
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')  
            df.to_csv('electricity_bill_history.csv', index=False)

            # Close the window
            edit_window.destroy()

            messagebox.showinfo("Success", "Item successfully modified.")

             # Adicionar botão para visualizar o gráfico após alterar o dado
            visualize_button = tk.Button(frame2, text='Show Previous Expenses', command=visualize_previous_expenses)
            visualize_button.pack(pady=10)

    @staticmethod
    def delete_record(table, df):
        # Get selected item from the table
        selected_item = table.selection()
        if not selected_item:
            messagebox.showinfo("Notice", "No item selected.")
            return
    
        # Get the index of the selected item
        index = table.index(selected_item)
    
        # Remove the corresponding row from the DataFrame
        df = df.drop(index, axis=0)
    
        # Save the updated DataFrame back to the CSV file
        df.to_csv('electricity_bill_history.csv', index=False)
    
        # Remove the item from the table
        table.delete(selected_item)
    
        messagebox.showinfo("Success", "Item successfully deleted.")
    
        # Refresh the table
        Expenses.display_table(frame2, table)
    
        # Update the graph
        Expenses.visualize_previous_expenses(frame3)

    @staticmethod
    def edit_record(table, df):
        # Get selected item from the table
        selected_item = table.selection()
        if not selected_item:
            messagebox.showinfo("Notice", "No item selected.")
            return
    
        # Get the index of the selected item
        index = table.index(selected_item)
    
        # Open window for editing
        edit_window = tk.Toplevel(root)
    
        # Add fields for editing
        tk.Label(edit_window, text="New Date:").grid(row=0, column=0)
        new_date_entry = tk.Entry(edit_window)
        new_date_entry.grid(row=0, column=1)
    
        tk.Label(edit_window, text="New Value:").grid(row=1, column=0)
        new_value_entry = tk.Entry(edit_window)
        new_value_entry.grid(row=1, column=1)
    
        tk.Label(edit_window, text="Confirm Changes?").grid(row=2, column=0)
        confirm_button = tk.Button(edit_window, text='Update Data', 
                                   command=lambda: Expenses.apply_changes(edit_window, new_date_entry, new_value_entry, table, df, selected_item, index))
        confirm_button.grid(row=2, column=1)
    
        # Populate the editing fields with current values
        new_date_entry.insert(0, df.at[index, 'Date'].strftime('%d/%m/%Y'))
        new_value_entry.insert(0, df.at[index, 'Value'])
    
    @staticmethod
    def apply_changes(edit_window, new_date_entry, new_value_entry, table, df, selected_item, index):
        # Get the new values
        new_date = new_date_entry.get()
        new_value = new_value_entry.get()
    
        # Validate the date
        if not Expenses.validate_date(new_date):
            messagebox.showinfo("Error", "Invalid date format. Use DD/MM/YYYY.")
            return
    
        # Convert the new date to datetime
        new_date = pd.to_datetime(new_date, format='%d/%m/%Y', errors='coerce')
    
        # Check if the conversion failed
        if pd.isnull(new_date):
            messagebox.showinfo("Error", "Invalid date.")
            return
    
        # Update values in the DataFrame
        df.at[index, 'Date'] = new_date
        df.at[index, 'Value'] = float(new_value)
    
        # Update the table
        table.item(selected_item, values=(new_date.strftime('%d/%m/%Y'), new_value))
    
        # Save the updated DataFrame back to the CSV file
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        df.to_csv('electricity_bill_history.csv', index=False)
    
        # Close the editing window
        edit_window.destroy()
    
        messagebox.showinfo("Success", "Item updated successfully.")
    
        # Refresh the table
        Expenses.display_table(frame2, table)
    
        # Update the graph
        Expenses.visualize_previous_expenses(frame3)
    

class SolarEnergy:
    @staticmethod
    def calculate_solar_panel_autonomy(panel_power_entry, panel_cost_entry):
        try:
            # Check if the CSV file exists
            if not os.path.exists('electricity_bill_history.csv'):
                messagebox.showinfo("Notice", "No data found.")
                return

            # Load the data from the CSV file using Pandas
            df = pd.read_csv('electricity_bill_history.csv', parse_dates=['Date'], dayfirst=True)

            # Check if the DataFrame is empty
            if df.empty:
                messagebox.showinfo("Notice", "No data found in the CSV file.")
                return

            # Convert the 'Value' and 'kWh' columns to numeric
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
            df['kWh'] = pd.to_numeric(df['kWh'], errors='coerce')

            # Check for null values in the 'kWh' column
            if df['kWh'].isnull().any():
                messagebox.showinfo("Notice", "There are null or non-numeric values in the 'kWh' column.")
                return

            # Calculate the average kWh consumption
            average_kWh_consumption = df['kWh'].mean()

            # Calculate annual consumption
            annual_consumption = average_kWh_consumption * 12

            # Solar panel generation data
            noct_irradiation_rate = 800  # Assuming 800 kWh/m²/year
            correction_factor_F = 0.85  # Correction factor

            # Calculate the power of the solar panels
            panel_power = (average_kWh_consumption * 12) / (noct_irradiation_rate * correction_factor_F)

            # Calculate the number of solar panels needed
            num_panels = panel_power / float(panel_power_entry.get())

            # Calculate the average price per kWh using the database
            total_value = df['Value'].sum()
            total_kWh = df['kWh'].sum()

            if total_kWh == 0:
                messagebox.showinfo("Notice", "Unable to calculate the average price per kWh. Total kWh is zero.")
                return

            avg_price_kWh = total_value / total_kWh

            # Calculate the costs involved
            panel_cost = float(panel_cost_entry.get())
            total_cost = num_panels * panel_cost

            # Calculate the expected annual savings
            expected_annual_savings = average_kWh_consumption * 12 * avg_price_kWh

            # Calculate the financial payback period
            financial_payback_period = total_cost / expected_annual_savings

            messagebox.showinfo("Result", f"The average monthly consumption in kWh is {round(average_kWh_consumption, 2)}.\n"
                                          f"The estimated annual consumption is {round(annual_consumption, 2)} kWh.\n\n"
                                          f"The required solar panel power is {round(panel_power, 2)} Wp.\n"
                                          f"Approximately {round(num_panels, 2)} solar panels are needed.\n\n"
                                          f"The estimated total cost is R${round(total_cost, 2)}.\n"
                                          f"The expected annual savings are R${round(expected_annual_savings, 2)}.\n"
                                          f"The financial payback period is approximately {round(financial_payback_period, 2)} years.")

        except Exception as e:
            messagebox.showinfo("Error", f"Error calculating solar panel autonomy: {str(e)}")

style = Style()

# Create the main window
root = style.master
style = Style(theme='superhero')

# Get screen size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

width = screen_width 
height = screen_height 
root.geometry(f"{width}x{height}")

root.title('Energy Expense Control')

# Create a notebook (Widget to handle different tabs)
notebook = ttk.Notebook(root, height=screen_height, width=screen_width)
notebook.pack(pady=0, expand=False)

# Creating the tabs
frame1 = ttk.Frame(notebook, width=width, height=height)
frame2 = ttk.Frame(notebook, width=width, height=height)
frame3 = ttk.Frame(notebook, width=width, height=height)
frame4 = ttk.Frame(notebook, width=width, height=height)

frame1.pack(fill='both', expand=True)  # Home Page
frame2.pack(fill='both', expand=True)  # Table of Past Expenses
frame3.pack(fill='both', expand=True)  # View Past Expenses
frame4.pack(fill='both', expand=True)  # Solar Planning

notebook.add(frame1, text='Home Page')
notebook.add(frame2, text='Table of Past Expenses')
notebook.add(frame3, text='View Past Expenses')
notebook.add(frame4, text='Solar Planning')

# Add images to tabs
img1 = tk.PhotoImage(file="Images/casa-com-certificado-energetico.png")
img4 = tk.PhotoImage(file="Images/5415790 (Telefone).png")

label1 = tk.Label(frame1, image=img1, compound="top", text="Home Page").pack(pady=20)

entry_date = tk.Entry(frame1, width=15)
tk.Label(frame1, text='Date:').pack(pady=5)
entry_date.pack(pady=5)

value_box = tk.Entry(frame1, width=15)
tk.Label(frame1, text='Value:').pack(pady=5)
value_box.pack(pady=5)

kWh_box = tk.Entry(frame1, width=15)  
tk.Label(frame1, text='kWh:').pack(pady=5)
kWh_box.pack(pady=5)

save_button = tk.Button(frame1, text="Save Bill", command=lambda: Expenses.save_history(entry_date, value_box, kWh_box))
save_button.pack(pady=10)

tk.Label(frame2, text="Table of Past Expenses").pack(pady=20)

# Creating buttons
display_table_btn = tk.Button(frame2, text="Show Table", command=lambda: Expenses.display_table(frame2, table))
display_table_btn.pack(pady=10)

delete_button = tk.Button(frame2, text='Delete Selected', command=lambda: Expenses.delete_data(table, df))
delete_button.pack(pady=10)

edit_button = tk.Button(frame2, text='Edit Selected', command=lambda: Expenses.modify_data(table, df, frame2, visualize_previous_expenses))
edit_button.pack(pady=10)

tk.Label(frame3, text="Visualize Previous Expenses").pack(pady=20)

view_chart_btn = tk.Button(frame3, text="View Past Expenses", command=lambda: Expenses.visualize_previous_expenses(frame3))
view_chart_btn.pack(pady=10)

tk.Label(frame4, text="Green Area", image=img4, compound="top").pack(pady=20)

tk.Label(frame4, text="Panel Power (kWp):").pack(pady=5)
panel_power_entry = tk.Entry(frame4, width=15)
panel_power_entry.pack(pady=5)

tk.Label(frame4, text="Panel Cost (R$/Wp):").pack(pady=5)
panel_cost_entry = tk.Entry(frame4, width=15)
panel_cost_entry.pack(pady=5)

solar_autonomy_btn = tk.Button(frame4, text='Calculate Solar Panel Autonomy', command=lambda: SolarEnergy.calculate_solar_panel_autonomy(panel_power_entry, panel_cost_entry))
solar_autonomy_btn.pack(padx=10, pady=10)

root.mainloop()
