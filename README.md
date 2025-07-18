# Board Game Inventory Tracker

## Overview
The **Board Game Inventory Tracker** is a Python application designed to help users manage their board game collection. It provides a user-friendly GUI for adding, loaning, returning, listing, and deleting games from the inventory. The application uses a SQLite database for data storage and integrates with an external API for barcode lookup.

## Features
- **Add Game**: Add a new game to the inventory using a barcode.
- **Bulk Upload**: Add multiple games at once by scanning location and game barcodes.
- **Loan Game**: Loan a game to someone and track who borrowed it.
- **Return Game**: Mark a game as returned.
- **List Games**: View all games in the inventory.
- **Delete Game**: Remove a game from the inventory.
- **Barcode Lookup**: Fetch game details using an external API.
- **Export Games**: Export your game collection to CSV or Excel files.
- **Import Games**: Import games from CSV or Excel files.

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
   git clone https://github.com/MatthewStebbins/boardgame_inventory.git
   cd Boardgameinventory
   ```

2. Set up a virtual environment (optional):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # On Mac/Linux: source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install requests
   ```

4. Create a config.py file with your API key and URL (if using BarcodeLookup API):
   ```python
   API_KEY = 'your_api_key_here'
   API_URL = 'https://api.barcodelookup.com/v3/products'
   ```
   Or, if using RapidAPI (default in code):
   ```python
   RAPIDAPI_KEY = 'your_rapidapi_key_here'
   RAPIDAPI_HOST = 'barcodes1.p.rapidapi.com'
   RAPIDAPI_URL = 'https://barcodes1.p.rapidapi.com/'
   ```

## Usage
Run the application:
```bash
python main.py
```

## File Structure
- main.py: Launches the application and GUI.
- ui.py: Contains the BoardGameApp class and all GUI logic, including bulk upload, export/import features.
- api.py: Handles barcode lookup using an external API (RapidAPI or BarcodeLookup).
- db.py: Manages database operations (add, loan, return, delete, list, etc.).
- styles.py: Custom styles and widgets for the UI.
- config.py: Stores API configuration (excluded from version control).
- games.db: SQLite database file (excluded from version control).
- .gitignore: Specifies files to exclude from version control.
- LICENSE: MIT License for the project.


## License
This project is licensed under the MIT License. See the LICENSE file for details.