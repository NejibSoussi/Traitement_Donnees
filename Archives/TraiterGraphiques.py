import pandas as pd
import plotly.express as px
import plotly.io as pio
import tkinter as tk
from tkinter import filedialog, simpledialog

# Fonction pour afficher une boîte de dialogue de sélection de colonnes
def select_columns(columns, title):
    selected_columns = simpledialog.askstring(title, f"Sélectionner les colonnes (séparées par de virgules):\n{', '.join(columns)}", initialvalue=', '.join(columns))
    if selected_columns:
        return [col.strip() for col in selected_columns.split(',')]
    return None

# Créer une fenêtre racine tkinter
root = tk.Tk()
root.withdraw()

### Étape 1 : Demander à l'utilisateur de sélectionner un fichier CSV
csv_file_path = filedialog.askopenfilename(title="Sélectionner le fichier CSV", filetypes=[("CSV files", "*.csv")])

# Si asucun fichier sélectionné, arrêter le code
if not csv_file_path:
    print("Aucun fichier sélectionné. Action terminée.")
    exit()

# Charger le CSV dans le DataFrame de pandas
df = pd.read_csv(csv_file_path)

### Étape 2 : Demander à l'utilisateur de sélectionner le mode simple ou avancé
mode = simpledialog.askstring("Selectionner le mode souhaité", "Entrer le mode (simple/avance):").lower()

### Étape 3 : Extraire toutes les colonnes du fichier CSV et séparez-les en fonction du type de variable
continuous_columns = [col for col in df.columns if pd.to_numeric(df[col], errors='coerce').notna().all()]
categorical_columns = [col for col in df.columns if col not in continuous_columns]

# Afficher une boîte de dialogue pour permettre aux utilisateurs de sélectionner des colonnes
selected_continuous = select_columns(continuous_columns, "Selectionner des variables continues")
selected_categorical = select_columns(categorical_columns, "Selectionner des variables discontinues")

if selected_continuous is not None and selected_categorical is not None:
    continuous_columns = selected_continuous
    categorical_columns = selected_categorical

### Étape 4 : Obtenir tous les graphiques possibles selon la sélection de l'utilisateur
## Étape 4.1 : Obtenir tous les graphiques possible de 2 variables
if mode == "simple":
    if selected_continuous is not None and selected_categorical is not None:
        for col1 in selected_categorical:
            for col2 in selected_continuous:
                if col1 != col2:
                    fig = px.scatter(df, x=col1, y=col2, title=f"{col1} vs {col2}")
                    pio.show(fig)

    if selected_continuous is not None:
        for col1 in selected_continuous:
            for col2 in selected_continuous:
                if col1 != col2:
                    fig = px.histogram(df, x=col1, color=col2, title=f"{col1} vs {col2}")
                    pio.show(fig)
    
    if selected_categorical is not None:
        for col1 in selected_categorical:
            for col2 in selected_categorical:
                if col1 != col2:
                    # Créer un DataFrame pour l'histogramme empilé à 100 %
                    stacked_df = pd.crosstab(df[col1], df[col2], normalize='index').reset_index()

                    # Multipliez les valeurs par 100 pour les convertir en pourcentages
                    stacked_df.iloc[:, 1:] *= 100

                    # Faire fondre le DataFrame pour le traçage
                    melted_df = pd.melt(stacked_df, id_vars=col1, var_name=col2, value_name='Percentage')

                    # Tracer un histogramme empilé à 100 %
                    fig = px.bar(melted_df, x=col1, y='Percentage', color=col2, barmode='stack',
                                labels={col1: col1, 'Percentage': 'Percentage (%)'},
                                title=f"{col1} vs {col2} (100% Stacked Column)")
                    pio.show(fig)

## Étape 4.2 : Obtenir tous les graphiques possible de 3 variables
else:
    if selected_categorical is not None:
        for col1 in selected_categorical:
            for col2 in selected_categorical:
                for col3 in selected_categorical:
                    if col1 != col2 and col1 != col3 and col2 != col3:
                        # Créer un DataFrame pour l'histogramme empilé à 100 %
                        stacked_df = pd.crosstab([df[col1], df[col2]], df[col3], normalize='index').reset_index()

                        # Multipliez les valeurs par 100 pour les convertir en pourcentages
                        stacked_df.iloc[:, 2:] *= 100

                        # Faire fondre le DataFrame pour le traçage
                        melted_df = pd.melt(stacked_df, id_vars=[col1, col2], var_name=col3, value_name='Percentage')

                        # Tracer un histogramme empilé à 100 % avec 3 variables
                        fig = px.bar(melted_df, x=col1, y='Percentage', color=col3, facet_col=col2, barmode='stack',
                                    labels={col1: col1, 'Percentage': 'Percentage (%)'},
                                    title=f"{col1} vs {col2} vs {col3} (100% Stacked Column)")
                        pio.show(fig)