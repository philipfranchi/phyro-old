#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <jpeglib.h>
#include "phyro.h"

unsigned int i2c_out( register unsigned int data )
{
 volatile unsigned int i= 0;   //will be register
 unsigned int ack;

 //Make SDA output
 gpio_set_dir(GPIO_CAM_SDA, 1);

 //output eight bits of 'data'
 for( ; i < 8; ++i ) {
  //send the data bit
  if( data & 0x80 ) gpio_set_value(GPIO_CAM_SDA, 1);
  else gpio_set_value(GPIO_CAM_SDA, 0);

  //Set Clock High
  gpio_set_value(GPIO_CAM_SCL, 1);

  //Set Clock Low
  gpio_set_value(GPIO_CAM_SCL, 0);

  //shift next data bit
  data= data << 1;
 }

 //Make SDA input
 gpio_set_dir(GPIO_CAM_SDA, 0);

 //Set Clock High
 gpio_set_value(GPIO_CAM_SCL, 1);

 //get the ack bit
 gpio_get_value(GPIO_CAM_SDA, &ack);

 //Set Clock Low
 gpio_set_value(GPIO_CAM_SCL, 0);

 return ack;
}

//Assumes the IC2_MASTER_SCL is low
unsigned char i2c_in()
{
 unsigned char data;
 volatile unsigned int i= 0;
 int input;

 data= 0;

 //Make SDA input
 gpio_set_dir(GPIO_CAM_SDA, 0);

 for( ; i < 8; ++i ) {
  //Set Clock High
  gpio_set_value(GPIO_CAM_SCL, 1);

  //shift the bit over
  data= data << 1;

  gpio_get_value(GPIO_CAM_SDA, &input);
  if(input) data|= 0x01;

  //Set Clock Low
  gpio_set_value(GPIO_CAM_SCL, 0);
 }

 //ACK
 gpio_set_dir(GPIO_CAM_SDA, 1);
 gpio_set_value(GPIO_CAM_SDA, 1);

 //Set Clock High
 gpio_set_value(GPIO_CAM_SCL, 1);

 //Set Clock Low
 gpio_set_value(GPIO_CAM_SCL, 0);

 return(data);
}

void i2c_start()
{
 //Make SDA, SCL outputs
 gpio_set_dir(GPIO_CAM_SCL, 1);
 gpio_set_dir(GPIO_CAM_SDA, 1);

 gpio_set_value(GPIO_CAM_SDA, 1);
 gpio_set_value(GPIO_CAM_SCL, 1);
 gpio_set_value(GPIO_CAM_SDA, 0);
 gpio_set_value(GPIO_CAM_SCL, 0);
}

//Assumes the clock is low
void i2c_stop(){
 //Make SDA, SCL outputs
 gpio_set_dir(GPIO_CAM_SCL, 1);
 gpio_set_dir(GPIO_CAM_SDA, 1);

 gpio_set_value(GPIO_CAM_SDA, 0);
 gpio_set_value(GPIO_CAM_SCL, 1);
 gpio_set_value(GPIO_CAM_SDA, 1);
}

int camera_i2c_write(unsigned int address, unsigned int data)
{
 int retval = 0;

 i2c_start();
 if(i2c_out(0x60)) {
  flukelog("ERROR: %s ack missing on byte 1\n", __FUNCTION__);
  retval = -1;
 }
 if(i2c_out(address)) {
  flukelog("ERROR: %s ack missing on byte 2\n", __FUNCTION__);
  retval = -2;
 }
 if(i2c_out(data)) {
  flukelog("ERROR: %s ack missing on byte 3\n", __FUNCTION__);
  retval = -3;
 }
 i2c_stop();

 return(retval);
}

// BUG: this function doesn't work - no idea why - looks good on scope
int camera_i2c_read(unsigned int address, unsigned char *data)
{
 int retval = 0;

 i2c_start();
 if(i2c_out(0x60)) {
  flukelog("ERROR: %s ack missing on write byte 1\n", __FUNCTION__);
  retval = -1;
 }
 if(i2c_out(address)) {
  flukelog("ERROR: %s ack missing on write byte 2\n", __FUNCTION__);
  retval = -2;
 }
 i2c_stop();

 i2c_start();
 if(i2c_out(0x61)) {
  flukelog("ERROR: %s ack missing on write byte 3\n", __FUNCTION__);
  retval = -3;
 }
 if(data) *data = i2c_in();
 i2c_stop();

 return(retval);
}

// A gain parameter of zero will use the fluke2 default gain.
// A positive gain is brighter and a negative gain is darker.
// The fluke2 camera allows for auto exposure/gain targets so leave
//   AGC and AEC enabled.
int camera_set_gain(int gain)
{
 int setgain, retval = 0;

 setgain = CAMERA_DEF_GAIN + gain;
 if(setgain > 0xFF) setgain = 0xFF;
 if(setgain < 3) setgain = 3;

 //   auto exposure target - high range
 if(camera_i2c_write(0x24, setgain)) retval = -1;
 //   auto exposure target - low range
 if(camera_i2c_write(0x25, setgain - 3)) retval = -2;

 return(retval);
}

