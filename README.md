#Traitement_Donnees
##Traiter des données CSV pour obtenir des graphiques

##Guide d'utilisation de l'application Dash
Cette application Dash a été développée pour permettre aux utilisateurs d'explorer et de visualiser facilement les données contenues dans un fichier CSV. L'application offre une interface conviviale avec des menus déroulants pour la sélection des colonnes, des filtres et des types de graphiques.

##Prérequis
Avant d'utiliser cette application, assurez-vous d'avoir installé Python ainsi que les bibliothèques requises. Vous pouvez installer les dépendances en exécutant les commandes suivantes :

pip install dash 
pip install pandas 
pip install plotly

##Utilisation
#Chargement du fichier CSV :
Lorsque vous lancez l'application, une boîte de dialogue de sélection de fichier apparaîtra automatiquement. Sélectionnez le fichier CSV contenant vos données.

#Sélection des colonnes :
Une fois le fichier chargé, vous verrez une liste déroulante vous permettant de sélectionner la colonne à utiliser comme axe x pour le graphique.

#Sélection des filtres :
Utilisez les menus déroulants des colonnes de filtre pour sélectionner les colonnes sur lesquelles vous souhaitez filtrer les données. Après avoir sélectionné une colonne de filtre, une liste déroulante des valeurs uniques disponibles dans cette colonne apparaîtra. Vous pouvez sélectionner une ou plusieurs valeurs pour filtrer les données.

#Sélection du type de graphique :
Utilisez le menu déroulant pour sélectionner le type de graphique que vous souhaitez afficher. Les options disponibles incluent : Nuage de points, Histogramme, Histogramme Empilé, Line Chart, Box Plot, Violin Plot, 3D Scatter Plot, Graphique Circulaire et Graphique Donut.

#Affichage du graphique :
Une fois que vous avez sélectionné les options souhaitées, le graphique correspondant sera automatiquement généré et affiché dans la zone de sortie.

#Interactivité :
Vous pouvez interagir avec le graphique en utilisant les fonctionnalités natives de Plotly. Par exemple, zoomer, faire défiler, survoler pour obtenir des informations détaillées, etc.

#Réinitialisation des filtres :
Pour réinitialiser les filtres sélectionnés, il suffit de décocher toutes les options sélectionnées dans les menus déroulants des filtres.

##Notes supplémentaires
Cette application est conçue pour fonctionner avec des fichiers CSV. Assurez-vous que vos données sont correctement formatées dans un fichier CSV avant de les charger dans l'application.
