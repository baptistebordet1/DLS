#include "DLS_library.h"
//DLS_library DLS_library(3,4,5,6,8,9,10,11,4,1,5,3);
/*
int sense=3;
int clock_plus = 4;
int clock_moins =5;
int data_plus= 6;
int data_moins=7;
String gray_code;
String multi_turn_gray;
String single_turn_gray;
int multi_turn_int;
int single_turn_int;
float single_turn_float;
int data_read_plus;
float position_encoder;
int data_read_moins;
*/
int _mot1=8;
int _mot2=9;
int _mot3=10;
int _mot4=11;
int steps_number=1;
int _delay_attenuation_motor=200000;
int ena=12;
int enb=13;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.write("here1");
  //DLS_library.begin();
  /*
  pinMode(sense,OUTPUT);
  pinMode(clock_plus,OUTPUT);
  pinMode(clock_moins,OUTPUT);
  pinMode(data_plus,INPUT);
  pinMode(data_moins,INPUT);
  digitalWrite(sense,HIGH);
  digitalWrite(clock_plus,HIGH);
  digitalWrite(clock_moins,LOW);
  */
    pinMode(_mot1, OUTPUT);
    pinMode(_mot2, OUTPUT);
    pinMode(_mot3, OUTPUT);
    pinMode(_mot4, OUTPUT);
    pinMode(ena, OUTPUT);
    pinMode(enb, OUTPUT);
    digitalWrite(ena, HIGH);
    digitalWrite(enb, HIGH);
}

void loop() {
    Serial.write("here3");
  // put your main code here, to run repeatedly:
  /*
  gray_code="";
  Serial.write(gray_code);
  for (int i=0; i<25; i++){
    digitalWrite(clock_plus,LOW);
    digitalWrite(clock_moins,HIGH);
    digitalWrite(clock_plus,HIGH);
    digitalWrite(clock_moins,LOW);
    data_read_plus=digitalRead(data_plus);
    data_read_moins=digitalRead(data_moins);
    gray_code+=String(data_read_plus);  
  }
  delay(1);
  multi_turn_gray=gray_code.substring(3,12);
  single_turn_gray=gray_code.substring(12,22);
  multi_turn_int=DLS_library.graytoInt(multi_turn_gray);
  single_turn_int=DLS_library.graytoInt(single_turn_gray);
  //Serial.write(multi_turn_int);
  //Serial.write(single_turn_int);
  single_turn_float=map(single_turn_int,0,1024,0,1);
  position_encoder=multi_turn_int+single_turn_float;
  Serial.write(position_encoder);
  */
for (int i=0; i<steps_number; i++){
    digitalWrite(_mot1, HIGH); 
    digitalWrite(_mot2, LOW); 
    digitalWrite(_mot3, HIGH); 
    digitalWrite(_mot4, LOW);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, LOW); 
    digitalWrite(_mot2, HIGH); 
    digitalWrite(_mot3, HIGH); 
    digitalWrite(_mot4, LOW);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, LOW); 
    digitalWrite(_mot2, HIGH); 
    digitalWrite(_mot3, LOW); 
    digitalWrite(_mot4, HIGH);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, HIGH); 
    digitalWrite(_mot2, LOW); 
    digitalWrite(_mot3, LOW); 
    digitalWrite(_mot4, HIGH);
    delayMicroseconds(_delay_attenuation_motor);
    }


  delay(1000);
}
