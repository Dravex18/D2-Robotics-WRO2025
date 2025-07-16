![GIF](D2%20ROBOTICS%20-%20SRC.gif)

# 💻 src – Source Code

### Welcome to the **src** section!  
### Here you’ll find the complete codebase used to tackle and complete the competition challenges.  
### This includes everything from sensor handling and motor control to autonomous navigation and decision-making logic.



# 🚀 OPEN CHALLENGE CODE

For the development of the control system, careful planning of the challenge stages—previously explained in the Obstacle Management section—was essential.
Given the need for full control over the robot’s behavior, we designed and implemented custom libraries, each responsible for a specific subsystem such as:

- Distance measurement

- PID control

- Camera vision

- Counters and timers

- And other essential functionalities

This modular structure allowed for a more organized and scalable codebase, reducing development time and improving maintainability.

As the first step in our code, we import all the necessary libraries:


<details open>
<summary>⚙️ Libraries</summary>

```cpp
#include <Arduino.h>
#include <Bounce2.h>
#include "Robot.h"
#include "PID.h"
#include <math.h>
``` 
</details>

> **Note 🔔**  
> Variables and constants are declared within their respective librarie

We then initialize the serial interface and call setup functions defined inside our custom libraries:

<details open>
<summary>⚙️ SETUP</summary>

```cpp
  
 ```cpp
  void setup() {
  Serial.begin(115200);
  myRobot.begin();

  pinMode(builtinLed, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(builtinLed, HIGH);

  button.attach(buttonPin, INPUT_PULLUP);
  button.interval(50);
}

```
</details>

Finally, the main loop is responsible for the robot's high-level behavior, including angle estimation, position updates, distance readings, and PID-based control.

The logic is structured in four main steps, allowing the robot to progress through defined stages of the challenge.

<details open>
<summary>⚙️ LOOP </summary>



```cpp
void loop() {
  //Start
  button.update();
  if (button.fell() && !activo) {
    activo = true;
    digitalWrite(builtinLed, LOW);
    myRobot.setSteerAngle(0);
    delay(1000);
  }
  if (!activo || terminado) return;

 //-----------------------------------------

  if (step==0){
    if (!stepActivaded[step]){
        myRobot.setForceTriggerF(true);
        myRobot.setForceTriggerO(true);
        myRobot.setForceTriggerI(true);
        myRobot.setDriveSpeed(0.4);
        delay(200);
        setpoint=0.5;
        myRobot.setPoseX(0.5);  //Ronda 1, se puede cambiar por una lectura con el sensor ultrasonico
        myRobot.setPoseY(1.4+0.4*0.2);  
        stepActivaded[step]=true;
    }
    //out
    if(myRobot.getPose('y')>=2){
      step++;
    }
    
  }

  myRobot.listenEcho();
  myRobot.updatePose();
  if (pid.isEnabled()){ pwm = pid.compute(setpoint, myRobot.getPose('x')); }
  myRobot.setServoPWM(pwm);
  myRobot.simulateContinuousServo();

  if (step==1){ 
    if (!stepActivaded[step]){
    //Aqui se puede agregar al despues
    }
      

    if (myRobot.getDist('f')>0.2 && myRobot.getDist('f')<0.8 && dirr==0){  //esto se puede reemplazar por myrobotgetpose y
      dirr = (myRobot.getDist('o') < 1) ? 1 : -1;

    }


    //out
    if (dirr!=0 && myRobot.getDist('f')<0.65){ //el cornering toma 0.35m y se quiere que el setpoint este a 0.3,por lo que 0.35+0.3=0.65 //esto se puede reemplazar por myrobotgetpose y
      
      myRobot.setPoseX(myRobot.getDist('f'));

      if (dirr==1){
        myRobot.setPoseY(myRobot.getPose('x'));
        myRobot.setPoseH(-90 + myRobot.getPose('h')) ; //aqui tengo que ver que pex
      }
      
      else{
        myRobot.setPoseY(1-myRobot.getPose('x'));
        myRobot.setPoseH(-90 - myRobot.getPose('h'));  //aqui tengo que ver que pex
      }
      myRobot.setDIR(dirr);
      pid.disable();
      pid.setDIR(dirr);
      step++;

    } 
  }
  

  if (step==2){
    if (!stepActivaded[step]){
    stepActivaded[step]=true;
    }

    //out
    if(myRobot.getPose('h')>-5){
      myRobot.setPoseX(myRobot.getDist('o'));
      step++;
    }
    else {
      myRobot.setSteerAngle(dirr == 1 ? -10 : -12);//esto no es lo ideal, esto se debe a un problema con la direccion
    }
  }

  if (step==3){
    if (!stepActivaded[step]){
      digitalWrite(LED, LOW);
      setpoint=0.3;
      //myRobot.setDriveSpeed(0.0);
      //myRobot.setSteerAngle(0);
      //delay(500);
      //myRobot.setDriveSpeed(0.4);
      pid.reset();
      pid.enable();
      stepActivaded[step]=true;
    }

    // Captura primer punto
    if (myRobot.getPose('y') > 1.1 && !x1_capturado) {
      digitalWrite(LED, HIGH);
      temp_x1 = myRobot.getDist('o');
      temp_y1 = myRobot.getPose('y');
      x1_capturado = true;
    }

    // Captura segundo punto
    if (myRobot.getPose('y') > 1.2 && !x2_capturado) {
      digitalWrite(LED, LOW);
      temp_x2 = myRobot.getDist('o');
      temp_y2 = myRobot.getPose('y');
      x2_capturado = true;

      float dx = temp_x2 - temp_x1;
      float dy = temp_y2 - temp_y1;

      float angulo_rad = atan2(dx, dy);
      float angulo_deg = angulo_rad * 180.0 / PI;

      myRobot.setPoseX(temp_x2);
      myRobot.setPoseH(angulo_deg);

    }
    

    //out
    if (myRobot.getPose('y')>2 ){
      //x1_capturado = false;
      //x2_capturado = false;
      stepActivaded[2]=false;
      stepActivaded[3]=false;
      step=1;
    }

  }

  if (step==6){

    
    myRobot.setDriveSpeed(0.0);
    myRobot.setServoPWM(0);
/*
    int divisor = round(myRobot.getPose('y') / 0.1);
    for (int i = 0; i < divisor; i++) {
    digitalWrite(LED, HIGH);
    delay(500);
    digitalWrite(LED, LOW);
    delay(500);
  }
  */
    terminado = true;
  }

}


```
</details>


