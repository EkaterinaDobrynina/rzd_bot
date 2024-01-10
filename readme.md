1) Установи poetry  
```PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
2) Установи библиотеки
```PowerShell
poetry install
```
3) Заполни `.env` файл
4) Запусти бота
```PowerShell
poetry run python app.py
```