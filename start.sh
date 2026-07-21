#!/bin/bash

# =========================================================================
# CONFIGURATION DES ACCÈS HIGHRISE (Remplissez ces valeurs)
# =========================================================================
ROOM_ID="69d017f93f0865c7eb8c9f16"
API_TOKEN="d9e3af99381568871073f37371a8db05182c7c3938a2f4e417cbdc6d67cf4be2"

echo "🚀 Démarrage du gestionnaire de connexion Highrise..."
echo "Presser [CTRL+C] pour arrêter définitivement le bot."
echo "--------------------------------------------------"

# Boucle de reconnexion permanente
while true
do
    echo "📅 [$(date +'%T')] Tentative de connexion au salon Highrise..."
    
    # Exécution via la commande native du SDK Highrise
    highrise bot:SuperBotHighrise "$ROOM_ID" "$API_TOKEN"
    
    # Récupération du code d'arrêt si le bot se déconnecte ou crash
    EXIT_CODE=$?
    
    echo "⚠️ [$(date +'%T')] Le bot s'est déconnecté (Code de sortie : $EXIT_CODE)"
    echo "⏳ Reconnexion automatique initiée par le script .sh dans 5 secondes..."
    
    # Pause de sécurité avant de retenter la connexion
    sleep 5
    echo "--------------------------------------------------"
done
