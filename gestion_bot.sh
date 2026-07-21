#!/bin/bash

# 1. Nettoie automatiquement les sessions mortes
screen -wipe > /dev/null 2>&1

# 2. Vérifie si une session active nommée "monbot" existe déjà
if screen -list | grep -q "monbot"; then
    echo "Le bot tourne déjà dans une session screen."
    echo "Pour le rejoindre, tapez : screen -r monbot"
else
    # 3. Lance le bot dans une nouvelle session en arrière-plan
    echo "Lancement du bot dans une nouvelle session screen..."
    screen -dmS monbot ./start.sh
    echo "Bot lancé avec succès !"
fi
