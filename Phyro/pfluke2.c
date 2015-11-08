#include "phyro.h"

struct camera_control camctrl;

//Defined in misc.c
char *errorlog = NULL;
int errorlog_pos = 0;

//Defined in fluke2.c
unsigned char scribbler_orientation;
int last_ir_power = 0;

int readRet, writeRet;

int init(){
	//Error init
	errorlog = (char *)malloc(ERRORLOGSIZE + 2);
	errorlog_pos = 0;
	memset(errorlog, 0, ERRORLOGSIZE + 2);

	//Camera Init
	camctrl.fd = 0;
	camctrl.command = 0;
	camctrl.client = NULL;
	camctrl.imagetimestamp = 0;
	camctrl.colorflag = 1;
	camctrl.dojpeg = 1;
	camctrl.jpegquality = JPEG_QUALITY_GOOD;
 	camctrl.image = (char *)malloc(RAWIMAGESIZE * 3 + 20);
 	
 	if(!camctrl.image) {
  		flukelog("ERROR: main initialization failed allocating image_rgb memory\n");
  		exit(1);
	}

	 // is this enough space ?
 	camctrl.jpegmyro = (char *)malloc(RAWIMAGESIZE + 20);
 	if(!camctrl.jpegmyro) {
  		flukelog("ERROR: main initialization failed allocating jpeg memory\n");
  		exit(1);
	 }
	 // myro jpeg format has an extra 2 byte header
 	camctrl.jpeg = camctrl.jpegmyro + 2;

  int fd = open(SCRIBBLERTTY, O_RDWR | O_NONBLOCK);

	return(fd);
}

int fluke_get_errors(char * buf){
	strncpy(buf,errorlog,ERRORLOGSIZE);
	return(0);
}

int fluke_get_image(char* buf){
	int i, ret;
	time_t now;

	// check if there is already a recent image in the buffer
	now = time(NULL);
	if(now - camctrl.imagetimestamp <= IMAGE_EXPIRE_SECONDS) {
 		image_rgb2vyuy(camctrl.image);
    for(i = 0; i < (RAWIMAGESIZE * 3 + 20); i++){
      buf[i] = camctrl.image[i];  
    }
		return(0);
	}

	if(camctrl.fd) {
 		flukelog("ERROR: %s waiting on old image grab to complete\n", __FUNCTION__);
  		return(-1);
	}

 	ret = camera_start_grab_image();
 	if(ret <= 0) {
  		flukelog("ERROR: %s camera_start_grab_image failed\n", __FUNCTION__);
  		return(-1);
 	}
 	camctrl.fd = ret;
 	camctrl.colorflag = 1;

 	return(0);
}

int fluke_get_battery(){
	int ret, raw, final;
	float conv;

	ret = read_a2d(0, &raw, NULL);
	if(ret) {
		flukelog("ERROR: %s read_a2d failed\n", __FUNCTION__);
		return(-1);
	}
	conv = (float)raw / 4.382;
	final = (int)conv;
	return(final);
}

int fluke_get_blob(){
  return(0);
}

int fluke_set_led_on()
{
 // this LED on the fluke2 is used for CPU load so use the bright LED instead
 set_pwm(BRIGHT_LED_DEFAULT_PWM);
 gpio_set_value(GPIO_BRIGHT_LED, 1);

 return(0);
}

int fluke_set_led_off()
{
 // this LED on the fluke2 is used for CPU load so use the bright LED instead
 gpio_set_value(GPIO_BRIGHT_LED, 0);
 // IR pwm power is shared with the bright LED
 if(last_ir_power) set_pwm(last_ir_power);

 return(0);
}

int fluke_get_ir_left(char * buf){
 // fluke2 only has a center IR emitter/sensor
	return(fluke_get_ir_center(buf));
}

int fluke_get_ir_center(char * buf){
 int i, val, cnt;

 cnt = 0;

 for(i=0;i<10;i++) {

  // with the code below GPIO_IROUT will be low for about 1-2ms
  // delay from starting pulses to sensor going low is 180us
  // delay from stopping pulses to the sensor going high is 240us

  // turn IR emitter pulses on
  gpio_set_value(GPIO_IROUT, 0);
  // check sensor
  gpio_get_value(GPIO_IRIN, &val);
  // turn IR emitter pulses off
  gpio_set_value(GPIO_IROUT, 1);

  // IR sensor is active low
  if(!val) cnt++;

  // duty cycle of output pulse train must be less than 40%
  //  total delay includes another 1-2ms from gpio calls
  udelay(1000);

  // should be no IR return now because the output pulses are off
  //   if the IR sensor is high its a false positive so decrease 
  //   the pulse counter
  gpio_get_value(GPIO_IRIN, &val);

  if(!val) cnt--;
 }

 // fluke1 value ranged from 0 to 6400
 if(cnt < 0) cnt = 0;
 cnt *= (6400/10);

 buf[0] = ((cnt >> 8) & 0xFF);  // high byte of 16 bit result
 buf[1] = (cnt & 0xFF);         // low byte of 16 bit result

 return(0);
}

