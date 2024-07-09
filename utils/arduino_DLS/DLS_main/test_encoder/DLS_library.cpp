
#include "Arduino.h"
#include "DLS_library.h"


DLS_library::DLS_library(int in1, int in2, int in3, int in4, int mot1, int mot2, int mot3, int mot4, int clock_positiv, int clock_negativ, int data_positiv, int data_negativ){
 _in1=in1;
 _in2=in2;
 _in3=in3;
 _in4=in4;
 _mot1=mot1;
 _mot2=mot2;
 _mot3=mot3;
 _mot4=mot4;
 _clock_positiv=clock_positiv;
 _clock_negativ=clock_negativ;
 _data_positiv=data_positiv;
 _data_negativ=data_negativ;
}
void DLS_library::begin(){
    pinMode(_in1, OUTPUT);
    pinMode(_in2, OUTPUT);
    pinMode(_in3, OUTPUT);
    pinMode(_in4, OUTPUT);
    pinMode(_mot1, OUTPUT);
    pinMode(_mot2, OUTPUT);
    pinMode(_mot3, OUTPUT);
    pinMode(_mot4, OUTPUT);
    pinMode(_clock_positiv, OUTPUT);
    pinMode(_clock_negativ, OUTPUT);
    pinMode(_data_positiv, OUTPUT);
    pinMode(_data_negativ, OUTPUT);
}
void DLS_library::move_trig_positiv_rotation_platine(int _rotation_number_before_measure_position, int _dl){
    for (int i=0; i<_rotation_number_before_measure_position*10; i++){
    digitalWrite(_in1, HIGH); 
    digitalWrite(_in2, LOW); 
    digitalWrite(_in3, LOW); 
    digitalWrite(_in4, HIGH);
    delayMicroseconds(_dl);

    digitalWrite(_in1, HIGH); 
    digitalWrite(_in2, HIGH); 
    digitalWrite(_in3, LOW); 
    digitalWrite(_in4, LOW);
    delayMicroseconds(_dl);

    digitalWrite(_in1, LOW); 
    digitalWrite(_in2, HIGH); 
    digitalWrite(_in3, HIGH); 
    digitalWrite(_in4, LOW);
    delayMicroseconds(_dl);

    digitalWrite(_in1, LOW); 
    digitalWrite(_in2, LOW); 
    digitalWrite(_in3, HIGH); 
    digitalWrite(_in4, HIGH);
    delayMicroseconds(_dl);

    
    }
}
void DLS_library::move_trig_negativ_rotation_platine(int _rotation_number_before_measure_position, int _dl) { // rotation_number_before_measure_position is the number of rotation before the value is checked.
    for (int i=0; i<_rotation_number_before_measure_position*200; i=i++){
    digitalWrite(_in1, LOW); 
    digitalWrite(_in2, LOW); 
    digitalWrite(_in3, HIGH); 
    digitalWrite(_in4, HIGH);
    delayMicroseconds(_dl);

    digitalWrite(_in1, LOW); 
    digitalWrite(_in2, HIGH); 
    digitalWrite(_in3, HIGH); 
    digitalWrite(_in4, LOW);
    delayMicroseconds(_dl);

    digitalWrite(_in1, HIGH); 
    digitalWrite(_in2, HIGH); 
    digitalWrite(_in3, LOW); 
    digitalWrite(_in4, LOW);
    delayMicroseconds(_dl);

    digitalWrite(_in1, HIGH); 
    digitalWrite(_in2, LOW); 
    digitalWrite(_in3, LOW); 
    digitalWrite(_in4, HIGH);
    delayMicroseconds(_dl);
    }
}
void DLS_library::move_trig_positiv_attenuator(int _steps_number, int _delay_attenuation_motor)
{
for (int i=0; i<=_steps_number; i=i++){
    digitalWrite(_mot1, HIGH); 
    digitalWrite(_mot2, LOW); 
    digitalWrite(_mot3, LOW); 
    digitalWrite(_mot4, HIGH);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, HIGH); 
    digitalWrite(_mot2, HIGH); 
    digitalWrite(_mot3, LOW); 
    digitalWrite(_mot4, LOW);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, LOW); 
    digitalWrite(_mot2, HIGH); 
    digitalWrite(_mot3, HIGH); 
    digitalWrite(_mot4, LOW);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, LOW); 
    digitalWrite(_mot2, LOW); 
    digitalWrite(_mot3, HIGH); 
    digitalWrite(_mot4, HIGH);
    delayMicroseconds(_delay_attenuation_motor);
    }
}
void DLS_library::move_trig_negativ_attenuator(int _steps_number,int _delay_attenuation_motor)
{
    for (int i=0; i<_steps_number; i=i++){
    digitalWrite(_mot1, LOW); 
    digitalWrite(_mot2, LOW); 
    digitalWrite(_mot3, HIGH); 
    digitalWrite(_mot4, HIGH);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, LOW); 
    digitalWrite(_mot2, HIGH); 
    digitalWrite(_mot3, HIGH); 
    digitalWrite(_mot4, LOW);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, HIGH); 
    digitalWrite(_mot2, HIGH); 
    digitalWrite(_mot3, LOW); 
    digitalWrite(_mot4, LOW);
    delayMicroseconds(_delay_attenuation_motor);

    digitalWrite(_mot1, HIGH); 
    digitalWrite(_mot2, LOW); 
    digitalWrite(_mot3, LOW); 
    digitalWrite(_mot4, HIGH);
    delayMicroseconds(_delay_attenuation_motor);
}
}
char DLS_library::flip(char c)
{ // Helper function to flip the bit
    return (c == '0') ? '1' : '0'; 
}

int DLS_library::graytoInt(String gray)
{ // function to convert gray code String to int 
    String binary = String("");
    // MSB of binary code is same as gray code
    binary += gray[0];
 
    // Compute remaining bits
    for (int i = 1; i < gray.length(); i++) {
        // If current bit is 0, concatenate
        // previous bit
        if (gray[i] == '0'){
            binary += binary[i - 1];
        }
        // Else, concatenate invert of
        // previous bit
        else{
            binary += flip(binary[i - 1]);
        }
    }
    unsigned long k = strtoul(binary.c_str(), NULL, 2);
    return k;
}
