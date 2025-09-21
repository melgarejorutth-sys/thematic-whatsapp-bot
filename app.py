import os
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "Eres un asesor amable de Thematic.pe (regalos temáticos personalizados en Perú). "
    "Responde breve y útil. Ofrece opciones por categoría (Dragon Ball, One Piece, Anime, "
    "parejas, cumpleaños, corporativos). Pide detalles clave: personaje, edad, presupuesto, "
    "fecha de entrega y ciudad. Explica envíos (Olva, Shalom u otros couriers nacionales) "
    "y recojo en taller en Breña si aplica. Si piden precios, da rangos estimados y ofrece "
    "enviar catálogo con fotos si comparten correo o Instagram. Si algo no sabes, sé honesto "
    "y deriva a un asesor humano."
)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "Thematic WhatsApp Bot"})

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming = request.form.get("Body", "").strip()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": incoming or "Hola"},
    ]
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        reply_text = completion.choices[0].message.content.strip()
    except Exception as e:
        reply_text = ("Lo siento, tuve un problema con la IA. "
                      "¿Puedes repetir tu consulta o escribir 'asesor' para hablar con una persona?")
        print("OpenAI error:", e)

    twiml = MessagingResponse()
    twiml.message(reply_text)
    return str(twiml)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
