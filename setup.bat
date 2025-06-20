@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
echo FastAPI environment setup complete. Run "call .venv\Scripts\activate" to start using it.
