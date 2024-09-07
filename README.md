Frontend bot for other bot that tracks big buys and sells of tokens

How to setup
1. Create virtual environment
```
python -m venv venv
```
2. Activate virtual environment
```
source venv/bin/activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Create .env file and add the following variables:
```
BOT_TOKEN=<your_token>
```
5. Run the bot
```
python main.py

Thats all, you can now use the bot
```
/start - start the bot
/add <token_contract> - add a token contract to the database
/remove <token_contract> - remove a token contract from the database
/list - list all token contracts in the database
```

