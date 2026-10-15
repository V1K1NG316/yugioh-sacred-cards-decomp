#include "global.h"

void sub_08018E08(void);

extern u16 gUnk_0201FCAC[];
extern u16 gUnk_02020D9C[];

u32 sub_0801843C(void)
{
    u32 res = 0;
    u16 bit;
    u16 keys;
    u8 i;

    sub_08018E08();

    bit = 1;
    keys = gUnk_0201FCAC[0];
    if ((keys & 0x3FF) != 0) {
        i = 0;
        do {
            if (bit & keys)
                res = bit;
            bit <<= 1;
            i++;
        } while (i <= 9);
    }

    bit = 0x10;
    keys = gUnk_02020D9C[0];
    if ((keys & 0x3F0) != 0) {
        i = 0;
        do {
            if (bit & keys)
                res = bit;
            bit <<= 1;
            i++;
        } while (i <= 5);
    }

    return res;
}
