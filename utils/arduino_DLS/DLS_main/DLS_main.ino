#include "DLS_library.h"
DLS_library DLS_library(9,10,11,12,5, 53, 4,8,23);

int dl = 20;                       //  time between each motor step for the turntable (ms)
int delay_attenuation_motor = 20;  //  time between each motor step for the attenuator (ms)
int is_signal_phototransistor;     // variable containing the result of initialisation of the attenuator motor
int position_motor_attenuator=0;     // Variable containing the position of the attenuation motor
float position_motor_rotation;     // Variable containing the position of the rotation motor
char operation;                    // Variable containing R or W for Read or Write
char motor_select;                 // Variable containing A or T for Attenuator motor and Turntable motor
char rotation_direction;           // Variable containing P or N for positive or and Negative (positiv is in trigonometric direction)
int steps_to_do;                   // Variable containing the number of steps to move for the attenuator motor
float steps_to_do_rotation;                   // Variable containing the number of steps to move for the rotation motor
int step_to_reach;                 // Variable containing the position to reach for the attenuator motor
float step_to_reach_rotation;        // Variable containing the position to reach for the rotation motor
int condition = 0;
int rotation_number_before_measure_position;  // Variable containing the steps between position measurements for platine rotation
int relay_R_pin = 7;                         // Pin for relay for rotation motor, fault restart and stop the power of motor in case of limit switches reached
int state_relay_R = 0;                        // state of the relay 0: closed (motor powered), 1: open (motor stopped)
int reset_attenuator_control_pin= 22;         // Pin to try to reset the attenuator control
int fault_attenuator_control_pin = 2;         // Pin receive LOW when driver detects fault in motor (over temperature,over voltage over current  )
int stall_attenuator_pin = 3;                 // Pin receives low when drivers detect a stall in the attenuator motor (attempt to reset the chip and restart procedure)
int fault_detection_rotation_motor_pin = 19;  // Pin to read if a fault is detected in the motor attenuation
int limit_switch_1_pin = 20;                  // Pin to read if the limit switch has been reached
int limit_switch_2_pin = 21;                  // Pin to read if the limit switch has been reached

 
void fault_stop_attenuation() {
  DLS_library.fault_stop_A = 1;
}
void fault_stop_rotation() {
  DLS_library.fault_stop_R = 1;
}
void emergency_stop_rotation() {
  DLS_library.emergency_stop_R = 1;
}
void setup() {
  DLS_library.begin();
  Serial.begin(115200);
  
  position_motor_rotation = DLS_library.read_encoder();
  pinMode(fault_attenuator_control_pin, INPUT);
  pinMode(stall_attenuator_pin, INPUT);
  pinMode(fault_detection_rotation_motor_pin, INPUT);
  pinMode(limit_switch_1_pin, INPUT);
  pinMode(limit_switch_2_pin, INPUT);
  attachInterrupt(digitalPinToInterrupt(fault_attenuator_control_pin), fault_stop_attenuation, FALLING);
  attachInterrupt(digitalPinToInterrupt(stall_attenuator_pin), fault_stop_attenuation, RISING);
  attachInterrupt(digitalPinToInterrupt(fault_detection_rotation_motor_pin), fault_stop_rotation, RISING);
  attachInterrupt(digitalPinToInterrupt(limit_switch_1_pin),emergency_stop_rotation, RISING);
  attachInterrupt(digitalPinToInterrupt(limit_switch_2_pin),emergency_stop_rotation, RISING);
  position_motor_attenuator=DLS_library.initialisation_position_attenuator();
}

