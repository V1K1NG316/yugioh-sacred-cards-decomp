#include "global.h"

u32 sub_080311B0(u8, u8);
u32 sub_0803181C(u16);

extern u8 gUnk_02023490[];
extern u8 gUnk_02020D84[];

void sub_08031A0C(void)
{
    u8 v = gUnk_02023490[0x20];
    u32 r;

    if (v == 1) {
        r = sub_0803181C(sub_080311B0(gUnk_02023490[0xC], gUnk_02023490[0xE]));
        if (r == 0) {
            gUnk_02020D84[0] = r;
            gUnk_02020D84[1] = r;
            gUnk_02020D84[2] = v;
        }
    }
}
