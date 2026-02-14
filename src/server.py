from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__)
GAMES_DIR = os.path.join(os.getcwd(), "remote_storage")
games_db = [
    {
        "id": 1, 
        "name": "Game", 
        "filename": "Game.zip", 
        "exe_name": "Game.exe"
    }
]

@app.route('/games')
def get_games():
    return jsonify(games_db)

@app.route('/download/<filename>')
def download_game(filename):
    return send_from_directory(GAMES_DIR, filename)

if __name__ == '__main__':
    if not os.path.exists(GAMES_DIR):
        os.makedirs(GAMES_DIR)
        print(f"Created {GAMES_DIR}. Put your Unity ZIPs here!")
    app.run(port=PORT, debug=True)
