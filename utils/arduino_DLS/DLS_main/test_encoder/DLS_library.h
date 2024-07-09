/*
DLS_library is a library used to control 
the DLS experiment in LIPhy. 
Created by Baptiste Bordet, April 3 2024. 
*/

#include "Arduino.h"
#ifndef DLS_library_h
#define DLS_library_h

class DLS_library{
    public:
    DLS_library(int in1, int in2, int in3, int in4, int mot1, int mot2, int mot3, int mot4, int clock_positiv, int clock_negativ, int data_positiv, int data_negativ);
    void begin();
    void move_trig_positiv_rotation_platine(int _rotation_number_before_measure_position, int _dl);
    void move_trig_negativ_rotation_platine(int _rotation_number_before_measure_position, int _dl);
    char flip(char _c);
    int graytoInt(String _gray);
    void move_trig_positiv_attenuator(int _steps_number, int _delay_attenuation_motor);
    void move_trig_negativ_attenuator(int _steps_number, int _delay_attenuation_motor);

    private:
    int _rotation_number_before_measure_position;
    int _in1; // motor rotation 1
    int _in2; // motor rotation 2
    int _in3; // motor rotation 3
    int _in4; // motor rotation 4
    int _dl; // delay motor rotation 
    int _mot1; // motor attenuator 1
    int _mot2; // motor attenuator 2
    int _mot3; // motor attenuator 3
    int _mot4; // motor attenuator 4
    int _delay_attenuation_motor; //delay motor attenuator 
    char _c;
    String _gray;
    int _steps_number;
    int _clock_positiv;  // encoder clock + 
    int _clock_negativ;  // encoder clock -
    int _data_positiv;   // encoder data +
    int _data_negativ; // encoder data -  
};

#endif