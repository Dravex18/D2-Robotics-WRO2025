![GIF](D2%20ROBOTICS%20-%20SRC.gif)

# 💻 src – Source Code

### Welcome to the **src** section!  
### Here you’ll find the complete codebase used to tackle and complete the competition challenges.  
### This includes everything from sensor handling and motor control to autonomous navigation and decision-making logic.

> **Note 🔔**  
>For a proper understanding of the code, please refer to the custom libraries we developed, which are attached above.

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

# 🧱 OBSTACLE CHALLENGE

For the obstacle challenge round, we used the same mobility system as in the first round. The only difference is that we activated the camera to detect and classify obstacles.

As the first step, we import the necessary libraries.

Due to the orientation of our robot, we inverted the captured image to correct its alignment.

Additionally, we reduced the camera resolution (i.e., pixel count) to speed up image processing and enable faster response times.


### MODULES & GLOBAL STATE

In this section, helper functions are implemented to handle essential tasks such as selecting the path to follow, calculating angular error for steering, ensuring safe communication with the Raspberry Pi through timeout mechanisms, correcting the lane layout, and managing step latching. The goal is to keep these functions as independent as possible, operating only on their inputs without relying on hidden states, which makes them more predictable and reusable. In cases where maintaining state is unavoidable, such as using flags for path changes or step transitions, explicit resets are introduced to prevent previous errors from affecting the operation. This approach achieves a balance between simplicity, reliability, and precise control of the system.


<details open>
<summary>⚙️ Obtacle Challenge Main Code </summary>

```cpp
#include <Arduino.h>
#include <Bounce2.h>
#include <math.h> 
#include "PID.h"
#include "Robot.h"
#include "paths.h"  
#include "Rectification.h" 


// === OBJECTS ===
Bounce button = Bounce();
PID pursuit_pid(0.6, 0.0,0.1); 
PID pid(170, 50, 150);
Robot robot;
Rectification rect;


// === PATH SELECTION ===
int currentPath = 0;
const float* current_path_x;
const float* current_path_y;
int current_n_points;

// === PARAMETERS ===
float x_pos=0, y_pos=0, heading=0;
float f_dist=0, o_dist=0, i_dist=0;
int step = 0;
float steer_angle = 0;
char direction = 'A';
float setpointArr[4] = {0.2, 0.4, 0.5, 0.8};
int setpoint = 0; // this variable stores the index into the array
float offset = 0 ,angle_errorr = 0;
bool activo = false, terminado = false; 
bool stepActivated[10] = {false};
char feedbackAxis = 'x'; // or 'y'
float limit=0;
int lastStep = step;

// === 2D ROUND ===
char blocklayout[4][2] = { {'N','N'}, {'N','N'}, {'N','N'}, {'N','N'} };
char blocklayoutt[] = {'O', 'I', 'O', 'C', 'D', 'E'};  // your sequence
int blockIndex = 0;  // current position

int zone = 0; // there are 4 zones (0,1,2,3)
int lap = 0;
float curva=0.3;
char lane='N';


// === PINOUT ===
const int buttonPin = 13;
const int builtinLed = 25;
const int BUZZER_PIN = 12;

// === UPDATE TIME ===
unsigned long lastTime = 0;
const unsigned long interval = 10; // milliseconds

unsigned long lastRect = 0;
const unsigned long rectEveryMs = 50;

// === PURSUIT PARAMETERS ===
float lookahead_dist = 0.2; 
bool pursuit_done = false;
bool pursuit_started = false;
float x_start = 0, y_start = 0;
```
</details>

### HELPERS (paths, pursuit, comms, layout, step tracking)

In this section, helper functions are implemented to handle essential tasks such as selecting the path to follow, calculating angular error for steering, ensuring safe communication with the Raspberry Pi through timeout mechanisms, correcting the lane layout, and managing step latching. The goal is to keep these functions as independent as possible, operating only on their inputs without relying on hidden states, which makes them more predictable and reusable. In cases where maintaining state is unavoidable, such as using flags for path changes or step transitions, explicit resets are introduced to prevent previous errors from affecting the operation. This approach achieves a balance between simplicity, reliability, and precise control of the system.
 
