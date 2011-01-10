/*
  Button
 
 Turns on and off a light emitting diode(LED) connected to digital  
 pin 13, when pressing a pushbutton attached to pin 7. 
 
 
 The circuit:
 * LED attached from pin 13 to ground 
 * pushbutton attached to pin 2 from +5V
 * 10K resistor attached to pin 2 from ground
 
 * Note: on most Arduinos there is already an LED on the board
 attached to pin 13.
 
 
 created 2005
 by DojoDave <http://www.0j0.org>
 modified 17 Jun 2009
 by Tom Igoe
 
 http://www.arduino.cc/en/Tutorial/Button
 */

// constants won't change. They're used here to 
// set pin numbers:
const int buttonPin = 2;     // the number of the pushbutton pin
const int stateLED =  13;      // the number of the LED pin
const int outputLED = 12;

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status
int ontimeout = 5000;        // time to wait before turning on
int offtimeout = 15000;      // time to wait before turning off
int timestored = 0;
int timetogo = 0;

long previousMillis = 0;      // last update time
long elapsedMillis = 0;       // elapsed time
long storedMillis = 0;  

boolean active = false;
boolean countingdown = false;
boolean statusLEDstate = 0;

void setup() {
  // initialize the LED pins as outputs:
  pinMode(stateLED, OUTPUT);
  pinMode(outputLED, OUTPUT);;  
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT);     

  // Initialize the serial port
  Serial.begin(57600);
  Serial.println("\nHello!");
  delay(500);
}

void loop(){
  unsigned long currentMillis = millis();
  // Serial.print("Time is ");
  // Serial.println(currentMillis);
  delay(10);
  
  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);
  // check if the pushbutton is pressed.
  // if it is, the buttonState is HIGH:
  if (active == false) {
    if (buttonState == HIGH) { 
      digitalWrite(stateLED, HIGH);
      if (timestored == 0) {
        timestored = 1;
        storedMillis = currentMillis;
        Serial.print("Storing time : ");
        Serial.println(currentMillis);
      }
      if (timestored == 1) {
        elapsedMillis = currentMillis - storedMillis;
        if (elapsedMillis > ontimeout) {
          active = 1;
        }
        Serial.print("Elapsed time : ");
        Serial.println(elapsedMillis);
      }

    } else {
      digitalWrite(stateLED, LOW);
      timestored = 0;
      storedMillis = 0;
    }
  }

  if (active == true) {
    // We're active, so we have to count down now as well
    digitalWrite(outputLED, HIGH);
    if (buttonState == LOW) {
      if (countingdown == 0) {
        storedMillis = currentMillis; // Store the time the button was pressed
        Serial.print("Storing time : ");
        Serial.println(storedMillis);
        countingdown = 1;
      }
      if (countingdown == 1) {
        timetogo = (offtimeout + storedMillis) - currentMillis; // Time left is the current time
        Serial.print("Runtime left : ");
        Serial.println(timetogo);
      }
      if (timetogo <= 0 && countingdown == 1) {
        // That's us at the end. Reset some variables for reactivation and power off
        Serial.println("Power off");
        active = false;
        timetogo = 0;
        countingdown = 0;
        digitalWrite(outputLED, LOW);
      }
    }
    if (buttonState == HIGH) {
      // What do we do when the ignition comes back on during the countdown?
      countingdown = 0;
    }
  }
}