void loop() {
    
  if (Serial.available() > 1) {
    operation = Serial.read();
    motor_select = Serial.read();
    switch (operation) {
      case 'M':      
        if (motor_select == 'T') {
          step_to_reach_rotation = Serial.parseFloat();
          position_motor_rotation=DLS_library.read_encoder();
          if (position_motor_rotation<step_to_reach_rotation){
            rotation_direction='N';
          }
          else if (position_motor_rotation>step_to_reach_rotation)
          {
            rotation_direction='P';
          }
          else {
            rotation_direction='H'; // case where the motor is already at the right position
          }

          if (rotation_direction == 'P') {
            position_motor_rotation=DLS_library.read_encoder();
            steps_to_do_rotation = step_to_reach_rotation - position_motor_rotation;

            while (steps_to_do_rotation < 0) {  
              if (abs(steps_to_do_rotation) > 0.5) {
                
                rotation_number_before_measure_position = 10*200;
              }
              else {
                rotation_number_before_measure_position = 10;
              }
              DLS_library.move_trig_positiv_rotation_platine(rotation_number_before_measure_position, dl);
              if (DLS_library.emergency_stop_R == 1) {
                Serial.write("error_rotation_motor\n");
                break;
              }
              position_motor_rotation = DLS_library.read_encoder();
              Serial.write("motor_rotating,");
              Serial.print(position_motor_rotation,3);
              Serial.write("\n");
              steps_to_do_rotation = step_to_reach_rotation - position_motor_rotation;
            }
            position_motor_rotation = DLS_library.read_encoder();

            Serial.write("movement_finished,");
            Serial.print(position_motor_rotation,3);
            Serial.write("\n");
          } else if (rotation_direction=='N') {
            position_motor_rotation=DLS_library.read_encoder();
            steps_to_do_rotation = step_to_reach_rotation - position_motor_rotation;
            while (steps_to_do_rotation > 0) {  
      
              if (abs(steps_to_do_rotation) > 0.5) {
                
                rotation_number_before_measure_position = 10*200;
              }
              else {
                rotation_number_before_measure_position = 10;
              }
              DLS_library.move_trig_negativ_rotation_platine(rotation_number_before_measure_position, dl);
              if (DLS_library.emergency_stop_R == 1) {
                Serial.write("error_rotation_motor\n");
                break;
              }
              position_motor_rotation = DLS_library.read_encoder();
              Serial.write("motor_rotating,");
              Serial.print(position_motor_rotation,3);
              Serial.write("\n");
              steps_to_do_rotation = step_to_reach_rotation - position_motor_rotation;
            }
            position_motor_rotation = DLS_library.read_encoder();
            Serial.write("movement_finished,");
            Serial.print(position_motor_rotation,3);
            Serial.write("\n");
          } else {
            break;
            // character not recognised
          }

        } else if (motor_select == 'A') {
          step_to_reach = Serial.parseInt();

          if (step_to_reach - position_motor_attenuator < 0)  // To ensure that 0 is the right value
          {
            rotation_direction = 'P';
            steps_to_do = step_to_reach - position_motor_attenuator;

          } else if (step_to_reach - position_motor_attenuator > 0)  // to ensure that zero is the right value
          {
            rotation_direction = 'N';
            steps_to_do = step_to_reach - position_motor_attenuator;
            
          } else {
            rotation_direction = 'H';  // case where it is already at the asked value no movement need here
          }

          if (rotation_direction == 'P') {
            DLS_library.move_trig_positiv_attenuator(steps_to_do);
            if (DLS_library.fault_stop_A == 1) {
              Serial.write("error_attenuation_motor\n");
              break;
            } 
            else {
              position_motor_attenuator = abs((position_motor_attenuator + steps_to_do) % 192); // change 200 to the number of step per turn 
              Serial.write("movement_attenuation_finished,");
                Serial.print(position_motor_attenuator);
                Serial.write("\n");
                
                  
            }
            
          } else if (rotation_direction == 'N') {
            DLS_library.move_trig_negativ_attenuator(steps_to_do);
            if (DLS_library.fault_stop_A == 1) {
              Serial.write("error_attenuation_motor\n");
              break;
            } else {
              position_motor_attenuator = abs((position_motor_attenuator + steps_to_do) % 192); // change 200 to the number of step per turn 
               Serial.write("movement_attenuation_finished,");
                Serial.print(position_motor_attenuator);
                Serial.write("\n");

                
            }

          } else {
            break;
            // character not recognised, unexpected rotation direction
          }
        } else {
          break;
          // character not recognised, unexpected motor selection
        }

        break;
      case 'R':  // not used now still here in case it is needed for the python code to acess manually the values of the positions (it is normally send after a movement and not refreshed until another movement is started )
        if (motor_select == 'T') {
          position_motor_rotation = DLS_library.read_encoder();
          Serial.print(position_motor_rotation,3);
          Serial.write("\n");
          break;
        } else if (motor_select == 'A') {
          Serial.print(position_motor_attenuator);
          Serial.write("\n");
          break;
        }
        break;
      case 'E':  // calibration move
        rotation_number_before_measure_position = Serial.parseInt();
        DLS_library.move_trig_positiv_rotation_platine(rotation_number_before_measure_position, dl);
        if (DLS_library.emergency_stop_R == 1) {
          Serial.write("error_rotation_motor\n");
          break;
        }
        position_motor_rotation = DLS_library.read_encoder();
        Serial.write("calibration_finished_movement,");
        Serial.print(position_motor_rotation,3);
        Serial.write("\n");
        break;
    }
  }
  else if (Serial.available()>0){
    operation = Serial.read();
    
    switch (operation){
      case 'C':  // ping from python code at the beginning to see if arduino is connected
        Serial.write("ALIVE\n");
        
        break;
      case 'I': 
        is_signal_phototransistor,position_motor_attenuator = DLS_library.initialisation_position_attenuator();  //
        Serial.print(position_motor_attenuator);
        if (is_signal_phototransistor == 1) {
          Serial.write("Error_init_attenuator\n");
        }
        break;
      
      default:
      break;
    }
      
  }
  if (DLS_library.emergency_stop_R == 1) {
  Serial.write("CRITICAL_ERROR\n");
  state_relay_R = HIGH;
  digitalWrite(relay_R_pin, state_relay_R);
  DLS_library.emergency_stop_R = 0;
}
if (DLS_library.fault_stop_A == 1) {
  digitalWrite(reset_attenuator_control_pin, HIGH);
  delay(200);
  digitalWrite(reset_attenuator_control_pin, LOW);
  DLS_library.fault_stop_A = 0;
  Serial.write("fault_motor_attenuation\n");
}
if (DLS_library.fault_stop_R) {
  state_relay_R = HIGH;
  digitalWrite(relay_R_pin, state_relay_R);
  delay(1000);
  state_relay_R = LOW;
  digitalWrite(relay_R_pin, state_relay_R);
  DLS_library.fault_stop_R = 0;
  Serial.write("fault_motor_rotation\n");
}
delay(1);
}


