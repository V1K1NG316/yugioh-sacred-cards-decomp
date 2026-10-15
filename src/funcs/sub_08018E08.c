#include "global.h"

extern u16 gUnk_0201FCAC[];
extern u16 gUnk_0201FCA8[];
extern u16 gUnk_02020D9C[];
extern u8 gUnk_02020D98[];

void sub_08018E08(void)
{
    u16 keys = gUnk_0201FCAC[0];
    u8 v;

    if ((keys & 0x3FF) != 0) {
        gUnk_02020D9C[0] = keys;
        gUnk_02020D98[0] = 10;
    } else {
        v = gUnk_02020D98[0];
        if (v != 0) {
            gUnk_02020D9C[0] = 0;
            gUnk_02020D98[0] = v - 1;
        } else {
            gUnk_02020D9C[0] = gUnk_0201FCA8[0];
            gUnk_02020D98[0] = 3;
        }
    }
}
