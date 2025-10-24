# **☀️ Time-Series Weather Data Analyst 📊**

This is a comprehensive desktop GUI application built using Python's **Tkinter** and **Matplotlib** for performing time-series analysis and visualization of weather data (Temperature and Humidity).

## **✨ Features**

* **GUI-Driven:** Easy-to-use graphical interface with clear controls.  
* **Data Handling:** Loads CSV files, performs cleaning, and sets a Date index.  
* **Time-Series Analysis:** Calculates and displays detailed average statistics (**Weekly, Monthly, Yearly, Decade**) relative to the most recent data point.  
* **Targeted Visualization:** Generates four distinct line plots for single-variable trends: Daily Temperature, Monthly Temperature, Daily Humidity, and Monthly Humidity.  
* **Reporting:** Saves a full analysis and links to generated plots in a readable **Markdown (.md)** report file.  
* **Dummy Data:** Automatically creates a sample\_weather\_5years.csv file for immediate testing.

## **🚀 Getting Started: VS Code Setup**

Follow these steps to quickly set up and run the project in your local development environment.

### **1\. Prerequisites**

You need **Python 3.x** installed on your system. You must also install the required Python libraries using the following command in your terminal:

pip install pandas numpy matplotlib Pillow

*Note: Tkinter is usually included with standard Python installations.*

### **2\. Copy the Project (Option A: Local Setup)**

This is for when you are copying the code manually into a new local folder.

1. **Open your Terminal** (or VS Code's integrated terminal, typically accessed via \`Ctrl+\`\`).  
2. **Create and enter the project folder** using the cd (Change Directory) command:

mkdir weather-analyzer-project  
cd weather-analyzer-project

3. **Create the Python File:** Inside this new folder, create a new file named weather\_analyzer.py and paste the entire Python code into it.

### **3\. Copy the Project (Option B: Cloning from GitHub)**

This is the standard way to get the project from a remote GitHub repository into your VS Code workspace.

1. **Get the Repository URL:** Copy the HTTPS clone URL from your GitHub repository (e.g., https://github.com/user/repo-name.git).  
2. **Clone the Repo in VS Code:** In your VS Code terminal, run the git clone command. Replace \<YOUR\_REPO\_URL\> with the actual URL.

git clone \<YOUR\_REPO\_URL\>

3. **Change Directory:** Navigate into the newly cloned project folder (the folder name will be the repository name).

cd \<REPOSITORY\_NAME\>

### **4\. Run the Application**

Execute the script directly from the terminal while inside the project directory:

python weather\_analyzer.py

The graphical user interface (GUI) window will open, and a dummy data file named sample\_weather\_5years.csv will be automatically generated in your folder for testing.

## **📁 Input Code Explained: weather\_analyzer.py**

The Python code is structured as a single class, WeatherAnalyzerApp, encompassing the entire application logic, from GUI creation to data processing.

| Component | Description | Key Logic |
| :---- | :---- | :---- |
| **GUI Setup** | Initializes the Tkinter window, applies styling, and creates all interactive elements (tabs, buttons). | Uses ttk.Style for a modern, clean look. |
| **Data Management** | Handles the generation of synthetic data and the loading/preprocessing of the user's CSV file. | Uses pd.read\_csv, pd.to\_datetime, and set\_index('Date'). |
| **Time-Series Analysis** | Calculates mean, minimum, and maximum metrics for defined periods (Week, Month, Year, Decade) using Pandas slicing. | df.loc\[start\_date:end\_date\].mean(), min(), max(). |
| **Visualization** | Contains the core plotting logic using **Matplotlib**. It generates four separate, single-line plots based on user selection. | Uses df.resample('D').mean() or df.resample('M').mean() for time aggregation before plotting. |
| **Reporting** | Collects text output and plot image links to generate a final, structured **Markdown Report**. | Saves plot images as .png files and embeds their paths in the report. |

## **📊 Output & Usage**

### **1\. The Input Data Format**

The application requires a CSV file with at least these three columns. The internal script logic handles the necessary time-series conversion.

| Column Name | Data Type | Example | Description |
| :---- | :---- | :---- | :---- |
| Date | Datetime | 2024-01-15 | The date of the observation (any common format works). |
| Temperature\_C | Float | 18.5 | Daily average temperature in Celsius. |
| Humidity\_pct | Float | 65.2 | Daily average humidity percentage (0-100). |

### **2\. Analysis Output**

After clicking **"📈 Calculate Period Averages,"** the results are displayed in the **Analysis Results** tab, showing:

* **Period Breakdown:** Analysis for the last 7 Days, last 30 Days, last Year, and last Decade.  
* **Key Metrics:** Average, Minimum, and Maximum values for both Temperature (°C) and Humidity (%).

### **3\. Plotting Output**

The four dedicated buttons generate clean, dedicated line graphs in the **Trend Plotting** tab:

| Button | Data Aggregation | Purpose |
| :---- | :---- | :---- |
| **Daily Temperature Avg** | Daily (D frequency) | Shows high-resolution, day-to-day temperature fluctuations. |
| **Monthly Temperature Avg** | Monthly (M frequency) | Shows smoothed, long-term **seasonal** temperature patterns. |
| **Daily Humidity Avg** | Daily (D frequency) | Shows high-resolution, day-to-day humidity fluctuations. |
| **Monthly Humidity Avg** | Monthly (M frequency) | Shows smoothed, long-term **seasonal** humidity patterns. |

### **4\. Report Output**

Clicking **"💾 Save Report"** creates a file named Weather\_Analysis\_Report.md (or a name you choose). This file is a complete document containing:

* All calculated averages.  
* Markdown-formatted links to all .png image files of the plots you generated, ensuring all your results are documented together.