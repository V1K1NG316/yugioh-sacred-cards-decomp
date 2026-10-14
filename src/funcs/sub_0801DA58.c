#include "global.h"

void sub_08004284(u8, u8 *);
void sub_080042A8(u8, u8 *);
void sub_080041C8(u8, u8 *);
void sub_0800423C(u8, u8 *);

extern u8 gUnk_02020B00[];
extern u8 gUnk_0200F9A0[];
extern u8 gUnk_02000180[];

void sub_0801DA58(void)
{
    u8 *p;
    u8 *q;

    sub_08004284(gUnk_02020B00[0x17], p = gUnk_0200F9A0);
    sub_080042A8(gUnk_02020B00[0x17], q = gUnk_02000180);
    sub_080041C8(gUnk_02020B00[0x16], p -= 0x80);
    sub_0800423C(gUnk_02020B00[0x16], q -= 0x20);
}