<details open>
<summary>⚙️ Obtacle Challenge Main Code </summary>
  
  ```cpp
void updatePath(int index){
  currentPath = index;
  current_path_x = path_x[index];
  current_path_y = path_y[index];
  current_n_points = path_sizes[index];
  pursuit_started = false;
  pursuit_done = false;
}

float getPurePursuitAngleError() {
    bool absolute = true;     // here you still need to decide which paths are relative vs absolute

    if (!pursuit_started) { 
        x_start = x_pos; 
        y_start = y_pos; 
        pursuit_started = true; 
    }

    float offX = absolute ? 0.0f : x_start;
    float offY = absolute ? 0.0f : y_start;

    // 1) Closest point
    int   closest  = 0;
    float min_dist = 1e9f;
    for (int i = 0; i < current_n_points; ++i) {
        float px = current_path_x[i] + offX;
        float py = current_path_y[i] + offY;
        float dx = px - x_pos, dy = py - y_pos;
        float d  = sqrt(dx*dx + dy*dy);
        if (d < min_dist) { min_dist = d; closest = i; }
    }

    // 2) Lookahead point
    int lookahead = current_n_points - 1;
    for (int i = closest; i < current_n_points; ++i) {
        float px = current_path_x[i] + offX;
        float py = current_path_y[i] + offY;
        float dx = px - x_pos, dy = py - y_pos;
        float d  = sqrt(dx*dx + dy*dy);

        if (d > lookahead_dist) { lookahead = i; break; }
    }

    // 3) Stop condition
    if (closest >= current_n_points - 11) {
        pursuit_started = false;
        pursuit_done = true;
        return 0.0f;
    }

    // 4) Angle error
    float tx = current_path_x[lookahead] + offX;
    float ty = current_path_y[lookahead] + offY;
    float dx = tx - x_pos, dy = ty - y_pos;
    float target_angle = atan2(dx, dy) * 180.0f / 3.14159265f;

    float angle_err = -(target_angle - heading);

    return angle_err;
}

char waitFromPi(unsigned long timeout_ms = 100) {
  unsigned long start = millis();
  while (!Serial1.available()) {
    if (millis() - start > timeout_ms) {
      robot.setDriveSpeed(0);   // stop the robot for safety
      robot.detachSteering();   // release steering
      while(true){}
      return 0;                 // or 'X' to indicate timeout
    }
  }
  return Serial1.read();
}
/*
char requestLaneFromPi() {
  Serial1.println('R');          // send the command to Pi
  return waitFromPi(100); // wait for the reply
}
*/

char requestLaneFromPi() {
  char result = blocklayoutt[blockIndex];
  // advance index
  blockIndex++;
  return result;
}


void fixBlockLayout() {
    for (int i = 0; i < 4; i++) {
        // Case 1: if left is 'E' and right is 'O' or 'I'
        if (blocklayout[i][0] == 'E' &&
           (blocklayout[i][1] == 'O' || blocklayout[i][1] == 'I')) {
            blocklayout[i][0] = blocklayout[i][1];
        }
        // Case 2 (vice versa): if right is 'E' and left is 'O' or 'I'
        else if (blocklayout[i][1] == 'E' &&
                (blocklayout[i][0] == 'O' || blocklayout[i][0] == 'I')) {
            blocklayout[i][1] = blocklayout[i][0];
        }
    }
}

void updateStep() {
    if (step != lastStep) {
        stepActivated[lastStep] = false; // deactivate the step you just left
        lastStep = step;                 // update tracker
    }
}
```
</details>

### SETUP (hardware init and startup handshake)

In this section, the system sets up the essential hardware interfaces by initializing Serial1, the robot object, pin configurations, and the debounced button. Once the basic components are prepared, the program waits for the Raspberry Pi to signal that it is ready, ensuring proper synchronization between devices. Only after receiving this confirmation does the robot respond by sending its own ready signal. This process relies on functions like begin(), attach(), and interval() to configure serial communication, input handling, and timing. A blocking wait with built-in timeout protection is used during the handshake phase, guaranteeing that the robot does not begin motion until communication is established safely, preventing misalignment or unsafe startup conditions.
   
<details open>
<summary>⚙️ Obtacle Challenge Main Code </summary>
  
 ```cpp
void setup() {
    Serial1.begin(115200);
    robot.begin();

    pinMode(builtinLed, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    button.attach(buttonPin, INPUT_PULLUP);
    button.interval(50);

    waitFromPi(6000);
    digitalWrite(builtinLed, HIGH);
 
}
```

</details>


### PERIODIC TASKS (inside loop: control + rectification)
In this section, the system sets up the essential hardware interfaces by initializing Serial1, the robot object, pin configurations, and the debounced button. Once the basic components are prepared, the program waits for the Raspberry Pi to signal that it is ready, ensuring proper synchronization between devices. Only after receiving this confirmation does the robot respond by sending its own ready signal. This process relies on functions like begin(), attach(), and interval() to configure serial communication, input handling, and timing. A blocking wait with built-in timeout protection is used during the handshake phase, guaranteeing that the robot does not begin motion until communication is established safely, preventing misalignment or unsafe startup conditions.

