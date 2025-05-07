import streamlit as st
import os
import base64
from streamlit.components.v1 import html
import tempfile
import shutil

# Set page configuration
st.set_page_config(page_title="KIK - Meeresdaten", layout="wide")

# Title for the application
st.title("Studiengang KIK / AKI - Projekt Auswertung von Meeresdaten")

# Placeholder text section
st.markdown("""
## Ziel des Projektes

Das Ziel des Projektes ist die Auswertung von Meeresdaten, insbesondere der Korrelation zwischen Temperatur und Salzgehalt des Ozeans.

Die Daten stammen von der **World Ocean Database** und umfassen Messungen aus verschiedenen Tiefen des Ozeans für jeden Breiten- und Längengrad.

""")

# Define available depth levels
depths = [0, 50, 100, 150, 200, 300, 400, 500, 750, 1000, 1250, 1500, 1750, 1950]

# Section for scatter plots
st.header("Korrelation: Salzgehalt und Temperatur")
st.write("""
Die folgenden Grafiken zeigen die Korrelation zwischen Salzgehalt und Temperatur des Ozeans 
auf verschiedenen Wassertiefen. Wählen Sie eine Tiefe, um die entsprechende Visualisierung anzuzeigen.
""")

# Depth selection slider
selected_depth = st.select_slider(
    "Wählen Sie die Wassertiefe (in Metern):",
    options=depths
)

# Path to the HTML file for the selected depth
html_file_path = os.path.join("saved_plots2", f"scatter_pearson-{selected_depth}m.html")

# Check if file exists and display it
if os.path.exists(html_file_path):
    # Strategy 1: Try various text encodings
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    html_content = None
    
    for encoding in encodings_to_try:
        try:
            with open(html_file_path, "r", encoding=encoding) as file:
                html_content = file.read()
                break  # If successful, break the loop
        except UnicodeDecodeError:
            continue
    
    # Strategy 2: If all text encodings fail, try as binary
    if html_content is None:
        try:
            # Read as binary and create a data URI
            with open(html_file_path, "rb") as file:
                binary_content = file.read()
            
            # Create a temporary HTML file that loads the original file in an iframe
            temp_html = f"""
            <html>
            <head><meta charset="utf-8" /></head>
            <body style="margin:0; padding:0; height:100%;">
                <iframe src="{html_file_path}" style="width:100%; height:100%; border:none;"></iframe>
            </body>
            </html>
            """
            html_content = temp_html
            
        except Exception as e:
            st.error(f"Fehler beim Lesen der Binärdatei: {str(e)}")
    
    if html_content:
        # Display the interactive plot
        st.subheader(f"Salzgehalt-Temperatur-Korrelation auf {selected_depth}m Tiefe")
        html(html_content, height=800, scrolling=False)
    else:
        st.error(f"Die Datei konnte mit keiner bekannten Kodierung gelesen werden.")
else:
    st.error(f"Die Datei '{html_file_path}' wurde nicht gefunden. Bitte überprüfen Sie, ob der Ordner 'saved_plots' existiert und die Datei enthält.")

# Add a separator between the sections
st.markdown("---")

# Section for the correlation by depth graph
st.header("Gesamtübersicht: Temperatur-Salzgehalt-Korrelation nach Tiefe")
st.write("""
Die folgende Grafik zeigt die Korrelation zwischen Temperatur und Salzgehalt des Ozeans
über verschiedene Wassertiefen hinweg.
""")

# Path to the additional HTML file
correlation_file_path = os.path.join("saved_plots2", "temperature_salinity_correlation_by_depth.html")

# Check if file exists and display it using the same robust method
if os.path.exists(correlation_file_path):
    # Strategy 1: Try various text encodings
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    html_content = None
    
    for encoding in encodings_to_try:
        try:
            with open(correlation_file_path, "r", encoding=encoding) as file:
                html_content = file.read()
                break  # If successful, break the loop
        except UnicodeDecodeError:
            continue
    
    # Strategy 2: If all text encodings fail, try as binary
    if html_content is None:
        try:
            # Read as binary and create a data URI
            with open(correlation_file_path, "rb") as file:
                binary_content = file.read()
            
            # Create a temporary HTML file that loads the original file in an iframe
            temp_html = f"""
            <html>
            <head><meta charset="utf-8" /></head>
            <body style="margin:0; padding:0; height:100%;">
                <iframe src="{correlation_file_path}" style="width:100%; height:100%; border:none;"></iframe>
            </body>
            </html>
            """
            html_content = temp_html
            
        except Exception as e:
            st.error(f"Fehler beim Lesen der Binärdatei: {str(e)}")
    
    if html_content:
        # Display the interactive plot
        html(html_content, height=800, scrolling=False)
    else:
        st.error(f"Die Datei konnte mit keiner bekannten Kodierung gelesen werden.")
else:
    st.error(f"Die Datei '{correlation_file_path}' wurde nicht gefunden. Bitte überprüfen Sie, ob der Ordner 'saved_plots' existiert und die Datei enthält.")

    #NOTE: For first plots we may want to use st.maps