int fluke_get_ir_right(char * buf){
	// fluke2 only has a center IR emitter/sensor
	return(fluke_get_ir_center(buf));
}

int fluke_set_bright_led(char * bit){
 int pwmval;

 if(*bit != 0) {
  pwmval = *bit << 4;
  set_pwm(pwmval);
  gpio_set_value(GPIO_BRIGHT_LED, 1);
 }
 else {
  gpio_set_value(GPIO_BRIGHT_LED, 0);
  // IR pwm power is shared with the bright LED
  if(last_ir_power) set_pwm(last_ir_power);
 }

 return(0);
}

int fluke_set_forwardness(char* bit){
 scribbler_orientation = *bit;

 if(scribbler_orientation == 0) {
  scribbler_orientation = 0xDF;
  flashdata_write(&scribbler_orientation, 0, 1);
  scribbler_orientation = 0;
 }
 else {
  scribbler_orientation = 1;
  flashdata_write(&scribbler_orientation, 0, 1);
 }

 return(0);
}

int fluke_white_balance_on(){
 // restore defaults - enable automatic white balance correction
 camera_i2c_write(0x38, 0x10);
 camera_i2c_write(0x96, 0xF9);

 return(0);
}

int fluke_white_balance_off(){
 // disable automatic white balance correction
 camera_i2c_write(0x38, 0x00);
 camera_i2c_write(0x96, 0xE9);

 return(0);
}

int fluke_set_camera_param(char * bit1, char* bit2)
{
 unsigned char address, data;

 address = *bit1;
 data = *bit2;

 // to allow backward compatiblity intercept the commonly used 
 //  address/data combos used with the fluke1
 // fluke2 camera can set the combined auto exposure/gain target so there 
 //  is no need to disable agc/aec or program the exposure/gain individually.

 if(address == 0x12 && data == 0x14) {
  // enable automatic white balance correction
  // camera_i2c_write(0x38, 0x10);
  // camera_i2c_write(0x96, 0xF9);
 }
 else if(address == 0x12 && data == 0x10) {
  // disable automatic white balance correction
  // camera_i2c_write(0x38, 0x00);
  // camera_i2c_write(0x96, 0xE9);
 }
 else if(address == 0x13 && data == 0xA3) {
  // enable auto exposure and gain control
  // camera_i2c_write(0x13, 0x85);
 }
 else if(address == 0x13 && data == 0xA0) {
  // disable auto exposure and gain control
  // camera_i2c_write(0x13, 0x00);
 }
 else if(address == 0x01) {
  // auto white balance blue channel gain - fluke1 default is 0x80
 }
 else if(address == 0x02) {
  // auto white balance red channel gain - fluke1 default is 0x80
 }
 else if(address == 0x00) {
  // set manual gain level - fluke1 default is 0x00
  camera_set_gain(data-128);
 }
 else if(address == 0x06) {
  // set manual gain level - fluke1 default is 0x80
  // camera_set_gain((int)data - 0x80);
 }
 else if(address == 0x10) {
  // set manual exposure level - fluke1 default is 0x41
  // disable to allow myro darkenCamera to work
  // camera_set_gain((int)data - 0x41);
 }
 else camera_i2c_write(address, data);

 return(0);
}




/***************************************************************
Read and write to port
***************************************************************/
int write_to_port(char * string, int size, int fd){
        int i;
        writeRet = write(fd, string, size);
        return writeRet;
}

int read_port(char* buf, int size, int fd){
        int numRead = 0;
        int timer = 0;
        int ret;
        while(numRead < size){
                ret = read( fd, buf+numRead, size-numRead);
                if(ret <= 0){
                        printf("Read returned %d with error %d: %s\n",ret,errno,strerror(errno));
                        timer++;
                        if(timer>size){
                                return -1;
                        }
                }
                else{
                        numRead += ret;
                        timer = 0;
                        printf("%d Bytes read now for a total of %d with %d left to read\n",ret,numRead,size-numRead);
                }
        }
        return numRead-size;
}

int test_buf(char* buf){
  printf("Called on %s\n", buf);
  int i;
  for(i = 0; i < 10000; i ++){
    *(buf+i) = (char) 42;
  }
  return(0);
}