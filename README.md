# Mecharm-270-MQTT

Programm zum Ausführen verschiedener Skills mit dem Mecharm 270-Pi Roboter-Arm von Elephant Robotics.  
Dies ist ein 6-Achsen Roboter mit integriertem Raspberry Pi 4B.  

Weiterleitung zu 
<a href="https://docs.elephantrobotics.com/docs/gitbook-en/2-serialproduct/2.6-mecharm_270/2.6.1-mechArm.html">mechArm 270-Pi</a>.  

Dieser Mecharm ist mit einer Vakuum-Pumpe
(<a href="https://docs.elephantrobotics.com/docs/gitbook-en/2-serialproduct/2.7-accessories/2.7.2%20pump/2.7.2.1-pump.html">Vertical Suction Pump</a>)
ausgerüstet, um einen Einkaufschip aufzuheben.

## Skills

| Skill                 | Beschreibung |
|-----------------------|---|
| home                  | Fährt auf den Ausgangszustand mit Koordinaten [ 0, 0, 0, 0, 0, 0 ] |
| grip                  | Schaltet die Vakuum-Pumpe an |
| release               | Schaltet die Vakuum-Pumpe aus |
| pickupFromConveyor1   | Nimmt den Chip von Förderband 1 auf |
| placeToConveyor1      | Legt den Chip auf Förderband 1 ab |
| pickupFromConveyor2   | Nimmt den Chip von Förderband 2 auf |
| placeToConveyor2      | Legt den Chip auf Förderband 2 ab |
| pickupFromLaser       | Nimmt den Chip aus der Laservorrichtung |
| placeToLaser          | Legt den Chip in die Laservorrichtung |
| pickupFromChipFlipper | Nimmt den Chip aus der Dreh-Vorrichtung raus |
| placeToChipFlipper    | Legt den Chip in die Dreh-Vorrichtung ab |
| release_servos        | Deaktiviert alle Servos des Roboter und macht diesen dadurch frei beweglich | 
| get_angles            | Zeigt die aktuellen Positions-Winkel des Roboter-Armes an | 

---
Bevor das Skript ``main_service.py`` ausgeführt werden kann muss noch eine .env-Datei angelegt werden.  
In die .env Datei die folgenden Variablen eintragen:

````python
MQTT_BROKER=  
MQTT_PORT=
MQTT_USER=  
MQTT_PASS=  
SERIAL_PORT=/dev/ttyAMA0
BAUD=1000000  
VACUUM_ON_PIN=20  
VACUUM_OFF_PIN=21
````

## MQTT Topics:

````python
TOPIC_CMD = "mecharm/command"
TOPIC_STATUS = "mecharm/status"
TOPIC_CONNECTION = "mecharm/connection"
````

## Winkel des Mecharm 270 PI

<img src="images/Mecharm_angles.jpeg" width="500">