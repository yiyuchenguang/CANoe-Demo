// PrintDeviceInfo.cpp : 定义控制台应用程序的入口点。
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <Windows.h>

unsigned char crc8(unsigned char value)
{
    unsigned char i, crc;
    crc = value^0x00;
    /* 数据往左移了8位，需要计算8次 */
    for (i = 8; i > 0; --i)
    {
        if (crc & 0x80)  /* 判断最高位是否为1 */
        {
            crc = (crc << 1) ^ 0x1d;
        }
        else
        {
            /* 最高位为0时，不需要异或，整体数据往左移一位 */
            crc = (crc << 1);
        }
    }
    crc = crc ^ 0x00;
    return crc;
}

int  main(int  argc, char* argv[])
{

    unsigned char retCRC;
    unsigned char testValue = 3;
    unsigned char Crc8Table[256];
    
    for(int i =0 ;i< 256 ;i++)
    {
        Crc8Table[i] = crc8(i);

        printf("%5x  ", Crc8Table[i]); 
        if ((i+1) % 12 == 0)
            printf("\n");
    }
	getchar();
	return  0;
}