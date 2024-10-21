#include "Arduino.h"
#include "DLS_library.h"
#include <SPI.h>
#include <HighPowerStepperDriver.h>

DLS_library::DLS_library(int clock_positiv, int clock_negativ, int data_positiv, int data_negativ, int sense, int CSPinA, int DirPinA, int StepPinA, int StepPinR, int DirPinR, int phototransistor_pin) {
  _clock_positiv = clock_positiv;
  _clock_negativ = clock_negativ;
  _data_positiv = data_positiv;
  _data_negativ = data_negativ;
  _sense = sense;
  _DirPin_A = DirPinA;
  _StepPin_A = StepPinA;
  _CSPin_A = CSPinA;
  _StepPin_R = StepPinR;
  _DirPin_R = DirPinR;
  _phototransistor_pin = phototransistor_pin;
}
void DLS_library::begin() {
  pinMode(_clock_positiv, OUTPUT);
  pinMode(_clock_negativ, OUTPUT);
  pinMode(_data_positiv, OUTPUT);
  pinMode(_data_negativ, OUTPUT);
  pinMode(_DirPin_A, OUTPUT);
  pinMode(_StepPin_A, OUTPUT);
  pinMode(_CSPin_A, OUTPUT);
  pinMode(_StepPin_R, OUTPUT);
  pinMode(_DirPin_R, OUTPUT);
  pinMode(_sense, OUTPUT);
  pinMode(_phototransistor_pin, INPUT);
  digitalWrite(_sense, HIGH);
  digitalWrite(_clock_positiv, HIGH);
  digitalWrite(_clock_negativ, LOW);

/*

  // initiate SPI connection for polllolu driver
  HighPowerStepperDriver _sd;
  SPI.begin();
  _sd.setChipSelectPin(_CSPin_A);

  // Drive the STEP and DIR pins low initially.
  pinMode(_StepPin_A, OUTPUT);
  digitalWrite(_StepPin_A, LOW);
  pinMode(_DirPin_A, OUTPUT);
  digitalWrite(_DirPin_A, LOW);

  // Give the driver some time to power up.
  delay(1);

  // Reset the driver to its default settings and clear latched status
  // conditions.
  _sd.resetSettings();
  _sd.clearStatus();

  // Select auto mixed decay.  TI's DRV8711 documentation recommends this mode
  // for most applications, and we find that it usually works well.
  _sd.setDecayMode(HPSDDecayMode::AutoMixed);

  // Set the current limit. You should change the number here to an appropriate
  // value for your particular system.
  _sd.setCurrentMilliamps36v4(1000);

  // Set the number of microsteps that correspond to one full step.
  _sd.setStepMode(HPSDStepMode::MicroStep32);

  // Enable the motor outputs.
  _sd.enableDriver();

*/

}
// Generic functions for motor
void DLS_library::setDirection(int _Direction_Pin, bool _dir) {
  // The STEP pin must not change for at least 200 nanoseconds before and after
  // changing the DIR pin.
  delayMicroseconds(1);
  digitalWrite(_Direction_Pin, _dir);
  delayMicroseconds(1);
}
void DLS_library::step(int _StepPin) {
  // The STEP minimum high pulse width is 1.9 microseconds.
  digitalWrite(_StepPin, HIGH);
  delayMicroseconds(3);
  digitalWrite(_StepPin, LOW);
  delayMicroseconds(3);
}
// Rotation motor control
void DLS_library::move_trig_positiv_rotation_platine(int _rotation_number_before_measure_position, int _dl) {
  DLS_library::setDirection(_DirPin_R, HIGH);
  for (int i = 0; i < _rotation_number_before_measure_position * 200; i = i++) {
    DLS_library::step(_StepPin_R);
    delayMicroseconds(_dl);
    if (DLS_library::emergency_stop_R == 1) {
      break;
    }
  }
}
void DLS_library::move_trig_negativ_rotation_platine(int _rotation_number_before_measure_position, int _dl) {  // rotation_number_before_measure_position is the number of rotation before the value is checked.
  DLS_library::setDirection(_DirPin_R, LOW);
  for (int i = 0; i < _rotation_number_before_measure_position * 200; i = i++) {
    DLS_library::step(_StepPin_R);
    delayMicroseconds(_dl);
    if (DLS_library::emergency_stop_R == 1) {
      break;
    }
  }
}
// Attenuator motor control
void DLS_library::move_trig_positiv_attenuator(int _steps_number, int _delay_attenuation_motor) {
  DLS_library::setDirection(_DirPin_A, LOW);
  for (unsigned int x = 0; x < _steps_number; x++) {
    DLS_library::step(_StepPin_A);
    delayMicroseconds(_delay_attenuation_motor);
    if (DLS_library::fault_stop_A == 1) {
      break;
    }
  }
}
void DLS_library::move_trig_negativ_attenuator(int _steps_number, int _delay_attenuation_motor) {
  DLS_library::setDirection(_DirPin_A, HIGH);
  for (unsigned int x = 0; x < _steps_number; x++) {
    DLS_library::step(_StepPin_A);
    delayMicroseconds(_delay_attenuation_motor);
    if (DLS_library::fault_stop_A == 1) {
      break;
    }
  }
}
int DLS_library::initialisation_position_attenuator() {
  int is_signal_phototransistor;
  DLS_library::setDirection(_DirPin_A, HIGH);
  for (unsigned int x = 0; x < 200; x++) {  // change here how steps is one turn 
    DLS_library::step(_StepPin_A);
    delayMicroseconds(_delay_attenuation_motor);
    is_signal_phototransistor = digitalRead(_phototransistor_pin);
    if (is_signal_phototransistor == 1) {  // Verify that it's high when light is coming
      _position_attenuator_motor = 196;    // Verify that this is the correct number
      break;
    }
  }
  return is_signal_phototransistor;
}
// Encoder functions
char DLS_library::flip(char c) {  // Helper function to flip the bit
  return (c == '0') ? '1' : '0';
}
int DLS_library::graytoInt(String _gray) {  // function to convert gray code String to int
  String binary = String("");
  // MSB of binary code is same as gray code
  binary += _gray[0];

  // Compute remaining bits
  for (int i = 1; i < _gray.length(); i++) {
    // If current bit is 0, concatenate
    // previous bit
    if (_gray[i] == '0') {
      binary += binary[i - 1];
    }
    // Else, concatenate invert of
    // previous bit
    else {
      binary += flip(binary[i - 1]);
    }
  }
  // Convert string to int
  unsigned long k = strtoul(binary.c_str(), NULL, 2);
  return k;
}

float DLS_library::read_encoder() {
  _gray_code = "";
  delayMicroseconds(25);  // just to ensure the wait period is complete.
  for (int i = 0; i < 25; i++) {
    digitalWrite(_clock_positiv, LOW);
    digitalWrite(_clock_negativ, HIGH);
    digitalWrite(_clock_positiv, HIGH);
    digitalWrite(_clock_negativ, LOW);
    _data_read_positiv = digitalRead(_data_positiv);
    _gray_code += String(_data_read_positiv);
  }
  _multi_turn_gray = _gray_code.substring(3, 12);
  _single_turn_gray = _gray_code.substring(12, 22);
  _multi_turn_int = graytoInt(_multi_turn_gray);
  _single_turn_int = graytoInt(_single_turn_gray);
  _single_turn_float = map(_single_turn_int, 0, 1024, 0, 1);
  _position_encoder = _multi_turn_int + _single_turn_float;
  return _position_encoder;
}
