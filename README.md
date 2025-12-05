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