int camera_start_grab_image()
{
 int fd, ret;

 fd = open(CAMERADEVICE, O_RDONLY | O_NONBLOCK);
 if(fd < 0) {
  flukelog("ERROR: %s failed opening camera device: %s\n", __FUNCTION__, strerror(errno));
  return(-1);
 }

 // executing a read starts the image capture routine which takes 1 sec
 // this read is nonblocking so it will return immediately
 // no data is stored

 ret = read(fd, NULL, RAWIMAGESIZE);
 if(ret < 0) {
  if(errno != EINTR && errno != EAGAIN) {
   flukelog("ERROR: %s failed reading from camera device: %s\n", __FUNCTION__, strerror(errno));
   close(fd);
   return(-1);
  }
 }

 return(fd);
}

static void jpeg_init_destination (j_compress_ptr cinfo)
{
    /* jpeg empty routine needed to support libjpeg */
}

static boolean jpeg_empty_output_buffer (j_compress_ptr cinfo)
{
    flukelog("ERROR: JPEG compressor ran out of buffer space\n");
    return TRUE;
}

static void jpeg_term_destination (j_compress_ptr cinfo)
{
    /* jpeg empty routine needed to support libjpeg */
}

int camera_image_compress(char *cambuf, char *jpegbuf, int *jpegsize, int jpegquality, int colorflag)
{
 int stride;
 struct jpeg_compress_struct cinfo;
 struct jpeg_error_mgr jerr;
 struct jpeg_destination_mgr jdest;
 JSAMPROW jpeg_row;

 cinfo.err = jpeg_std_error(&jerr);
 jpeg_create_compress(&cinfo);

 jdest.next_output_byte = jpegbuf;
 jdest.free_in_buffer = *jpegsize;
 jdest.init_destination = jpeg_init_destination;
 jdest.empty_output_buffer = jpeg_empty_output_buffer;
 jdest.term_destination = jpeg_term_destination;
 cinfo.dest = &jdest;

 cinfo.image_width = IMAGEWIDTH;
 cinfo.image_height = IMAGEHEIGHT;

 if(colorflag) {
  cinfo.input_components = 3;
  cinfo.in_color_space = JCS_RGB;
  stride = IMAGEWIDTH*3;
 }
 else {
  cinfo.input_components = 1;
  cinfo.in_color_space = JCS_GRAYSCALE;
  stride = IMAGEWIDTH*1;
 }

 jpeg_set_defaults(&cinfo);
 jpeg_set_quality(&cinfo, jpegquality, TRUE);

 jpeg_start_compress(&cinfo, TRUE);

 while (cinfo.next_scanline < cinfo.image_height) {
   jpeg_row = (JSAMPROW)(cambuf + cinfo.next_scanline * stride);
   jpeg_write_scanlines(&cinfo, &jpeg_row, 1);
 }

 jpeg_finish_compress(&cinfo);
 *jpegsize -= jdest.free_in_buffer;
 jpeg_destroy_compress(&cinfo);

 return(0);
}

void bayer_demosaic(unsigned char *rgb, unsigned char *bayer, int width, int height)
{
 unsigned int x, y, i;
 unsigned char *bayerptr;

 i=0;
 bayerptr = bayer;
 for(y=0; y < height; y+=2) {
  for(x=0; x < width; x+=2) {
   rgb[i++] = bayerptr[width + 1];
   rgb[i++] = (bayerptr[1] + bayerptr[width]) >> 1;
   rgb[i++] = bayerptr[0];
   bayerptr++;

   rgb[i++] = bayerptr[width];
   rgb[i++] = bayerptr[0];
   rgb[i++] = bayerptr[-1];
   bayerptr++;
  }

  for(x=0; x < width; x+=2) {
   rgb[i++] = bayerptr[1];
   rgb[i++] = bayerptr[0];
   rgb[i++] = bayerptr[-width];
   bayerptr++;

   rgb[i++] = bayerptr[0];
   rgb[i++] = (bayerptr[-1] + bayerptr[-width]) >> 1;
   rgb[i++] = bayerptr[-width-1];
   bayerptr++;
  }
 }
}

void image_rgb2gray(unsigned char *rgb)
{
 unsigned int i;
 unsigned char y;
 unsigned char *rgbptr, *rgbend;

 i = 0;
 rgbptr = rgb;
 rgbend = rgb + RAWIMAGESIZE * 3;

 // Y = 0.299R + 0.587G + 0.114B

 while(rgbptr < rgbend) {
  y = (rgbptr[0] * ((int)((0.299) * (1<<FIXEDSHIFT))) +
       rgbptr[1] * ((int)((0.587) * (1<<FIXEDSHIFT))) +
       rgbptr[2] * ((int)((0.114) * (1<<FIXEDSHIFT)))) >> FIXEDSHIFT;
  rgb[i++] = y;
  rgbptr += 3;
 }
}

