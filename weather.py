import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import datetime, timedelta

# --- Configuration & Constants ---
APP_TITLE = "☀️ Time-Series Weather Data Analyst 📊"
WINDOW_SIZE = "1200x750"

# --- New, more vibrant color palette ---
BG_COLOR = "#F0F8FF"     # Alice Blue (Very light blue background)
ACCENT_COLOR = "#42A5F5" # Primary Blue (Medium shade for buttons/highlights)
PRIMARY_COLOR = "#1976D2" # Darker Blue (For headers/section titles)
TEXT_COLOR = "#212121"   # Dark Gray (For general text)

REPORT_FILENAME = "Weather_Analysis_Report.md"
DUMMY_DATA_FILENAME = "sample_weather_5years.csv"

# --- Main Application Class ---

class WeatherAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title(APP_TITLE)
        master.geometry(WINDOW_SIZE)
        master.configure(bg=BG_COLOR)

        self.df = None # DataFrame to hold the loaded data
        self.report_content = [] # List to store report sections
        self.max_date = None
        self.is_loaded = False
        
        # --- Custom TTK Style Configuration for Modern Look ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # General frame and label styles
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR, font=('Inter', 10))
        
        # Define a custom Primary button style
        self.style.configure('Primary.TButton', 
                             background=ACCENT_COLOR, 
                             foreground='white', 
                             font=('Inter', 10, 'bold'), 
                             borderwidth=0, 
                             relief='flat',
                             padding=[15, 8]) # Increased padding for better touch target/look
        self.style.map('Primary.TButton', 
                       background=[('active', PRIMARY_COLOR), ('disabled', 'gray')],
                       foreground=[('active', 'white')])

        # Header style
        self.style.configure('Header.TLabel', background=PRIMARY_COLOR, foreground='white', font=('Inter', 18, 'bold'))

        # --- Generate Dummy Data for First Run ---
        self._create_dummy_data_file()

        # --- Set up the Main GUI Layout ---
        self._setup_layout(master)
        
    def _setup_layout(self, master):
        """Sets up the main structure of the Tkinter window."""
        
        # 1. Header Frame (Top) - Uses darker PRIMARY_COLOR
        header_frame = tk.Frame(master, bg=PRIMARY_COLOR, pady=15)
        header_frame.pack(fill='x', side='top')
        ttk.Label(header_frame, text=APP_TITLE, style='Header.TLabel').pack()

        # 2. Control Panel (Left Sidebar)
        control_panel = ttk.Frame(master, width=300)
        control_panel.pack(side='left', fill='y', padx=10, pady=10)
        
        # Data Upload Section
        self._add_control_section(control_panel, "1. Data Management", 
                                  self.load_data, "📁 Load CSV Dataset")
        
        self.status_label = ttk.Label(control_panel, text="Status: Ready", font=('Inter', 10, 'italic'), foreground=PRIMARY_COLOR)
        self.status_label.pack(pady=(0, 20))

        # Analysis Section
        analysis_frame = self._add_control_section(control_panel, "2. Time-Series Analysis")
        # Apply new button style
        ttk.Button(analysis_frame, text="📈 Calculate Period Averages", command=self.perform_time_series_analysis, style='Primary.TButton').pack(fill='x', pady=5)
        
        # Plotting Section (Now with 4 dedicated buttons)
        plotting_frame = self._add_control_section(control_panel, "3. 📈 Visualization")
        
        ttk.Label(plotting_frame, text="Temperature Trends:", background=BG_COLOR, font=('Inter', 10, 'underline')).pack(fill='x', pady=(5, 0))
        ttk.Button(plotting_frame, text="🌡️ Daily Temperature Avg", 
                   command=lambda: self._plot_single_trend('Temperature_C', 'Temperature', 'D'), style='Primary.TButton').pack(fill='x', pady=3)
        ttk.Button(plotting_frame, text="🌡️ Monthly Temperature Avg", 
                   command=lambda: self._plot_single_trend('Temperature_C', 'Temperature', 'M'), style='Primary.TButton').pack(fill='x', pady=3)
        
        ttk.Label(plotting_frame, text="Humidity Trends:", background=BG_COLOR, font=('Inter', 10, 'underline')).pack(fill='x', pady=(10, 0))
        ttk.Button(plotting_frame, text="💧 Daily Humidity Avg", 
                   command=lambda: self._plot_single_trend('Humidity_pct', 'Humidity', 'D'), style='Primary.TButton').pack(fill='x', pady=3)
        ttk.Button(plotting_frame, text="💧 Monthly Humidity Avg", 
                   command=lambda: self._plot_single_trend('Humidity_pct', 'Humidity', 'M'), style='Primary.TButton').pack(fill='x', pady=3)


        # Report Section
        self._add_control_section(control_panel, "4. Reporting", 
                                  self.save_report, f"💾 Save Report ({REPORT_FILENAME})")

        # 3. Output Notebook (Right Main Area)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Analysis Tab
        self.analysis_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.analysis_frame, text='📊 Analysis Results')
        # Styling the ScrolledText for a clean, flat look
        self.analysis_text = scrolledtext.ScrolledText(self.analysis_frame, wrap=tk.WORD, font=('Consolas', 10), bg='#FFFFFF', fg=TEXT_COLOR, padx=10, pady=10, relief=tk.FLAT)
        self.analysis_text.pack(fill='both', expand=True)
        
        # --- Configure Text Tags for Attractive Report Output ---
        self.analysis_text.tag_config('title_style', foreground=PRIMARY_COLOR, font=('Inter', 16, 'bold'))
        self.analysis_text.tag_config('subtitle_style', foreground=ACCENT_COLOR, font=('Inter', 12, 'italic'))
        self.analysis_text.tag_config('temp_metric', foreground='#E53935', font=('Consolas', 10, 'bold')) # Red for Temp
        self.analysis_text.tag_config('humid_metric', foreground='#42A5F5', font=('Consolas', 10, 'bold')) # Blue for Humidity
        self.analysis_text.tag_config('section_header', foreground=PRIMARY_COLOR, font=('Inter', 14, 'bold'), underline=1)


        # Plotting Tab
        self.plot_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_frame, text='📈 Trend Plotting')
        self._clear_plot() # Initialize plot area

    def _add_control_section(self, parent, title, command=None, button_text=None):
        """Helper to create section headers and buttons in the control panel."""
        # Use subtle visual separation for sections
        section_frame = ttk.Frame(parent, padding="10", relief=tk.GROOVE)
        section_frame.pack(fill='x', pady=10, padx=5)
        
        # Section title with contrasting background for visibility
        ttk.Label(section_frame, text=title, font=('Inter', 12, 'bold'), background=PRIMARY_COLOR, foreground='white', padding=5).pack(fill='x', pady=(0, 5))
        
        if command and button_text:
            # Apply the new primary button style
            ttk.Button(section_frame, text=button_text, command=command, style='Primary.TButton').pack(fill='x', pady=5)
            
        return section_frame

    # --- Data Generation and Loading ---
    
    def _create_dummy_data_file(self):
        """Generates a large, synthetic weather dataset (5 years) for robust testing."""
        if os.path.exists(DUMMY_DATA_FILENAME):
            print(f"Dummy file '{DUMMY_DATA_FILENAME}' already exists.")
            return

        print(f"Generating large dummy data file: {DUMMY_DATA_FILENAME}...")

        start_date = datetime.now() - timedelta(days=5 * 365) # 5 years ago
        end_date = datetime.now()
        dates = pd.to_datetime(pd.date_range(start=start_date, end=end_date, freq='D'))
        
        # Use seasonal sine wave for temperature to make data realistic
        days = np.arange(len(dates))
        temp_base = 15 + 10 * np.sin(2 * np.pi * days / 365.25)
        temp_noise = np.random.normal(loc=0, scale=3, size=len(dates))
        
        # Use inverse wave for humidity
        humidity_base = 70 + 15 * np.cos(2 * np.pi * days / 365.25)
        humidity_noise = np.random.normal(loc=0, scale=5, size=len(dates))

        data = {
            'Date': dates,
            # Temperature in Celsius: Base (seasonal) + Noise
            'Temperature_C': (temp_base + temp_noise).round(1),
            # Humidity Percentage: Base (seasonal) + Noise
            'Humidity_pct': np.clip((humidity_base + humidity_noise).round(1), 30, 100),
            # Wind Speed in km/h
            'WindSpeed_kmh': np.random.uniform(2, 40, len(dates)).round(1)
        }
        
        pd.DataFrame(data).to_csv(DUMMY_DATA_FILENAME, index=False)
        print(f"Successfully created {len(dates)} records in '{DUMMY_DATA_FILENAME}'.")

    def load_data(self):
        """Handles file dialog and loads the CSV data into a pandas DataFrame."""
        filepath = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=DUMMY_DATA_FILENAME
        )
        if not filepath:
            return

        self.report_content = []
        try:
            df_raw = pd.read_csv(filepath)
            
            # 1. Data Cleaning and Preprocessing (Pandas Core)
            required_cols = {'Date': 'Date', 'Temperature_C': 'Temperature_C', 'Humidity_pct': 'Humidity_pct'}
            if not all(col in df_raw.columns for col in required_cols.keys()):
                 messagebox.showerror("Data Error", "File must contain 'Date', 'Temperature_C', and 'Humidity_pct' columns.")
                 return

            df = df_raw.rename(columns=required_cols)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df.set_index('Date', inplace=True)
            df.dropna(subset=['Temperature_C', 'Humidity_pct'], inplace=True)
            df = df.sort_index() # Sort by date index
            
            self.df = df
            self.max_date = self.df.index.max()
            self.is_loaded = True
            
            # Reset analysis view
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, f"Data Loaded Successfully!\nTotal Records: {len(self.df)}\nDate Range: {self.df.index.min().strftime('%Y-%m-%d')} to {self.max_date.strftime('%Y-%m-%d')}")
            
            self.status_label.config(text=f"Status: Data Loaded! ({len(self.df)} records)")
            messagebox.showinfo("Success", f"Successfully loaded {len(self.df)} records from {os.path.basename(filepath)}.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{e}")
            self.df = None
            self.is_loaded = False
            self.status_label.config(text="Status: Loading Failed!")

    # --- Core Analysis Functions (Enhanced for Attractive Text Output) ---

    def perform_time_series_analysis(self):
        """Calculates and displays averages for the last week, month, year, and decade, with rich formatting."""
        if not self.is_loaded or self.df is None:
            messagebox.showwarning("Warning", "Please load a dataset first!")
            return
        
        # Clear previous analysis and report log
        self.report_content = []
        self.analysis_text.delete(1.0, tk.END)
        self.notebook.select(0) # Switch to the analysis tab
        
        # Title for the display using color tags
        title = "Comprehensive Time-Series Analysis Report"
        self.analysis_text.insert(tk.END, title + "\n", 'title_style')
        
        reference_date = f"\nReference Date (End of Data): {self.max_date.strftime('%Y-%m-%d')}\n"
        self.analysis_text.insert(tk.END, reference_date, 'subtitle_style')
        
        # Log simple Markdown title for the saved file
        self.report_content.append(f"# {title}\nReference Date: {self.max_date.strftime('%Y-%m-%d')}\n") 
        
        # Define time periods relative to the last data point (self.max_date)
        periods = {
            "Last 7 Days (Week)": self.max_date - pd.Timedelta(days=7),
            "Last 30 Days (Month)": self.max_date - pd.Timedelta(days=30),
            "Last Year": self.max_date - pd.DateOffset(years=1),
            "Last Decade": self.max_date - pd.DateOffset(years=10)
        }
        
        for name, start_date in periods.items():
            # Pandas time-series slicing
            subset = self.df.loc[start_date:self.max_date]
            
            header_text = f"\n\n--- {name} (from {start_date.strftime('%Y-%m-%d')}) ---\n"
            self.analysis_text.insert(tk.END, header_text, 'section_header')

            if subset.empty:
                result = f"- Data not available for this period.\n"
                self.analysis_text.insert(tk.END, result)
                self.report_content.append(f"## {name}\n- Data not available for this period.\n")
            else:
                # Core NumPy/Pandas Calculation
                avg_temp = subset['Temperature_C'].mean()
                avg_humid = subset['Humidity_pct'].mean()
                
                # Formatted text for Tkinter display
                temp_text = (
                    f"🌡️ Avg Temperature: {avg_temp:.2f} °C "
                    f"(Min: {subset['Temperature_C'].min():.1f} | Max: {subset['Temperature_C'].max():.1f})\n"
                )
                humid_text = (
                    f"💧 Avg Humidity: {avg_humid:.2f} % "
                    f"(Min: {subset['Humidity_pct'].min():.1f} | Max: {subset['Humidity_pct'].max():.1f})\n"
                )
                
                # Display with tags
                self.analysis_text.insert(tk.END, temp_text, 'temp_metric')
                self.analysis_text.insert(tk.END, humid_text, 'humid_metric')

                # Simple Markdown content for the saved file
                markdown_result = (
                    f"## {name} (from {start_date.strftime('%Y-%m-%d')})\n"
                    f"- 🌡️ Avg Temperature: {avg_temp:.2f} °C (Min: {subset['Temperature_C'].min():.1f} | Max: {subset['Temperature_C'].max():.1f})\n"
                    f"- 💧 Avg Humidity: {avg_humid:.2f} % (Min: {subset['Humidity_pct'].min():.1f} | Max: {subset['Humidity_pct'].max():.1f})\n"
                )
                self.report_content.append(markdown_result)

        self.status_label.config(text="Status: Analysis Complete! (Rich Text Output)")

    # --- Visualization Functions (Matplotlib) ---

    def _clear_plot(self):
        """Clears the plot area in the Plotting Tab."""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
    def _display_plot(self, fig, plot_filename, y_label):
        """Common logic to clear plot area, embed the Matplotlib figure, and log to report."""
        
        # 1. Clear previous plot
        self._clear_plot()

        # 2. Save the figure (needed for the report link)
        fig.savefig(plot_filename, bbox_inches='tight', dpi=150) 
        
        # 3. Embed the Plot into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True, padx=10, pady=10)
        canvas.draw()
        
        # 4. Log the image path to the report
        markdown_link = f"![{y_label} Plot]({plot_filename})"
        self.report_content.append(f"\n---\n## Visualization: {y_label} Plot\n\n{markdown_link}\n")
        self.status_label.config(text=f"Status: Plot for {y_label} generated and saved as {plot_filename}!")

        # Close the Matplotlib figure to free memory
        plt.close(fig)

    def _plot_single_trend(self, column_name, y_label, frequency_code):
        """
        Generates a single line plot for a specific column at a given frequency.
        frequency_code: 'D' for Daily, 'M' for Monthly.
        """
        if not self.is_loaded or self.df is None:
            messagebox.showwarning("Warning", "Please load a dataset first!")
            return
            
        if column_name not in self.df.columns:
            messagebox.showerror("Error", f"Column '{column_name}' not found for plotting.")
            return

        self.notebook.select(1) # Switch to the plotting tab
        
        try:
            freq_name = "Daily" if frequency_code == 'D' else "Monthly"
            
            # 1. Prepare Time-Series Data (Pandas Resampling)
            data_series = self.df[column_name].resample(frequency_code).mean().dropna()

            # 2. Create the Matplotlib Figure (Color and Styling)
            fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_COLOR)
            fig.patch.set_alpha(0.8) 
            
            # Determine styling based on frequency and metric
            line_color = ACCENT_COLOR
            line_width = 1.5
            marker_style = None
            plot_title_base = f'{freq_name} Average {y_label} Trend Analysis'
            
            if frequency_code == 'M':
                line_width = 3
                marker_style = 'o'
                if 'Temp' in y_label:
                    line_color = '#E53935' # Vivid Red for Monthly Temp
                    
                else:
                    line_color = PRIMARY_COLOR # Dark Blue for Monthly Humidity
                    
            else: # Daily
                line_width = 1.5
                if 'Temp' in y_label:
                    line_color = '#FFB74D' # Orange for Daily Temp
                else:
                    line_color = '#81D4FA' # Light Blue for Daily Humidity

            # 3. Plot the data
            ax.plot(data_series.index, data_series.values, 
                    label=f'{freq_name} Avg {y_label}', 
                    color=line_color, 
                    linewidth=line_width, 
                    marker=marker_style, 
                    markersize=4 if marker_style else 0,
                    markeredgecolor='white' if marker_style else line_color)
            
            # 4. Aesthetic Enhancements
            ax.set_title(plot_title_base, 
                          fontsize=15, color=PRIMARY_COLOR, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel(f'Average {y_label}', fontsize=12)
            
            ax.grid(True, linestyle='--', alpha=0.4)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            ax.tick_params(axis='x', rotation=45)
            ax.legend(loc='best', frameon=True, shadow=True)
            plt.tight_layout()

            # 5. Display and Log
            plot_filename = f"trend_{frequency_code.lower()}_{column_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self._display_plot(fig, plot_filename, plot_title_base)

        except Exception as e:
            messagebox.showerror("Plotting Error", f"Could not generate or save plot: {e}")

    # --- File Handling ---

    def save_report(self):
        """Saves the accumulated analysis content to a readable Markdown (.md) file."""
        if not self.report_content or self.df is None:
            messagebox.showwarning("Save Warning", "Please perform an analysis first!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            initialfile=REPORT_FILENAME,
            filetypes=[("Markdown Document", "*.md"), ("Text Document", "*.txt")]
        )

        if filepath:
            try:
                # Add overall summary to the report
                summary = (
                    f"\n---\n# Data Summary\n"
                    f"- Total Records Analyzed: {len(self.df)}\n"
                    f"- Dataset Range: {self.df.index.min().strftime('%Y-%m-%d')} to {self.max_date.strftime('%Y-%m-%d')}\n"
                    f"- Overall Mean Temp: {self.df['Temperature_C'].mean():.2f} °C\n"
                    f"- Overall Mean Humidity: {self.df['Humidity_pct'].mean():.2f} %\n"
                    f"---\n\n"
                )
                
                # Combine all sections
                final_report = summary + "\n".join(self.report_content)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(final_report)
                
                messagebox.showinfo("Success", f"Analysis report saved successfully to:\n{filepath}\n\nThis file is a Markdown (.md) document, which is easily readable in any text editor or browser. Note that plot images are saved separately in the same directory and linked in the report.")
                self.status_label.config(text="Status: Report Saved!")

            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save report: {e}")

# --- Main Execution Block ---

if __name__ == "__main__":
    # Ensure all necessary libraries are imported and set up before running Tkinter
    
    try:
        root = tk.Tk()
        app = WeatherAnalyzerApp(root)
        root.mainloop()
    except Exception as e:
        # Catch exceptions that might occur during setup (e.g., missing dependencies)
        print(f"An unexpected error occurred during application startup: {e}")
        messagebox.showerror("Startup Error", f"The application could not start. Ensure all libraries (pandas, numpy, matplotlib, tk) are installed.\nError: {e}")
