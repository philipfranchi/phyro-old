#include "phyro.h"

int main(void){
	int i;
	init();
	int ret = get_battery();
	printf("Result %d\n",ret);
	FILE *fp = fopen("/home/fluke2/server/pic.txt", "ab+");
	get_image();
	fwrite(camctrl.image, sizeof(char), RAWIMAGESIZE * 3 + 20, fp);
}