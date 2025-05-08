import streamlit as st
import os
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit.components.v1 import html
import base64
from pathlib import Path

# Set page configuration
st.set_page_config(page_title="KIK - Ozeanographische Datenanalyse", layout="wide")

# Title for the application
st.title("Studiengang KIK/AKI - Meeresforschung: Analyse globaler Ozeantemperatur und Salzgehaltskorrelationen")

# Placeholder text section
st.markdown("""
<h2 style='font-size:3.0em'>Projektübersicht</h2>
<p style='font-size:1.6em'>
Im Rahmen des Moduls <b>„KI in den Lifesciences"</b> verfolgt das vorliegende Projekt das Ziel, Meeresdaten systematisch auszuwerten und insbesondere die Korrelation zwischen Temperatur und Salzgehalt des Ozeans zu untersuchen. Die Analyse basiert auf Messdaten der <b>World Ocean Database</b>, die für sämtliche Breiten- und Längengrade sowie verschiedene Tiefenebenen des Ozeans vorliegen. Eine weiterführende, freiwillige Fragestellung bestand darin, die Daten gezielt auf potenzielle Muster oder Auffälligkeiten hin zu analysieren, um neue wissenschaftliche Erkenntnisse über ozeanografische Zusammenhänge zu gewinnen.
</p>

<h2 style='font-size:3.0em'>Datensatz</h2>
<p style='font-size:1.6em'>
Für die Untersuchung wurde der frei zugängliche Datensatz des <b>World Ocean Atlas</b> ausgewählt. Es wurde gezielt der Datensatz aus dem Jahr 2023 herangezogen, da dieser den aktuellsten Stand der verfügbaren Messungen repräsentiert. Der Datensatz umfasst für jedes Längen- und Breitengradpaar Messstationen auf unterschiedlichen Tiefenmetern, die eine Vielzahl ozeanografischer Parameter wie Salzgehalt, Temperatur, Stickstoffgehalt und weitere chemische sowie physikalische Größen erfassen. Im Rahmen dieses Projekts lag der Fokus insbesondere auf den Parametern Temperatur und Salzgehalt, da für diese Variablen die umfangreichsten und zuverlässigsten Messreihen vorliegen. Die verwendeten Werte stellen Durchschnittsdaten (Averages) aus dem Zeitraum 2015 bis 2022 dar, was sowohl die Aktualität als auch die Präzision der Analyse gewährleistet. Über 95 % der Messstationen liefern für Temperatur und Salzgehalt valide Daten, sodass eine robuste und repräsentative Auswertung dieser beiden Schlüsselparameter möglich ist.
</p>""", unsafe_allow_html=True)

# Define available depth levels
depths = [0, 50, 100, 150, 200, 300, 400, 500, 750, 1000, 1250, 1500, 1750, 1950]

