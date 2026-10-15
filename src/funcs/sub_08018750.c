#include "global.h"

extern u8 *gUnk_08D36418;

void sub_08018750(void)
{
    switch (gUnk_08D36418[1]) {
    case 0:
        gUnk_08D36418[1] = 7;
        break;
    case 1:
        gUnk_08D36418[1] = 0;
        break;
    case 2:
        gUnk_08D36418[1] = 10;
        break;
    case 3:
        gUnk_08D36418[1] = 10;
        break;
    case 4:
        gUnk_08D36418[1] = 1;
        break;
    case 5:
        gUnk_08D36418[1] = 2;
        break;
    case 6:
        gUnk_08D36418[1] = 3;
        break;
    case 7:
        gUnk_08D36418[1] = 4;
        break;
    case 8:
        gUnk_08D36418[1] = 5;
        break;
    case 9:
        gUnk_08D36418[1] = 6;
        break;
    case 10:
        gUnk_08D36418[1] = 8;
        break;
    }
}
