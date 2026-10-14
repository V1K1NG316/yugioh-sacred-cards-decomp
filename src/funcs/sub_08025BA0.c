#include "global.h"

void sub_08004284(u8, u8 *);
void sub_080042A8(u8, u8 *);
void sub_080041C8(u8, u8 *);
void sub_0800423C(u8, u8 *);

extern u8 gUnk_02020B00[];
extern u8 gUnk_02008980[];
extern u8 gUnk_020000C0[];

void sub_08025BA0(void)
{
    u8 *p;
    u8 *q;

    sub_08004284(gUnk_02020B00[0x17], p = gUnk_02008980);
    sub_080042A8(gUnk_02020B00[0x17], q = gUnk_020000C0);
    sub_080041C8(gUnk_02020B00[0x16], p -= 0x80);
    sub_0800423C(gUnk_02020B00[0x16], q -= 0x20);
}