# Section for visualization
st.markdown("<h2 style='font-size:3.0em;'>Visualisierung der T-S Korrelation in verschiedenen Meerestiefen</h2>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:1.6em'>
Die nachfolgenden Visualisierungen zeigen die räumliche Verteilung der Korrelationen zwischen Temperatur und Salzgehalt (T-S-Korrelation) auf verschiedenen Tiefenebenen. Diese Darstellungen ermöglichen es, regionale Unterschiede und tiefenabhängige Muster zu identifizieren.

Die Pearson-Korrelationskoeffizienten wurde für jede Messposition berechnet und farblich kodiert dargestellt:
<ul style='font-size:1.0em'>
  <li><span style='color:red; font-weight:bold'>Rot (positive Werte)</span>: Hier steigen oder fallen Temperatur und Salzgehalt gemeinsam – was auf bestimmte ozeanographische Prozesse wie Verdunstung oder das Einströmen von Wassermassen hindeuten kann.</li>
  <li><span style='color:blue; font-weight:bold'>Blau (negative Werte)</span>: Hier verhält sich die Beziehung gegenläufig – steigt die Temperatur, sinkt der Salzgehalt oder umgekehrt, was oft auf Süßwasserzuflüsse, Niederschlag oder Eisschmelze zurückzuführen ist.</li>
</ul>

Die Intensität der Farbe und Größe der Datenpunkte reflektiert die Stärke der Korrelation. Transparente Punkte weisen auf statistisch nicht signifikante Korrelationen hin (p > 0.05).
</p>
""", unsafe_allow_html=True)

# Add toggle between 2D Map and 3D Scatterplot
visualization_type = st.radio(
    "Wählen Sie den Visualisierungstyp:",
    ["3D Scatterplot", "2D Weltkarte"],
    horizontal=True
)

# Depth selection slider
selected_depth = st.select_slider(
    "Wählen Sie die Wassertiefe (in Metern):",
    options=depths
)

# Improved function to load correlation data
@st.cache_data
def load_correlation_data(depth):
    # Try multiple possible paths to handle both local and cloud environments
    possible_paths = [
        f"./correlation_data/correlation_data_{depth}m.csv",
        f"correlation_data/correlation_data_{depth}m.csv",
        f"../correlation_data/correlation_data_{depth}m.csv",
        f"/app/correlation_data/correlation_data_{depth}m.csv",  # Common path in containerized environments
    ]
    
    # Try each path until one works
    for file_path in possible_paths:
        try:
            if Path(file_path).exists():
                data = pd.read_csv(file_path)
                st.success(f"Successfully loaded data from {file_path}")
                
                # Add this right after loading the data
                if data is not None:
                    # Convert coordinate columns to numeric values
                    data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
                    data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')
                    data['correlation'] = pd.to_numeric(data['correlation'], errors='coerce')
                    
                    # Drop any rows with NaN values after conversion
                    data = data.dropna(subset=['latitude', 'longitude', 'correlation'])
                    
                    st.write(f"Data types: {data.dtypes}")
                
                return data
        except Exception:
            continue
    
    # If we get here, none of the paths worked
    st.error(f"Couldn't find correlation data for depth {depth}m. Please check file paths.")
    
    # Show available files in current directory to help debug
    try:
        current_dir = os.getcwd()
        files_in_dir = os.listdir(current_dir)
        st.error(f"Current directory: {current_dir}")
        st.error(f"Files in current directory: {files_in_dir}")
        
        # Check if correlation_data folder exists
        if os.path.exists("correlation_data"):
            correlation_files = os.listdir("correlation_data")
            st.error(f"Files in correlation_data: {correlation_files}")
    except Exception as e:
        st.error(f"Error inspecting directories: {str(e)}")
    
    return None

# Display visualization based on selected type
if visualization_type == "2D Weltkarte":
    # 2D Map visualization (from ocean_map_visualization.py)
    data = load_correlation_data(selected_depth)
    
    if data is not None:
        st.write(f"Anzeige der Daten für Tiefe: {selected_depth}m - {len(data)} Datenpunkte")

        # Filter for minimum correlation
        min_correlation = st.slider("Minimale absolute Korrelation:", 0.0, 1.0, 0.0, 0.01)
        show_significant_only = st.checkbox("Nur signifikante Korrelationen anzeigen")
        
        # Filter the data based on user selections
        filtered_data = data.copy()
        if show_significant_only:
            filtered_data = filtered_data[filtered_data['significant'] == True]
        if min_correlation > 0:
            filtered_data = filtered_data[abs(filtered_data['correlation']) >= min_correlation]
        
        # Prepare the data for visualization
        filtered_data = filtered_data.reset_index(drop=True)
        
        # Add debug information
        st.write(f"Filtered data points: {len(filtered_data)}")
        if len(filtered_data) == 0:
            st.warning("No data points match your filter criteria.")
            # Show a sample of the original data for debugging
            st.write("Sample of original data:")
            st.write(data.head())
        
        # Scale circle size based on correlation strength
        filtered_data['size'] = 5 + 15 * np.abs(filtered_data['correlation'])
        
        # Calculate height to use most of viewport
        map_height = 800
        
        # Create a Plotly figure with a color scale - USING GEO INSTEAD OF MAPBOX
        fig = px.scatter_geo(
            filtered_data,
            lat="latitude",
            lon="longitude",
            color="correlation",
            size="size",
            color_continuous_scale="RdBu_r",  # Red-Blue scale, red for positive, blue for negative
            range_color=[-1, 1],
            height=map_height,
            hover_data=["correlation", "p_value", "count", "significant"]
        )

        # Configure the map layout to show the entire world
        fig.update_geos(
            projection_type="natural earth",  # A simple projection that works well
            showcoastlines=True,
            coastlinecolor="Black",
            showland=True,
            landcolor="lightgray",
            showocean=True,
            oceancolor="lightblue",
            showlakes=True,
            lakecolor="lightblue",
            showcountries=True,
            countrycolor="gray",
            fitbounds="locations"  # Auto-fit to data points
        )

        fig.update_layout(
            height=map_height,
            margin=dict(l=0, r=0, t=0, b=0),
        )

        # Display the map with full width
        st.plotly_chart(fig, use_container_width=True)
        
        # Add this after the plotly chart
        if st.checkbox("Map not displaying correctly? Try alternative visualization"):
            st.subheader("Alternative Visualization")
            # Create a simpler scatter plot as fallback
            alt_fig = px.scatter(
                filtered_data,
                x="longitude", 
                y="latitude",
                color="correlation",
                size="size",
                color_continuous_scale="RdBu_r",
                range_color=[-1, 1],
                hover_data=["correlation", "p_value", "count", "significant"],
                width=1000, 
                height=500
            )
            # Add a grid to represent the world map
            alt_fig.update_layout(
                xaxis=dict(range=[-180, 180], title="Longitude", gridcolor="lightgray"),
                yaxis=dict(range=[-90, 90], title="Latitude", gridcolor="lightgray", scaleanchor="x", scaleratio=1),
                plot_bgcolor="white"
            )
            st.plotly_chart(alt_fig, use_container_width=True)
    else:
        st.error("Keine Daten für die Kartenvisualisierung verfügbar.")
        st.write("Bitte stellen Sie sicher, dass die Datendateien korrekt hochgeladen wurden.")

else:  # 3D Scatterplot visualization (original)
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
        st.error(f"Die Datei '{html_file_path}' wurde nicht gefunden. Bitte überprüfen Sie, ob der Ordner 'saved_plots2' existiert und die Datei enthält.")

# Add a separator between the sections
st.markdown("---")

# Section for the correlation by depth graph (unchanged)
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

st.markdown("<h2 style='font-size:3.0em;'>Fazit aus den Daten</h2>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:1.6em'>
Die Analyse der Temperatur-Salzgehalt-Korrelation zeigt, dass über alle Tiefen hinweg durchschnittlich eine positive Korrelation zwischen Temperatur und Salzgehalt besteht. Dies deutet darauf hin, dass in wärmeren Gewässern tendenziell auch höhere Salzgehalte zu beobachten sind.
Dennoch gibt es in manchen Gebieten die Korrelation umgekehrt zu sein, wie in der Nähe des Äquators und in der Nähe der Pole. Dies könnte auf verschiedene ozeanografische Prozesse zurückzuführen sein.
Schließlich ist außerdem zu erkennen, dass die Korrelation mit zunehmender Tiefe zuerst abnimmt und dann wieder zunimmt. Dies könnte darauf hindeuten, dass in den oberen Wasserschichten andere Prozesse wirken als in den tieferen Schichten.
Die Ergebnisse dieser Analyse könnten wertvolle Hinweise auf die ozeanografischen Prozesse und deren Wechselwirkungen geben, die das Klima und die Ökosysteme der Ozeane beeinflussen.
</p>
""", unsafe_allow_html=True)

st.markdown("Erstellt von: Laurin Klein,2025,Studiengang KIK/AKI, Hochschule Ansbach")
