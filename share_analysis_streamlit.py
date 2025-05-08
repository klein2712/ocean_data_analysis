import streamlit as st
import os
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit.components.v1 import html


#NOTE THIS IS A BACKUPF FILE
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

# Function to load correlation data for map visualization
@st.cache_data
def load_correlation_data(depth):
    file_path = f"./correlation_data/correlation_data_{depth}m.csv"
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        st.error(f"Fehler beim Laden der Korrelationsdaten: {str(e)}")
        return None

# Display visualization based on selected type
if visualization_type == "2D Weltkarte":
    # 2D Map visualization using Streamlit's PyDeck
    try:
        data = load_correlation_data(selected_depth)
        
        if data is not None:
            st.write(f"Anzeige der Daten für Tiefe: {selected_depth}m - {len(data)} Datenpunkte")

            # Filter controls
            min_correlation = st.slider("Minimale absolute Korrelation:", 0.0, 1.0, 0.0, 0.01)
            show_significant_only = st.checkbox("Nur signifikante Korrelationen anzeigen")
            
            # Filter data based on user selections
            filtered_data = data.copy()
            if show_significant_only:
                filtered_data = filtered_data[filtered_data['significant'] == True]
            if min_correlation > 0:
                filtered_data = filtered_data[abs(filtered_data['correlation']) >= min_correlation]
            
            # Prepare data for visualization
            if len(filtered_data) > 0:
                # Create color scale (red for positive, blue for negative)
                filtered_data['color'] = filtered_data['correlation'].apply(
                    lambda x: [255, int(255 * (1 - abs(x))), int(255 * (1 - abs(x)))] if x >= 0 
                    else [int(255 * (1 - abs(x))), int(255 * (1 - abs(x))), 255]
                )
                
                # Scale point size based on correlation strength (5-20)
                filtered_data['size'] = 5 + 15 * np.abs(filtered_data['correlation'])
                
                # Create tooltip text
                filtered_data['tooltip'] = filtered_data.apply(
                    lambda row: f"Korrelation: {row['correlation']:.3f}\n" +
                                f"P-Wert: {row['p_value']:.3f}\n" +
                                f"Anzahl: {row['count']}\n" +
                                f"Signifikant: {row['significant']}", 
                    axis=1
                )
                
                # Create PyDeck map
                import pydeck as pdk
                
                # Configure layer
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered_data,
                    get_position=["longitude", "latitude"],
                    get_color="color",
                    get_radius="size * 1000",  # Scale up for visibility
                    pickable=True,
                    opacity=0.7,
                    stroked=False,
                    filled=True,
                    radius_scale=1,
                    radius_min_pixels=3,
                    radius_max_pixels=15,
                )
                
                # Set the initial viewport
                view_state = pdk.ViewState(
                    latitude=0,
                    longitude=0,
                    zoom=1,
                    pitch=0,
                )
                
                # Create deck
                deck = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    map_style="light",
                    tooltip={"text": "{tooltip}"}
                )
                
                # Display the map
                st.pydeck_chart(deck)
                
                # Add a color legend
                st.markdown("""
                <div style="display: flex; align-items: center; margin-top: 10px;">
                    <div style="background: linear-gradient(to right, blue, white, red); height: 20px; width: 200px;"></div>
                    <div style="display: flex; justify-content: space-between; width: 200px; margin-top: 5px;">
                        <span>-1</span>
                        <span>0</span>
                        <span>1</span>
                    </div>
                </div>
                <div style="margin-top: 5px;">
                    <span style="color: blue; font-weight: bold;">Blau</span>: Negative Korrelation | 
                    <span style="color: red; font-weight: bold;">Rot</span>: Positive Korrelation
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Keine Daten gefunden, die den Filterkriterien entsprechen.")
                
    except Exception as e:
        st.error(f"Fehler bei der Kartenvisualisierung für Tiefe {selected_depth}m: {str(e)}")
        st.write("Bitte überprüfen Sie, ob die Datei existiert und korrekt formatiert ist.")

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
