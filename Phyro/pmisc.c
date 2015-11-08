#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include "phyro.h"


void flukelog(char *fmt, ...)
{
 time_t mytime;
 va_list ap;
 int size, start, bufspace;

 bufspace = 300;
 if(errorlog_pos >= ERRORLOGSIZE - bufspace) errorlog_pos = 0;
 start = errorlog_pos;

 time(&mytime);
 size = snprintf(errorlog+errorlog_pos, 15, "[%u] ", (unsigned int)mytime);
 errorlog_pos += size;
 bufspace -= size;

 va_start(ap,fmt);
 size = vsnprintf(errorlog+errorlog_pos, bufspace, fmt, ap);
 errorlog_pos += size;
 bufspace -= size;
 va_end(ap);

 errorlog[errorlog_pos]='\0';

#ifdef DEBUGPRINTCONSOLE
 printf("%s", errorlog+start);
#endif

}

/**
 * strlcpy - Copy a %NUL terminated string into a sized buffer
 * @dest: Where to copy the string to
 * @src: Where to copy the string from
 * @size: size of destination buffer
 *
 * Compatible with *BSD: the result is always a valid
 * NUL-terminated string that fits in the buffer (unless,
 * of course, the buffer size is zero). It does not pad
 * out the result like strncpy() does.
 */
size_t strlcpy(char *dest, const char *src, size_t size)
{
 size_t ret = strlen(src);

 if (size) {
  size_t len = (ret >= size) ? size - 1 : ret;
  memcpy(dest, src, len);
  dest[len] = '\0';
 }
 return ret;
}

/**
 * strlcat - Append a length-limited, %NUL-terminated string to another
 * @dest: The string to be appended to
 * @src: The string to append to it
 * @count: The size of the destination buffer.
 */
size_t strlcat(char *dest, const char *src, size_t count)
{
 size_t dsize = strlen(dest);
 size_t len = strlen(src);
 size_t res = dsize + len;

 /* This would be a bug */
 if(dsize >= count) return 0;

 dest += dsize;
 count -= dsize;
 if (len >= count)
  len = count-1;
 memcpy(dest, src, len);
 dest[len] = 0;
 return res;
}

// This function does block but should complete quickly

int read_a2d(char channel, int *val, char *valstr)
{
 int fd, ret;
 char buf[5];

 fd = open("/dev/lpc313x_adc", O_RDWR);
 if(fd < 0) {
  flukelog("ERROR: %s failed opening lpc313x_adc: %s\n",__FUNCTION__ , strerror(errno));
  return(-1);
 }

 // set channel
 ret = write(fd, &channel, 1);
 if(ret < 0) {
  flukelog("ERROR: %s failed writing to lpc313x_adc: %s\n",__FUNCTION__ , strerror(errno));
  close(fd);
  return(-1);
 }
 else if(ret != 1) {
  flukelog("ERROR: %s failed writing to lpc313x_adc: incomplete write\n",__FUNCTION__ );
  close(fd);
  return(-1);
 }

 ret = read(fd, buf, 4);
 if(ret < 0) {
  flukelog("ERROR: %s failed reading from lpc313x_adc: %s\n",__FUNCTION__ , strerror(errno));
  close(fd);
  return(-1);
 }
 else if(ret != 4) {
  flukelog("ERROR: %s failed reading from lpc313x_adc: incomplete read\n",__FUNCTION__ );
  close(fd);
  return(-1);
 }

 close(fd);
 buf[3] = '\0';

 if(val) *val = strtoul(buf, NULL, 16);
 if(valstr) memcpy(valstr, buf, 4);

 return(0);
}

// This function does block but should complete quickly

int set_pwm(int val)
{
 int fd, ret;
 char buf[3];

 fd = open("/dev/lpc313x_pwm", O_WRONLY);
 if(fd < 0) {
  flukelog("ERROR: %s failed opening lpc313x_pwm: %s\n",__FUNCTION__ , strerror(errno));
  return(-1);
 }

 buf[0] = val & 0xFF;            // low byte of 12-bit value
 buf[1] = (val >> 8) & 0x0F;     // high 4 bits of 12-bit value

 // set channel
 ret = write(fd, buf, 2);
 if(ret < 0) {
  flukelog("ERROR: %s failed writing to lpc313x_pwm: %s\n",__FUNCTION__ , strerror(errno));
  close(fd);
  return(-1);
 }
 else if(ret != 2) {
  flukelog("ERROR: %s failed writing to lpc313x_pwm: incomplete write\n",__FUNCTION__ );
  close(fd);
  return(-1);
 }

 close(fd);

 return(0);
}

void udelay(int microsec_delay)
{
 struct timeval now;
 unsigned int timeout_sec, timeout_usec;

 gettimeofday(&now, NULL);

 timeout_sec = now.tv_sec;
 timeout_usec = now.tv_usec + microsec_delay;
 if(timeout_usec >= 1000000) {
  timeout_sec++;
  timeout_usec -= 1000000;
 }

 do {
  gettimeofday(&now, NULL);
 } while (now.tv_sec <= timeout_sec && now.tv_usec <= timeout_usec);
}

