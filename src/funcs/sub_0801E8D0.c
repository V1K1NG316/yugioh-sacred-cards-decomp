#include "global.h"

extern u8 gUnk_020214D0[];

void sub_0801CE4C(u8);
void sub_0801E3D0(void);
void sub_0801E5C8(void);
void sub_0801C6D0(void);
void sub_0801E968(void);
void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_0801E94C(void);

void sub_0801E8D0(void)
{
    sub_0801CE4C(gUnk_020214D0[0x7E9]);
    sub_0801E3D0();
    sub_0801E5C8();
    sub_0801C6D0();
    sub_08003B58((void *)sub_0801E968);
    sub_08003BC4();
    sub_0801E94C();
}
