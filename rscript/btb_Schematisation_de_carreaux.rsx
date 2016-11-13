##PsarAU - Lissage et carroyage=group
##Fichier_CSV = file
##Taille_des_carreaux = number 200
##Rayon_de_lissage = number 800
##Liste_de_deciles = string NULL
##SCR = number 2154
##grille_lissee = output vector

# require(foreign)
library(btb)
require(rgdal)

donnees <- read.csv(Fichier_CSV)

if (Liste_de_deciles == 'NULL') {
listeDeciles <- NULL
} else {
listeDeciles <- as.numeric(strsplit(Liste_de_deciles,",")[[1]])
}

# Lissage des variables
donnees_smooth=kernelSmoothing(dfObservations = donnees,cellSize = Taille_des_carreaux, bandwidth = Rayon_de_lissage , vQuantiles = listeDeciles )

# Creation du fond de carte
grille_lissee=smoothingToGrid(donnees_smooth,as.character(SCR))