void image_rgb2yuv(unsigned char *rgb)
{
 unsigned char y, u, v;
 unsigned char *rgbptr, *rgbend;

 rgbptr = rgb;
 rgbend = rgb + RAWIMAGESIZE * 3;

 // Y = 0.299R + 0.587G + 0.114B
 // U = (B-Y)*0.565 + 128
 // V = (R-Y)*0.713 + 128

 while(rgbptr < rgbend) {
  y = (rgbptr[0] * ((int)((0.299) * (1<<FIXEDSHIFT))) +
       rgbptr[1] * ((int)((0.587) * (1<<FIXEDSHIFT))) +
       rgbptr[2] * ((int)((0.114) * (1<<FIXEDSHIFT)))) >> FIXEDSHIFT;
  u = ((rgbptr[2] - y) * ((int)((0.565) * (1<<FIXEDSHIFT))) +
       (128 << FIXEDSHIFT)) >> FIXEDSHIFT;
  v = ((rgbptr[0] - y) * ((int)((0.713) * (1<<FIXEDSHIFT))) +
       (128 << FIXEDSHIFT)) >> FIXEDSHIFT;

  rgbptr[0] = y;
  rgbptr[1] = u;
  rgbptr[2] = v;
  rgbptr += 3;
 }
}

// fluke1 raw image format
void image_rgb2vyuy(unsigned char *rgb)
{
 unsigned int i;
 unsigned char y, u, v;
 unsigned char *rgbptr, *rgbend;

 i = 0;
 rgbptr = rgb;
 rgbend = rgb + RAWIMAGESIZE * 3;

 // Y = 0.299R + 0.587G + 0.114B
 // U = (B-Y)*0.565 + 128
 // V = (R-Y)*0.713 + 128

 while(rgbptr < rgbend) {
  y = (rgbptr[0] * ((int)((0.299) * (1<<FIXEDSHIFT))) +
       rgbptr[1] * ((int)((0.587) * (1<<FIXEDSHIFT))) +
       rgbptr[2] * ((int)((0.114) * (1<<FIXEDSHIFT)))) >> FIXEDSHIFT;
  v = ((rgbptr[0] - y) * ((int)((0.713) * (1<<FIXEDSHIFT))) +
       (128 << FIXEDSHIFT)) >> FIXEDSHIFT;

  rgb[i++] = v;
  rgbptr += 3;

  y = (rgbptr[0] * ((int)((0.299) * (1<<FIXEDSHIFT))) +
       rgbptr[1] * ((int)((0.587) * (1<<FIXEDSHIFT))) +
       rgbptr[2] * ((int)((0.114) * (1<<FIXEDSHIFT)))) >> FIXEDSHIFT;

  rgb[i++] = y;
  rgbptr += 3;

  y = (rgbptr[0] * ((int)((0.299) * (1<<FIXEDSHIFT))) +
       rgbptr[1] * ((int)((0.587) * (1<<FIXEDSHIFT))) +
       rgbptr[2] * ((int)((0.114) * (1<<FIXEDSHIFT)))) >> FIXEDSHIFT;
  u = ((rgbptr[2] - y) * ((int)((0.565) * (1<<FIXEDSHIFT))) +
       (128 << FIXEDSHIFT)) >> FIXEDSHIFT;

  rgb[i++] = u;
  rgbptr += 3;

  y = (rgbptr[0] * ((int)((0.299) * (1<<FIXEDSHIFT))) +
       rgbptr[1] * ((int)((0.587) * (1<<FIXEDSHIFT))) +
       rgbptr[2] * ((int)((0.114) * (1<<FIXEDSHIFT)))) >> FIXEDSHIFT;

  rgb[i++] = y;
  rgbptr += 3;
 }
}

void yuv2rgb(unsigned char *r, unsigned char *g, unsigned char *b,
             unsigned char y, unsigned char u, unsigned char v)
{
 float r_tmp, g_tmp, b_tmp;

 r_tmp = y + 1.403*((float)v-128);
 g_tmp = y - 0.344*((float)u-128) - 0.714*((float)v-128);
 b_tmp = y + 1.770*((float)u-128);

 if(r_tmp < 0) r_tmp=0;
 if(r_tmp > 255) r_tmp=255;
 if(g_tmp < 0) g_tmp=0;
 if(g_tmp > 255) g_tmp=255;
 if(b_tmp < 0) b_tmp=0;
 if(b_tmp > 255) b_tmp=255;

 *r = (unsigned char)r_tmp;
 *g = (unsigned char)g_tmp;
 *b = (unsigned char)b_tmp;
}