static unsigned char crc8table[256] = {
  0x00, 0x07, 0x0E, 0x09, 0x1C, 0x1B, 0x12, 0x15,
  0x38, 0x3F, 0x36, 0x31, 0x24, 0x23, 0x2A, 0x2D,
  0x70, 0x77, 0x7E, 0x79, 0x6C, 0x6B, 0x62, 0x65,
  0x48, 0x4F, 0x46, 0x41, 0x54, 0x53, 0x5A, 0x5D,
  0xE0, 0xE7, 0xEE, 0xE9, 0xFC, 0xFB, 0xF2, 0xF5,
  0xD8, 0xDF, 0xD6, 0xD1, 0xC4, 0xC3, 0xCA, 0xCD,
  0x90, 0x97, 0x9E, 0x99, 0x8C, 0x8B, 0x82, 0x85,
  0xA8, 0xAF, 0xA6, 0xA1, 0xB4, 0xB3, 0xBA, 0xBD,
  0xC7, 0xC0, 0xC9, 0xCE, 0xDB, 0xDC, 0xD5, 0xD2,
  0xFF, 0xF8, 0xF1, 0xF6, 0xE3, 0xE4, 0xED, 0xEA,
  0xB7, 0xB0, 0xB9, 0xBE, 0xAB, 0xAC, 0xA5, 0xA2,
  0x8F, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9D, 0x9A,
  0x27, 0x20, 0x29, 0x2E, 0x3B, 0x3C, 0x35, 0x32,
  0x1F, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0D, 0x0A,
  0x57, 0x50, 0x59, 0x5E, 0x4B, 0x4C, 0x45, 0x42,
  0x6F, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7D, 0x7A,
  0x89, 0x8E, 0x87, 0x80, 0x95, 0x92, 0x9B, 0x9C,
  0xB1, 0xB6, 0xBF, 0xB8, 0xAD, 0xAA, 0xA3, 0xA4,
  0xF9, 0xFE, 0xF7, 0xF0, 0xE5, 0xE2, 0xEB, 0xEC,
  0xC1, 0xC6, 0xCF, 0xC8, 0xDD, 0xDA, 0xD3, 0xD4,
  0x69, 0x6E, 0x67, 0x60, 0x75, 0x72, 0x7B, 0x7C,
  0x51, 0x56, 0x5F, 0x58, 0x4D, 0x4A, 0x43, 0x44,
  0x19, 0x1E, 0x17, 0x10, 0x05, 0x02, 0x0B, 0x0C,
  0x21, 0x26, 0x2F, 0x28, 0x3D, 0x3A, 0x33, 0x34,
  0x4E, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5C, 0x5B,
  0x76, 0x71, 0x78, 0x7F, 0x6A, 0x6D, 0x64, 0x63,
  0x3E, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2C, 0x2B,
  0x06, 0x01, 0x08, 0x0F, 0x1A, 0x1D, 0x14, 0x13,
  0xAE, 0xA9, 0xA0, 0xA7, 0xB2, 0xB5, 0xBC, 0xBB,
  0x96, 0x91, 0x98, 0x9F, 0x8A, 0x8D, 0x84, 0x83,
  0xDE, 0xD9, 0xD0, 0xD7, 0xC2, 0xC5, 0xCC, 0xCB,
  0xE6, 0xE1, 0xE8, 0xEF, 0xFA, 0xFD, 0xF4, 0xF3
};

unsigned char crc8calc(unsigned char *buf, unsigned int len)
{
 unsigned char crc = 0;

 while(len--) crc = crc8table[crc ^ *buf++];

 return(crc);
}

int flashdata_write(char *buf, int offset, int len)
{
 FILE *fp_data;
 int ret;

 fp_data = fopen(NONFSDATADEVICE, "wb");
 if(!fp_data) {
  flukelog("ERROR: %s error(%s) opening non-fs data device\n", __FUNCTION__, strerror(errno));
  return(-1);
 }

 ret = fseek(fp_data, NONFSDATA_LEGACYFLASH_OFFSET + offset, SEEK_SET);
 if(ret) {
  flukelog("ERROR: %s error(%s) seeking offset on non-fs data device\n", __FUNCTION__, strerror(errno));
  fclose(fp_data);
  return(-1);
 }

 ret = fwrite(buf, 1, len, fp_data);
 if(ret != len) {
  flukelog("ERROR: %s error(%s) writing to non-fs data device\n", __FUNCTION__, strerror(errno));
  fclose(fp_data);
  return(-1);
 }

 fclose(fp_data);

 return(0);
}

int flashdata_read(char *buf, int offset, int len)
{
 FILE *fp_data;
 int ret;

 fp_data = fopen(NONFSDATADEVICE, "rb");
 if(!fp_data) {
  flukelog("ERROR: %s error(%s) opening non-fs data device\n", __FUNCTION__, strerror(errno));
  return(-1);
 }

 ret = fseek(fp_data, NONFSDATA_LEGACYFLASH_OFFSET + offset, SEEK_SET);
 if(ret) {
  flukelog("ERROR: %s error(%s) seeking offset on non-fs data device\n", __FUNCTION__, strerror(errno));
  fclose(fp_data);
  return(-1);
 }

 ret = fread(buf, 1, len, fp_data);
 if(ret != len) {
  flukelog("ERROR: %s error(%s) reading from non-fs data device\n", __FUNCTION__, strerror(errno));
  fclose(fp_data);
  return(-1);
 }

 fclose(fp_data);

 return(0);
}
