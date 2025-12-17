# bralma_NLP
Brent, Alex, Mauro. NLP Project


### Maak een nieuwe virtual environment aan (altijd met Python 3.11)
rm -rf .venv;
python3.11 -m pip cache purge;
python3.11 -m venv .venv;

### Activeer de virtual environment
source .venv/bin/activate;

### Upgrade pip en installeer alle requirements (voor Python 3.11!)
python3.11 -m pip install --upgrade pip;
python3.11 -m pip install -r requirements.txt;

### Run de frontend (Streamlit)
streamlit run Frontend.py;

Voor Windows (Git Bash):

```bash
# Verwijder oude venv
rm -rf .venv

# Als python3.11 in PATH: (anders gebruik volledig pad naar python.exe)
/c/Users/yourusername/AppData/Local/Programs/Python/Python311/python.exe -m venv .venv

# Activeer de venv in Git Bash
source .venv/Scripts/activate

# Upgrade pip en installeer requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run de frontend
python -m streamlit run Frontend.py
```

Belangrijke opmerkingen:

- `python -m pip cache purge` werkt alleen op pip >= 23.1. Je kunt deze stap overslaan of eerst `python -m pip install --upgrade pip` uitvoeren.
- Als je meerdere Python-versies hebt, gebruik het volledige pad naar de gewenste `python.exe`

Werkt `.venv` automatisch in `.py` bestanden?

- Nee — welk Python-interpreter een `.py` bestand gebruikt hangt af van hoe je het uitvoert. Om zeker te zijn dat je venv gebruikt:
	- Activeer de venv (`source .venv/bin/activate` of `.\.venv\Scripts\Activate.ps1`) en run je commando's (bijv. `python -m streamlit run Frontend.py`).
	- Of gebruik het venv-python expliciet: `./.venv/bin/python script.py` (bash) of `.venv\Scripts\python.exe script.py` (Windows).

Deze README bevat nu copy/paste-commando's voor macOS/Linux (bash), Windows Git Bash.