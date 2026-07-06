from flask import Flask, render_template, request, jsonify
from chatbot import WebsiteChatbot

app = Flask(__name__)

bot = WebsiteChatbot()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"answer": "Please type a question first."})

    answer = bot.answer(question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
