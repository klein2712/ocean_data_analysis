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
<h2 style='font-size:3.0em'>Ziel des Projekts</h2>
<p style='font-size:1.6em'>
Im Rahmen des Moduls <b>„KI in den Lifesciences“</b> verfolgt das vorliegende Projekt das Ziel, Meeresdaten systematisch auszuwerten und insbesondere die Korrelation zwischen Temperatur und Salzgehalt des Ozeans zu untersuchen. Die Analyse basiert auf Messdaten der <b>World Ocean Database</b>, die für sämtliche Breiten- und Längengrade sowie verschiedene Tiefenebenen des Ozeans vorliegen. Eine weiterführende, freiwillige Fragestellung bestand darin, die Daten gezielt auf potenzielle Muster oder Auffälligkeiten hin zu analysieren, um neue wissenschaftliche Erkenntnisse über ozeanografische Zusammenhänge zu gewinnen.
</p>

<h2 style='font-size:3.0em'>Datensatz</h2>
<p style='font-size:1.6em'>
Für die Untersuchung wurde der frei zugängliche Datensatz des <b>World Ocean Atlas</b> ausgewählt. Es wurde gezielt der Datensatz aus dem Jahr 2023 herangezogen, da dieser den aktuellsten Stand der verfügbaren Messungen repräsentiert. Der Datensatz umfasst für jedes Längen- und Breitengradpaar Messstationen auf unterschiedlichen Tiefenmetern, die eine Vielzahl ozeanografischer Parameter wie Salzgehalt, Temperatur, Stickstoffgehalt und weitere chemische sowie physikalische Größen erfassen. Im Rahmen dieses Projekts lag der Fokus insbesondere auf den Parametern Temperatur und Salzgehalt, da für diese Variablen die umfangreichsten und zuverlässigsten Messreihen vorliegen. Die verwendeten Werte stellen Durchschnittsdaten (Averages) aus dem Zeitraum 2015 bis 2022 dar, was sowohl die Aktualität als auch die Präzision der Analyse gewährleistet. Über 95 % der Messstationen liefern für Temperatur und Salzgehalt valide Daten, sodass eine robuste und repräsentative Auswertung dieser beiden Schlüsselparameter möglich ist.
</p>""", unsafe_allow_html=True)

# Define available depth levels
depths = [0, 50, 100, 150, 200, 300, 400, 500, 750, 1000, 1250, 1500, 1750, 1950]

# Section for scatter plots
st.markdown("<h2 style='font-size:3.0em;'>Korrelation: Salzgehalt und Temperatur (T-S Korrelation) für verschiedene Meerestiefen</h2>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:1.6em'>
Die folgenden Grafiken zeigen die Temperatur-Salzgehalt-Korrelation (T-S-Korrelation) für verschiedene Meerestiefen.<br>
Die Korrelation wurde mittels Pearson-Korrelation berechnet. Der Korrelationswert liegt zwischen -1 und 1: Ein positiver Wert bedeutet, dass beide Parameter gemeinsam steigen oder fallen (z.&nbsp;B. steigt die Temperatur, steigt auch der Salzgehalt). Ein negativer Wert zeigt an, dass ein Anstieg des einen Parameters mit einem Rückgang des anderen einhergeht (z.&nbsp;B. steigt die Temperatur, sinkt der Salzgehalt).<br>
Wählen Sie eine Tiefe, um die entsprechende Visualisierung anzuzeigen.<br>
<b>ANMERKUNG:</b> Die Legende in den Grafiken ist fehlerhaft. <span style='color:red;'>Rot</span> steht für positive Korrelation, <span style='color:blue;'>Blau</span> für negative Korrelation.
</p>
""", unsafe_allow_html=True)

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


st.markdown("<h2 style='font-size:3.0em;'>Fazit aus den Graphen</h2>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:1.6em'>
Die Analyse der Temperatur-Salzgehalt-Korrelation zeigt, dass über alle Tiefen hinweg durchschnittlich eine positive Korrelation zwischen Temperatur und Salzgehalt besteht. Dies deutet darauf hin, dass in wärmeren Gewässern tendenziell auch höhere Salzgehalte zu beobachten sind.
Dennoch gibt es in manchen Gebieten die Korrelation umgekehrt zu sein, wie in der Nähe des Äquators und in der Nähe der Pole. Dies könnte auf verschiedene ozeanografische Prozesse zurückzuführen sein.
Schließlich ist außerdem zu erkennen, dass die Korrelation mit zunehmender Tiefe zuerst abnimmt und dann wieder zunimmt. Dies könnte darauf hindeuten, dass in den oberen Wasserschichten andere Prozesse wirken als in den tieferen Schichten.
Die Ergebnisse dieser Analyse könnten wertvolle Hinweise auf die ozeanografischen Prozesse und deren Wechselwirkungen geben, die das Klima und die Ökosysteme der Ozeane beeinflussen.
</p>
""", unsafe_allow_html=True)
    #NOTE: For first plots we may want to use st.maps
