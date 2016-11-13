##PsarAU - Lissage et carroyage=group
##Fichier_CSV = file
##Taille_des_carreaux = number 1000
##Rayon_de_lissage = number 15000
##Liste_de_deciles = string NULL
##Grille = file
##Sortie = string
require(btb)
require(foreign)

donnees <- read.csv(Fichier_CSV)
grille<- read.dbf(Grille, as.is = T)

if (Liste_de_deciles == 'NULL') {
listeDeciles <- NULL
} else {
listeDeciles <- as.numeric(strsplit(Liste_de_deciles,",")[[1]])
}

# Lissage des variables
donnees_smooth=kernelSmoothing(dfObservations = donnees,cellSize = Taille_des_carreaux, bandwidth = Rayon_de_lissage, dfCentroids = grille, vQuantiles = listeDeciles )

donnees_smooth$ID <- paste(donnees_smooth$x, donnees_smooth$y,sep = "_")

write.dbf(file=Sortie,donnees_smooth)

