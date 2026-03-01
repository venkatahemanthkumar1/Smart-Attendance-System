#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 5
#define RST_PIN 22

MFRC522 mfrc522(SS_PIN, RST_PIN);

// 🔹 Structure to store UID and Name
struct Card {
  String uid;
  String name;
};

// 🔹 All Authorized Cards
Card cards[] = {
  {"E195193D", "hemanth"},
  {"316C8B3C", "vinay"},
  {"C19C7E3C", "joshi"},
  {"918B673C", "sujith"},
  {"E1CF913C", "venkat"},
  {"C1F0673C", "srikhari"},
  {"B11D6E3C", "sneha"},
  {"31F38E3C", "abhiram"},
  {"61DC7E3C", "swaroop"}
};

const int totalCards = sizeof(cards) / sizeof(cards[0]);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("Scan RFID Card...");
}

void loop() {

  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  String uid = "";

  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      uid += "0";   // Add leading zero
    }
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }

  uid.toUpperCase();

  checkCard(uid);

  mfrc522.PICC_HaltA();
  delay(2000);
}

// 🔹 Function to Check Card
void checkCard(String uid) {
  for (int i = 0; i < totalCards; i++) {
    if (uid == cards[i].uid) {
      
      Serial.println(cards[i].name);
      return;
    }
  }
  Serial.println("UNKNOWN_CARD");
}