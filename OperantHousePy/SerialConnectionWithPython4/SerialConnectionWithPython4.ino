#include <Servo.h>
Servo myservo;//Declar Servo object
void setup(){
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(7, OUTPUT);
  myservo.attach(2);  //Set channel 0 for servo regulation
  myservo.write(90);  //Change the angle of servo arm to 90 degree
  //Serial.begin(9600);
  Serial.begin(115200); //Init serial port as 115200 bps
  
}
//Variables for LED switching
int Phase=0;
int CurrentChannelID;
int CurrentValue;
char CurrentChar;
int Trg;
int inputchar;

//Variables for reading of infrared sensor
int analogPin = 0;     //Channel of analog the input
int val = 0;           //The value of analog input
void loop(){
  // シリアルポートより1文字読み込む
  inputchar = Serial.read();  // Get the input from the PC
  if(inputchar != -1 ){ // If received value is not -1 
    Trg=0;
    if(Phase == 0){
      if(inputchar == 'a'){ // If input data designates channel 13
        //digitalWrite(13, HIGH);
        CurrentChannelID=0;
        Phase++;
      }
      if(inputchar == 'b'){ // If input data designates channel 12
        CurrentChannelID=1;
        Phase++;
      }
      if(inputchar == 'c'){ // If input data designates channel 11
        CurrentChannelID=2;
        Phase++;
      }
      if(inputchar == 'd'){ // If input data designates channel 10
        CurrentChannelID=3;
        Phase++;
      }
      if(inputchar == 'e'){ // If input data designates channel 9
        CurrentChannelID=4;
        Phase++;
      }
      if(inputchar == 'f'){ // If input data designates channel 8
        CurrentChannelID=5;
        Phase++;
      }
      if(inputchar == 'g'){ // If input data designates channel 7
        CurrentChannelID=6;
        Phase++;
      }
      if(inputchar == 'h'){ // If input data is for the regulation of servo
        CurrentChannelID=7;
        Phase++;
      }
      Trg=1;
    }
    if(Phase == 1 && Trg==0 && CurrentChannelID!=7){
      //digitalWrite(13, HIGH);
      if(inputchar == '1'){
        CurrentValue=1;
        Phase++;
      }
      if(inputchar == '0'){
        CurrentValue=0;
        Phase++;
      }
    }
    if(Phase == 1 && Trg==0 && CurrentChannelID==7){
      Phase++;
    }
    if(Phase==2){
      Serial.println(analogRead(analogPin));
      if(CurrentChannelID==0){
        if(CurrentValue==1){
          digitalWrite(13, HIGH);
        }
        if(CurrentValue==0){
          digitalWrite(13, LOW);
        }
      }
      if(CurrentChannelID==1){
        if(CurrentValue==1){
          digitalWrite(12, HIGH);
        }
        if(CurrentValue==0){
          digitalWrite(12, LOW);
        }
      }
      if(CurrentChannelID==2){
        if(CurrentValue==1){
          digitalWrite(11, HIGH);
        }
        if(CurrentValue==0){
          digitalWrite(11, LOW);
        }
      }
      if(CurrentChannelID==3){
        if(CurrentValue==1){
          digitalWrite(10, HIGH);
        }
        if(CurrentValue==0){
          digitalWrite(10, LOW);
        }
      }
      if(CurrentChannelID==4){
        if(CurrentValue==1){
          digitalWrite(9, HIGH);
        }
        if(CurrentValue==0){
          digitalWrite(9, LOW);
        }
      }
      if(CurrentChannelID==5){
        if(CurrentValue==1){
          digitalWrite(8, HIGH);
        }
        if(CurrentValue==0){
          digitalWrite(8, LOW);
        }
      }
      if(CurrentChannelID==6){
        if(CurrentValue==1){
          digitalWrite(7, HIGH);
        }
        if(CurrentValue==0){
          digitalWrite(7, LOW);
        }
      }
      if(CurrentChannelID==7){
        myservo.write(inputchar);  //Change the angle of servo arm to the designated degree
        //myservo.write(180);
        //Serial.println(inputchar);
      }
      Phase=0;
    }
  }
}
