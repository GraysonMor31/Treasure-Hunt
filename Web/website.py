import logging
import os
from flask import Flask, request, jsonify, send_from_directory

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Website:
    @staticmethod
    def create_app():
        app = Flask(__name__)
        return app

    app = create_app.__func__()

    @app.route("/get_state", methods=["GET"])
    def get_state():
        return jsonify({"result": "state"})

    @app.route("/join_game", methods=["POST"])
    def join_game():
        data = request.get_json()
        player_name = data.get("player_name")
        return jsonify({"result": f"joined as {player_name}"})

    @app.route("/leave_game", methods=["POST"])
    def leave_game():
        data = request.get_json()
        player_name = data.get("player_name")
        return jsonify({"result": f"left as {player_name}"})

    @app.route("/update_clients", methods=["POST"])
    def update_clients():
        data = request.get_json()
        clients = data.get("clients")
        return jsonify({"result": f"updated clients: {clients}"})

    @app.route("/")
    def serve_index():
        return send_from_directory(os.path.dirname(__file__), "index.html")

    @staticmethod
    def run():
        Website.app.run(host='0.0.0.0',port=3003, debug=True, use_reloader=False)

if __name__ == "__main__":
    Website.run()