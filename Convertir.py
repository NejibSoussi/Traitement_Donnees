import pandas as pd
import ast
import tkinter as tk
from tkinter import filedialog
import os

# Créé le tkinter
root = tk.Tk()
root.withdraw()

### Étape 1 : Demander à l'utilisateur de sélectionner un fichier csv
csv_file_path = filedialog.askopenfilename(title="Sélectionner le fichier CSV", filetypes=[("CSV files", "*.csv")])

# Si asucun fichier sélectionné, arrêter le code
if not csv_file_path:
    print("Aucun fichier sélectionné. Action terminée.")
    exit()

# Charger le CSV dans le DataFrame de pandas
df = pd.read_csv(csv_file_path)

### Étape 2 : Aller chercher la colonne contemant les données en format json
json_column_name = 'Champs personnalises'

# Valider que le nom de la colonne existe dans le DataFram pandas
if json_column_name not in df.columns:
    print(f"Column '{json_column_name}' not found in the DataFrame. Exiting.")
    exit()

### Étape 3 : Convertir la représentation sous forme de chaîne de la liste de dictionnaires en une liste réelle
df[json_column_name] = df[json_column_name].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

### Étape 4 : Éclater la liste des dictionnaires en lignes distinctes
df_exploded = df.explode(json_column_name)

### Étape 5 : Extraire les « valeurs » et le « nom » dans des colonnes séparées
df_exploded['values'] = df_exploded[json_column_name].apply(lambda x: x['values'][0] if x and 'values' in x else '')
df_exploded['name'] = df_exploded[json_column_name].apply(lambda x: x['name'] if x and 'name' in x else '')

### Étape 6 : Faire pivoter le DataFrame pour obtenir le résultat souhaité
df_pivoted = df_exploded.pivot_table(index=df_exploded.index, columns='name', values='values', aggfunc='first')

### Étape 7 : Concaténer le DataFrame pivoté avec le DataFrame d'origine
df_fixed = pd.concat([df, df_pivoted], axis=1)

### Étape 8 : Supprimer la colonne d'origine de type JSON
df_fixed = df_fixed.drop(columns=[json_column_name])

### Étape 9 : Enregistrer le DataFrame fixed dans un nouveau fichier CSV
output_csv_path = 'Modifié_' + os.path.basename(csv_file_path)
output_full_path = os.path.join(os.path.dirname(csv_file_path), output_csv_path)
df_fixed.to_csv(output_full_path, index=False)

# Imprimer le chemin complet du fichier CSV corrigé
print(f"Le fichier modifié a été enregistré ici : {output_full_path}")