<details open>
<summary>⚙️ Obtacle Challenge Main Code </summary>

```cpp
void loop() {

    unsigned long now = millis();
    button.update();
    updateStep();

    if (button.fell() && ! terminado) {
      activo = !activo;
      if (!activo) terminado = true;
    }

    if (!activo || terminado) {
      
      if(terminado){
        robot.setDriveSpeed(0);
        robot.detachSteering();
      }
      return;
    }

    // PROCESSING (fast control loop)
    if (now - lastTime >= interval) {
        lastTime = now;
        robot.updatePose();
        x_pos = robot.getPose('x');
        y_pos = robot.getPose('y');
        heading = robot.getPose('h');

        if (pid.isEnabled()) {
            offset = (feedbackAxis == 'x') ? x_pos : y_pos;
            steer_angle=pid.compute(setpointArr[setpoint], offset);
        }
        else if(pursuit_pid.isEnabled()){
            angle_errorr = getPurePursuitAngleError();
            steer_angle = pursuit_pid.compute(0.0, angle_errorr);
        }
        robot.setSteerAngle(steer_angle);
    }

     // RECTIFICATION (slower cadence)
    if (now - lastRect >= rectEveryMs) {
      lastRect = now;
      if (rect.isEnabled()) {
        float x_measured = robot.getPoseXFromSensors(setpoint);
        if(x_measured>0.0f){
          rect.sample(y_pos, x_measured);
        }
      }
    }

```
</details>

### STATE MACHINE (steps 0–9)
In this stage, the system continuously monitors the button input to toggle between run and stop modes, updates the robot’s pose at a high frequency, calculates steering commands using either a PID controller or Pursuit algorithm, and executes rectification routines at a slower pace. To manage these different tasks efficiently, two timers are employed: one (interval) dedicated to fast control loop updates for smooth and responsive motion, and another (rectEveryMs) that handles slower correction sampling without interfering with the main control flow. This separation of timing ensures that critical control updates happen with minimal delay, while background corrections run at a sustainable rate, maintaining both stability and efficiency in the robot’s overall behavior.


<details open>
<summary>⚙️ Obtacle Challenge Main Code </summary>

