# 💎 Spezifikation: Generativer Dual-Color Ohrring Designer

## I. Zielsetzung

Entwicklung eines Web-basierten Tools zur generativen Erstellung von zweifarbigen Mandala-Ohrring-Designs. Das System soll eine "Endlos-Galerie" von Mustern bieten, die nach parametrischen Vorgaben und Zufall generiert werden, die Reproduzierbarkeit der Designs gewährleisten und fertige, AMS-kompatible 3D-Druckdateien (STLs) ausgeben.

## II. System-Architektur & Toolchain

| Komponente | Funktion | Technologie-Vorschlag |
| :--- | :--- | :--- |
| **Frontend** | Benutzer-Interface, Galerie, Parameter-Eingabe. | HTML/CSS, JavaScript (React/Vue.js) |
| **Backend/API** | Logik zur Mustergenerierung, Speicherung der Parameter. | Python (Flask/Django) |
| **Generative Engine** | Erstellung der Mandala-Muster als 2D-Heightmap. | Python (NumPy, Pillow/PIL) |
| **3D-Konvertierung** | Umwandlung der Heightmap in 3D-Geometrie und Aufsplittung in zwei separate STL-Dateien. | Python (Trimesh) |

## III. Kernfunktionen (Frontend)

### 1. ⚙️ Design-Parameter (Input)

Der Benutzer kann folgende **globale Parameter** für alle generierten Muster festlegen:

* **Geometrie:**
    * **Ohrstecker-Durchmesser (Größe):** $D$ (z.B. $8 \, \text{mm}$ bis $15 \, \text{mm}$)
    * **Gesamthöhe der Scheibe:** $H_{\text{gesamt}}$ (z.B. $2 \, \text{mm}$ bis $3 \, \text{mm}$)
    * **Relief-Tiefe (Kontrasthöhe):** $H_{\text{muster}}$ (z.B. $0.5 \, \text{mm}$ bis $1.5 \, \text{mm}$)
* **Generierung:**
    * **Zufalls-Seed (Optional):** Für die Reproduktion bestimmter Muster.

### 2. 🖼️ Endlos-Galerie & Navigation

* **Generierung:** Auf Knopfdruck ("Weiter", "Neues Muster") wird ein neues, zufälliges Mandala-Muster basierend auf den aktuellen globalen Parametern erzeugt und visualisiert.
* **Navigation:** Schaltflächen zum Erstellen des **nächsten** Musters oder Zurückkehren zum **letzten** Muster.
* **Ansicht:** 3D-Vorschau der generierten Scheibe mit **simulierten zwei Farben** (z.B. Basis: Beige, Muster: Grün), um den visuellen Kontrast zu beurteilen.

### 3. ⭐ Speicher- & Export-Funktion

* **Muster Speichern ("Merken"):** Eine Schaltfläche, um das aktuell angezeigte Muster zu einer persönlichen Liste hinzuzufügen.
    * **Gespeichert wird:** Der generierende Seed und alle zur Erstellung notwendigen Parameter.
* **Export:**
    * **Generierung:** Erstellt die druckfertigen STL-Dateien für das ausgewählte Muster.
    * **Download-Format (AMS-Kompatibel):** Ein ZIP-Archiv, das **zwei separate STL-Dateien** enthält:
        1.  **`Basis_Scheibe.stl`** (Die untere, dicke Scheibe)
        2.  **`Muster_Relief.stl`** (Das erhabene/versenkte Mandala-Muster)

## IV. Technische Details (Backend / Generative Engine)

### 1. 🐍 Mandala-Generierung

* Die Muster basieren auf **Polarkoordinaten-Funktionen** (Radial-Symmetrie).
* Die generative Logik soll verschiedene Muster-Parameter nutzen (z.B. Anzahl der Achsen, Frequenz, Amplituden-Gewichtung), die über den Zufalls-Seed gesteuert werden.
* **Output:** Eine Graustufen-Heightmap (PNG/Array).

### 2. ⚙️ STL-Konvertierung (Dual-Color Split)

Das 3D-Konvertierungsskript muss die Heightmap in zwei separate, druckbare Meshes zerlegen:

1.  **Basis-Scheibe (Farbe 1):** Die Hauptscheibe mit der Höhe $H_{\text{gesamt}} - H_{\text{muster}}$.
2.  **Muster-Relief (Farbe 2):** Das eigentliche Mandala-Muster, das exakt auf die Oberfläche der Basis-Scheibe passt und die Höhe $H_{\text{muster}}$ hat.

*Hinweis: Die finale STL muss an der Rückseite eine Aussparung oder eine Befestigung für den Ohrstecker-Pin enthalten (z.B. eine kleine zylindrische Vertiefung).*