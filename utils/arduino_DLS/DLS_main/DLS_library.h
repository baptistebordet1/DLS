/*
DLS_library is a library used to control 
the DLS experiment in LIPhy. 
Created by Baptiste Bordet, April 3 2024. 
*/

#include "Arduino.h"
#include <HighPowerStepperDriver.h>
#ifndef Morse_h
#define Morse_h

class DLS_library {
public:

  DLS_library(int clock_positiv, int clock_negativ, int data_positiv, int data_negativ, int sense, int CSPinA, int StepPinR, int DirPinR,int phototransistor_pin);
  void begin();
  void move_trig_positiv_rotation_platine(int _rotation_number_before_measure_position, int _dl);
  void move_trig_negativ_rotation_platine(int _rotation_number_before_measure_position, int _dl);
  char flip(char _c);
  String graytoInt(String _gray);
  void move_trig_positiv_attenuator(int _steps_number);
  void move_trig_negativ_attenuator(int _steps_number);
  float read_encoder();
  int initialisation_position_attenuator();
  float map_float(long x, long in_min, long in_max, float out_min, float out_max);
  int emergency_stop_R;
  int fault_stop_A;
  int fault_stop_R;


private:
  HighPowerStepperDriver _sd;         // SPI class
  void setDirection_R(int _Direction_Pin, bool _dir);
  void setDirection_A(  int _dir);
  void step_R(int _StepPin_R);
  void step_A();
  int _phototransistor_pin; // rphotostranstor pin reading value 
  int _DirPin_R;   // Direction pin for rotation control motor
  int _StepPin_R;  // Pin to send pulse to do a step for rotation control motor
  int _CSPin_A;    // Chip select pin for SPI connection (Attenuator driver)
  int _is_signal_phototransistor; // variable conatining the value of the phottransistor for attenuator position
  int _rotation_number_before_measure_position;
  int _position_attenuator_motor; // stores value of the position motor take care when changing this value
  int _dl;                       // delay motor rotation
  int _steps_number;             // steps to do attenuator
  int _clock_positiv;            // encoder clock +
  int _clock_negativ;            // encoder clock -
  int _data_positiv;             // encoder data +
  int _data_negativ;             // encoder data -
  int _sense;                    // Rotation direction pin for encoder
  int _data_read_positiv[25];        // digital value read from encoder
  String _gray_code;             // String holding full message from encoder
  String _multi_turn_gray;       // String holding the multi-turn infomation from encoder
  String _single_turn_gray;      // String holding the single turn information from encoder
  int _multi_turn_int;           // Converted value of the above
  int _single_turn_int;          // Converted value of the above
  float _single_turn_float;      // Conversion into a fraction of a single turn (decimal not degrees)
  float _position_encoder;       // Position from the encoder
  String _gray;                  // value to convert in graytoInt function
  char _c;                       // used in the conversion from gray code to int when reading encoder value (dumb variable)
};

#endif