```cpp
    // INITIAL ZONE
    if (step == 0) {   
        if (!stepActivated[step]) {
            
            if(robot.getDistance('O')>0.25){
              direction = 'H';
              robot.setDir(direction);
              Serial1.println(direction); 
            }
            else{
              Serial1.println(direction); 
            }
            
            steer_angle=28;
            robot.setSteerAngle(steer_angle);
            delay(400);
            
            robot.setDriveSpeed(0.3);
            robot.setPoseX(0.17);
            robot.setPoseY(direction == 'A' ? (2.0 - 0.2) : (1.0 + 0.1)); // this needs verification
            stepActivated[step] = true;
        }

        if (heading >= 60) {
          lane = requestLaneFromPi();

          if (direction == 'A') {
            if (lane == 'I') { 
              updatePath(0); 
              setpoint = 3; 
              }
            else {
              lane = requestLaneFromPi();
              blocklayout[1][0]=lane;
              updatePath(lane=='O' ? 2 : lane=='I' ? 1 : 3);
              setpoint = lane=='O' ? 0 : lane=='I' ? 3 : 2;
            }
          } 
          else {
            blocklayout[0][1]=lane;
            updatePath(lane == 'I' ? 4 : 5);
            setpoint = (lane == 'I' ? 3 : 0);
          }
          step++;
        }
  }


    // Path after parking
    if (step == 1) {
      if (!stepActivated[step]) {
        pursuit_pid.enable();
        stepActivated[step] = true;
      }

      if (pursuit_done) {
        pursuit_pid.disable();
        pursuit_done = false;
        step++;
      }
    }

 
    // TRANSITION ZONE
    if (step == 2) {
      if (!stepActivated[step]) {
        pid.reset();
        pid.enable();
        zone++;
        if (zone == 4) zone = 0;
        if (zone == 1) lap++;

        if (lap > 1 && y_pos < 1.5) {
          if (zone == 0 && setpoint == 1 && direction == 'A')
            rect.enable(1.0f, 1.6f);
          else if (zone == 0 && setpoint == 1 && direction == 'H')
            rect.enable(1.4f, 1.8f);
          else
            rect.enable(1.0f, 1.8f);
        }

        stepActivated[step] = true;
      }

      if (y_pos >= 1.9) {
        pid.disable();

        // Rectification
        if (rect.isReady()) {
          float yaw = rect.getYawDeg();
          if (fabs(heading - yaw) < 4) heading = yaw;
        }

        // Absolute positioning
        if(!(direction == 'A' && setpoint == 1)){
          float reading = robot.getPoseXFromSensors(setpoint);
          x_pos = (reading > 0) ? reading : x_pos;
        }

        robot.setPoseY(x_pos);
        robot.setPoseX(3 - y_pos);
        robot.setPoseH(heading-90);  
        x_pos = robot.getPose('x');
        y_pos = robot.getPose('y');
        heading = robot.getPose('h');

        if (direction == 'A' && lap == 1 && zone == 1 && currentPath != 0) {
            step = 6;
        } 
        else if (lap == 3 && zone == 0) {
            step = 8;
        } 
        else {
            step = 3;
        }

      }
    }

    
    // === START OF CURVE ===
    // STRAIGHT LINE
    if (step == 3) {
      if (!stepActivated[step]) {
        if(lap==2 && zone==1)fixBlockLayout();
        lane=blocklayout[zone][0];
        if (setpoint == 3 && lane == 'N' ) blocklayout[zone][0] = requestLaneFromPi() ; 
        feedbackAxis = 'y';
        pid.reset();

        limit = (lane == 'O') ? (zone == 0 ? setpointArr[1] : setpointArr[0])
            : (lane == 'I') ? setpointArr[3]
            : setpointArr[2];

        stepActivated[step] = true;
      }

      if (x_pos <= (limit + curva) ) {
        setpoint = (lane == 'O') ? (zone == 0 ? 1 : 0)
                : (lane == 'I') ? 3
                : 2;
        pid.disable();
        step++;
      }
    }


    // 90 DEGREES TURN
    if (step == 4) {
      if (!stepActivated[step]) {
        updatePath(6);
        pursuit_pid.reset();
        pursuit_pid.enable();
        stepActivated[step] = true;
      }

      if (pursuit_done) {
        pursuit_pid.disable();
        pursuit_done = false;

        if(y_pos>1){
        // Absolute positioning
          float reading = robot.getPoseXFromSensors(setpoint);
        }
        else if(!(direction == 'H' && setpoint == 1 )){
          float reading = robot.getPoseXFromSensors(0);
        }
        x_pos = (reading > 0) ? reading : x_pos;

        lane = blocklayout[zone][0];
        if (setpoint == 2 && lane == 'N') {
            lane = requestLaneFromPi();
            blocklayout[zone][0] = lane;
            step = (lane == 'E') ? 6 : 5;
        }
        else {
          step = 6;
        }

      }
    }


    // AUXILIARY ALIGNMENT
    if (step == 5) {
      if (!stepActivated[step]) {
        lane=blocklayout[zone][0];
        if (lane == 'O') {
          updatePath(zone == 0 ? 8 : 7);
          setpoint = (zone == 0 ? 1 : 0);
        } 
        else {
          updatePath(9);
          setpoint = 3;
        }
        pursuit_pid.reset();
        pursuit_pid.enable();
        stepActivated[step] = true;
      }

      if (pursuit_done) {
        pursuit_pid.disable();
        pursuit_done = false;
        step++;
      }
    }



    // SECOND STRAIGHT LINE 
    if (step == 6) {
      if (!stepActivated[step]) {
        feedbackAxis = 'x';
        pid.reset();
        pid.enable();
        stepActivated[step] = true;
      }

      if (y_pos >= 1) {
        pid.disable();
        step++;
      }
    }
    // === END OF CURVE ===



    // LAST STRAIGHT
    if (step == 7) {
      if (!stepActivated[step]) {
        lane=requestLaneFromPi();
        blocklayout[zone][1]=lane;
        if (setpoint == 0 && lane == 'I') updatePath(10);
        else if (setpoint == 1 && lane == 'I') updatePath(11);
        else if (setpoint == 2) updatePath(lane == 'I' ? 9 : (zone == 0 ? 8 : 7));
        else if (setpoint == 3 && lane == 'O') updatePath(zone == 0 ? 13 : 12);
        else pursuit_done = true;
        pursuit_pid.reset();
        pursuit_pid.enable();
        stepActivated[step] = true;
      }

      if (pursuit_done) {
        pursuit_pid.disable();
        pursuit_done = false;
        step = 2;
      }
    }

    // PARKING SEQUENCE
    if (step == 8){
                  /* PARKING CODE GOES HERE
              terminado=true;
              robot.setDriveSpeed(0);
              robot.setServoPWM(0);
              */
    }

    // FULL STOP
    if (step == 9){
        terminado=true;
    }
}

```
</details>

