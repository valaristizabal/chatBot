from twilio.rest import Client
from flask import Flask, request
import os

# Configuración de Twilio
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

app = Flask(__name__)

# Almacena el estado de la conversación
conversaciones = {}
@app.route("/whatsapp", methods=['POST'])
def reply_whatsapp():
    # Recibir el mensaje enviado
    incoming_msg = request.values.get('Body', '').lower()
    sender = request.values.get('From')

    # Obtener el estado de la conversación
    estado = conversaciones.get(sender, 0)


    if estado == 0:
        response = "¡Hola! ¿Es usted un supermercado o un restaurante?"
        conversaciones[sender] = 1
    elif estado == 1:
        if 'supermercado' in incoming_msg:
            response = "Entendido. ¿Cuál es el nombre de su establecimiento?"
            conversaciones[sender] = 2  # Cambiar al siguiente estado
        elif 'restaurante' in incoming_msg:
            response = "Gracias por su disposición. ¿Cuál es el nombre de su restaurante?"
            conversaciones[sender] = 2  # Cambiar al siguiente estado
        else:
            response = "Por favor, indique si es un supermercado o un restaurante."
    elif estado == 2:
        establecimiento = incoming_msg.capitalize()
        conversaciones[sender] = {'nombre': establecimiento, 'direccion': None}
        response = f"Gracias, {establecimiento}. Ahora, por favor, proporcione la dirección de su establecimiento."
    elif isinstance(estado, dict) and estado.get('direccion') is None:
        if 'cra.' in incoming_msg or 'calle' in incoming_msg or 'barrio' in incoming_msg:
            conversaciones[sender]['direccion'] = incoming_msg
            response = "Lo siento, no pude determinar la ubicación a partir de la dirección proporcionada. Por favor, intente proporcionar una dirección más detallada."
        else:
            conversaciones[sender]['direccion'] = incoming_msg
            response = "Gracias por la dirección. Estamos revisando su solicitud."
            del conversaciones[sender]  # Finaliza la conversación
    else:
        response = "Gracias por su información. Si necesita más ayuda, no dude en preguntar."

    # Envía la respuesta
    client.messages.create(
        from_='whatsapp:+14155238886',  # Número de WhatsApp de Twilio
        body=response,
        to=sender  # Número de WhatsApp del usuario que envió el mensaje
    )

    return 'Message sent'

if __name__ == "__main__":
    app.run(debug=True)
