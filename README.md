# Board Game Inventory Tracker

## Overview
The **Board Game Inventory Tracker** is a Python application designed to help users manage their board game collection. It provides a user-friendly GUI for adding, loaning, returning, listing, and deleting games from the inventory. The application uses a SQLite database for data storage and integrates with an external API for barcode lookup.

## Features
- **Add Game**: Add a new game to the inventory using a barcode.
- **Loan Game**: Loan a game to someone and track who borrowed it.
- **Return Game**: Mark a game as returned.
- **List Games**: View all games in the inventory.
- **Delete Game**: Remove a game from the inventory.
- **Barcode Lookup**: Fetch game details using an external API.

## Requirements
- Python 3.7 or higher
- Required Python libraries:
  - `tkinter` (built-in with Python)
  - `requests`
  - `sqlite3` (built-in with Python)

Here is the updated README.md file with the added **Usage**, **File Structure**, and **License** sections:

```markdown
# Board Game Inventory Tracker

## Overview
The **Board Game Inventory Tracker** is a Python application designed to help users manage their board game collection. It provides a user-friendly GUI for adding, loaning, returning, listing, and deleting games from the inventory. The application uses a SQLite database for data storage and integrates with an external API for barcode lookup.

## Features
- **Add Game**: Add a new game to the inventory using a barcode.
- **Loan Game**: Loan a game to someone and track who borrowed it.
- **Return Game**: Mark a game as returned.
- **List Games**: View all games in the inventory.
- **Delete Game**: Remove a game from the inventory.
- **Barcode Lookup**: Fetch game details using an external API.

## Requirements
- Python 3.7 or higher
- Required Python libraries:
  - `tkinter` (built-in with Python)
  - `requests`
  - `sqlite3` (built-in with Python)

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Boardgameinventory
   ```

2. Set up a virtual environment (optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install requests
   ```

4. Create a config.py file with  APIyour key and URL:
   ```python
   API_KEY = 'your_api_key_here'
   API_URL = 'https://api.barcodelookup.com/v3/products'
   ```

## Usage
Run the application:
```bash
python main.py
```

## File Structure
- main.py: Contains the main application logic and GUI.
- api.py: Handles barcode lookup using an external API.
- db.py: Manages database operations.
- config.py: Stores API configuration (excluded from version control).
- games.db: SQLite database file (excluded from version control).
- .gitignore: Specifies files to exclude from version control.


## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/MatthewStebbins/boardgame_inventory.git
   cd Boardgameinventory