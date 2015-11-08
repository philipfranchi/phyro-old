//#include <bluetooth/sdp.h>
//#include <bluetooth/sdp_lib.h>

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>

#define SCRIBBLER_IN_LENGTH 9
#define SCRIBBLER_OUT_LENGTH 11

#define DEBUGPRINTCONSOLE 1

#define FLUKE2_VERSION "fluke:3.0.5"

#define SCRIBBLERTTY       "/dev/ttyfiq"
#define CAMERADEVICE       "/dev/spidev0.0"
#define NONFSDATADEVICE    "/dev/mmcblk0p3"
#define NONFSDATA_LEGACYFLASH_OFFSET  16384

#define SCRIBCMD_GET_INFO       80
#define SCRIBCMD_SET_ECHO_MODE  98
#define SCRIBCMD_SET_MOTORS     109

#define GPIOOUTPUT         1
#define GPIOINPUT          0

#define GPIO_SERVO1        1
#define GPIO_SERVO2        0
#define GPIO_SERVO3        2
#define GPIO_SERVO4        3
#define GPIO_FRONTLED      5     // used by kernel for load display
#define GPIO_IROUT         6
#define GPIO_IRIN          7
#define GPIO_SCRIB_RX      8     // used by kernel for scribbler tty driver
#define GPIO_SCRIB_TX      9     // used by kernel for scribbler tty driver
#define GPIO_SCRIB_RST     10    
#define GPIO_CAM_SCL       11
#define GPIO_CAM_SDA       12
#define GPIO_PICINIT       13    // used by kernel for SPI driver
#define GPIO_BRIGHT_LED    14

#define BRIGHT_LED_DEFAULT_PWM  0x0B50

#define BTRXBUFSIZE       (128 * 1024)
#define BTTXBUFSIZE       4096
#define ERRORLOGSIZE      10000

#define IMAGEWIDTH            1280
#define IMAGEHEIGHT           800
#define RAWIMAGESIZE          (IMAGEWIDTH * IMAGEHEIGHT)
#define IMAGE_EXPIRE_SECONDS  2
#define JPEG_QUALITY_GOOD     80
#define JPEG_QUALITY_BAD      40
#define FIXEDSHIFT            8
#define NUM_WINDOWS           4
#define RLEBUFSIZE            0xFFFF
#define CAMERA_DEF_GAIN       78    // 0x3A

#define CALLER_MAIN           10
#define CALLER_MAIN_REPEAT    11
#define CALLER_CAMERA         12
#define CALLER_SERIAL         13

#define PROP_SHUTDOWN_CMD            0
#define PROP_DOWNLOAD_RUN_BINARY     1
#define PROP_DOWNLOAD_EEPROM         2
#define PROP_DOWNLOAD_RUN_EEPROM     3
#define PROP_DOWNLOAD_SHUTDOWN       4

#define msleep(msec) usleep(msec*1000);

struct rfcomm_client {
 int sock;
 char *rx_buf;
 char *rx_data;
 int rx_len;
 int rx_end;
 int rx_pos;
 char *tx_buf;
 char *tx_ptr;
 int tx_len;
 int tx_cnt;
 unsigned char command;
 int caller;
 char addr_str[19];
 struct btaddr {
  unsigned char b[6];
 } addr;
};

struct fluke_command {
 unsigned char cmd;
 unsigned char cmdlen;           // length of command + command data
 unsigned char responselen;      // only used for scribbler commands
 int (*process)(struct rfcomm_client *);
};

struct camera_control {
 int fd;
 unsigned char command;
 struct rfcomm_client *client;
 time_t imagetimestamp;
 int jpegsize;
 int jpegquality;
 int colorflag;
 int dojpeg;
 char *image;
 char *jpeg;
 char *jpegmyro;
};

struct serial_control {
 int fd;
 unsigned char command;
 struct rfcomm_client *client;
 char rx_buf[100];
 int rx_len;
 int rx_cnt;
};

struct camera_window {
 int xlow;
 int xhigh;
 int ylow;
 int yhigh;
 int xstep;
 int ystep;
};

struct colordef {
 unsigned char y_low;
 unsigned char y_high;
 unsigned char u_low;
 unsigned char u_high;
 unsigned char v_low;
 unsigned char v_high;
};

//Defined in misc.c
char *errorlog;
int errorlog_pos;

// functions in fluke2.c
int fluke_get_errors(char* buf);
int fluke_get_image();
int fluke_get_ir_left(char * buf);
int fluke_get_ir_center(char * buf);
int fluke_get_ir_right(char * buf);
int fluke_get_battery();
int fluke_get_blob();
int fluke_set_led_on();
int fluke_set_led_off();
int fluke_set_ir_power();
int fluke_set_bright_led(char* bit);
int fluke_set_forwardness(char* bit);
int fluke_white_balance_on();
int fluke_white_balance_off();
int fluke_set_camera_param();
int read_port(char * buf, int nbytes, int fd);
int write_port(char * buf, int nbytes, int fd);


// functions in misc.c
size_t strlcpy(char *dest, const char *src, size_t size);
size_t strlcat(char *dest, const char *src, size_t count);
int read_a2d(char channel, int *val, char *valstr);
int set_pwm(int val);
void udelay(int microsec_delay);
unsigned char crc8calc(unsigned char *buf, unsigned int len);
int flashdata_write(char *buf, int offset, int len);
int flashdata_read(char *buf, int offset, int len);

// functions in gpio.c
int gpio_export(unsigned int gpio);
int gpio_unexport(unsigned int gpio);
int gpio_set_dir(unsigned int gpio, unsigned int out_flag);
int gpio_set_value(unsigned int gpio, unsigned int value);
int gpio_get_value(unsigned int gpio, unsigned int *value);
int gpio_set_edge(unsigned int gpio, char *edge);
int gpio_fd_open(unsigned int gpio);
int gpio_fd_close(int fd);

// functions defined in camera.c
int camera_i2c_write(unsigned int address, unsigned int data);
int camera_i2c_read(unsigned int address, unsigned char *data);
int camera_set_gain(int gain);
int camera_start_grab_image();
int camera_image_compress(char *cambuf, char *jpegbuf, int *jpegsize, int jpegquality, int colorflag);
void bayer_demosaic(unsigned char *rgb, unsigned char *bayer, int width, int height);
void image_rgb2gray(unsigned char *rgb);
void image_rgb2yuv(unsigned char *rgb);
void image_rgb2vyuy(unsigned char *rgb);
void yuv2rgb(unsigned char *r, unsigned char *g, unsigned char *b,unsigned char y, unsigned char u, unsigned char v);

//phyroC.c
