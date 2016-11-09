##PsarAU - Lissage et carroyage=group
##Fichier_DBF = file
##Taille_des_carreaux = number 200
##Rayon_de_lissage = number 800
##SCR = number 2154
##grille_lissee = output vector

# require(foreign)
library(btb)
require(rgdal)

donnees <- read.csv(Fichier_DBF)

# Lissage des variables
donnees_smooth=kernelSmoothing(dfObservations = donnees,cellSize = Taille_des_carreaux, bandwidth = Rayon_de_lissage)

# Creation du fond de carte
grille_lissee=smoothingToGrid(donnees_smooth,as.character(SCR))

