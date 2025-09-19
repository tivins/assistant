# Architecture du Terminal AI Assistant

## Vue d'ensemble

Le projet a été refactorisé pour séparer les responsabilités en plusieurs classes spécialisées, rendant le code plus maintenable et modulaire.

## Structure des classes

### 1. TerminalAIAssistant (main.py)
**Responsabilité principale :** Orchestration et interface utilisateur
- Coordonne les interactions entre les différentes classes
- Gère la boucle principale de l'application
- Interface utilisateur (affichage, input/output)

### 2. AIClient (assistant/ai_client.py)
**Responsabilité :** Communication avec Ollama
- Gestion des modèles AI
- Envoi des requêtes à Ollama
- Gestion des erreurs de connexion
- Changement de modèles

### 3. ConversationManager (assistant/conversation_manager.py)
**Responsabilité :** Gestion de l'historique des conversations
- Ajout de messages à l'historique
- Récupération de l'historique
- Effacement de l'historique
- Gestion des timestamps

### 4. ArchiveManager (assistant/archive_manager.py)
**Responsabilité :** Sauvegarde et archivage des conversations
- Archivage automatique en temps réel
- Sauvegarde manuelle des conversations
- Gestion des sessions
- Liste et visualisation des archives
- Reprise de conversations archivées

### 5. ScriptExecutor (assistant/script_executor.py)
**Responsabilité :** Exécution des scripts
- Découverte des scripts disponibles
- Exécution de différents types de scripts (Python, Bash, Batch, PowerShell)
- Gestion des timeouts et erreurs
- Affichage des résultats

### 6. CommandProcessor (assistant/command_processor.py)
**Responsabilité :** Traitement des commandes spéciales
- Parsing des commandes utilisateur
- Routage vers les bonnes classes
- Gestion des commandes d'aide
- Sauvegarde/chargement de conversations

## Avantages de cette architecture

### Séparation des responsabilités
- Chaque classe a une responsabilité claire et unique
- Plus facile à maintenir et déboguer
- Code plus lisible et organisé

### Réutilisabilité
- Les classes peuvent être réutilisées dans d'autres projets
- Facilite les tests unitaires
- Permet l'extension facile de fonctionnalités

### Maintenabilité
- Modifications isolées dans des classes spécifiques
- Réduction de la complexité du code principal
- Plus facile à comprendre pour de nouveaux développeurs

## Flux de données

```
Utilisateur → TerminalAIAssistant → CommandProcessor
                ↓
        ConversationManager ← ArchiveManager
                ↓
            AIClient (Ollama)
                ↓
        ScriptExecutor (si nécessaire)
```

## Structure des fichiers

```
assistant2/
├── main.py                    # Classe principale et point d'entrée
├── assistant/
│   ├── __init__.py           # Package initialization
│   ├── ai_client.py          # Communication avec Ollama
│   ├── archive_manager.py    # Gestion des archives
│   ├── command_processor.py  # Traitement des commandes
│   ├── conversation_manager.py # Gestion des conversations
│   └── script_executor.py    # Exécution des scripts
├── scripts/                  # Scripts exécutables
├── conversations/            # Archives des conversations
└── requirements.txt          # Dépendances
```

## Utilisation

Le code refactorisé maintient la même interface utilisateur qu'avant, mais avec une architecture beaucoup plus propre et maintenable.
