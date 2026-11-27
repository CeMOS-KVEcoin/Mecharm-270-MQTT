import json
import logging

import paho.mqtt.client as mqtt


class MqttService:
    def __init__(
        self,
        *,
        client_id,
        username,
        password,
        broker,
        port,
        topic_cmd,
        topic_status,
        topic_connection,
        on_command,
    ):
        self.topic_cmd = topic_cmd
        self.topic_status = topic_status
        self.topic_connection = topic_connection
        self.on_command = on_command

        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set(username, password)

        # Broker meldet "offline", falls die Verbindung unerwartet abbricht.
        self.client.will_set(
            topic_connection,
            payload=self._connection_payload(online=False),
            qos=1,
            retain=True,
        )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.broker = broker
        self.port = port

    def start(self):
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()

    def stop(self):
        self.publish_connection(online=False)
        self.client.loop_stop()
        self.client.disconnect()

    def publish_status(self, message, state, angles=None):
        payload = {
            "state": state,
            "msg": message,
            "angles": angles,
        }
        self.client.publish(self.topic_status, json.dumps(payload))

    def publish_connection(self, *, online):
        payload = self._connection_payload(online=online)
        self.client.publish(
            self.topic_connection,
            payload,
            qos=1,
            retain=True,
        )

    def _connection_payload(self, *, online):
        return json.dumps({
            "state": "online" if online else "offline",
            "online": online,
        })

    def _on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            logging.error("MQTT-Verbindung fehlgeschlagen: rc=%s", rc)
            return

        logging.info("MQTT verbunden")
        client.subscribe(self.topic_cmd)
        self.publish_connection(online=True)

    def _on_disconnect(self, client, userdata, rc):
        if rc == 0:
            logging.info("MQTT sauber getrennt")
        else:
            logging.warning("MQTT-Verbindung unerwartet getrennt: rc=%s", rc)

    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            logging.exception("Ungültige JSON-Nachricht empfangen")
            self.publish_status("invalid JSON", "error")
            return

        if not isinstance(payload, dict):
            self.publish_status("Nachricht muss ein JSON-Objekt sein", "error")
            return

        # MQTT-Service kennt die Roboterbefehle nicht. Er reicht sie weiter.
        try:
            self.on_command(payload)
        except Exception:
            logging.exception("Fehler bei der Verarbeitung des Befehls")
            self.publish_status("command handler failed", "error")