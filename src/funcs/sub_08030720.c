#include "global.h"


extern u16 gUnk_0201FCAC[];
extern u16 gUnk_0201FCA8[];
extern u16 gUnk_0201FCA4[];

u32 sub_08030720(void)
{
    if (gUnk_0201FCAC[0] & 1)
        return 6;
    if (gUnk_0201FCAC[0] & 0x100)
        return 5;
    if (gUnk_0201FCA8[0] & 2) {
        if (gUnk_0201FCA8[0] & 0x40)
            return 0xB;
        if (gUnk_0201FCA8[0] & 0x80)
            return 0xC;
        if (gUnk_0201FCA8[0] & 0x20)
            return 0xD;
        if (gUnk_0201FCA8[0] & 0x10)
            return 0xE;
    }
    if (gUnk_0201FCA8[0] & 0x40)
        return 1;
    if (gUnk_0201FCA8[0] & 0x80)
        return 2;
    if (gUnk_0201FCA8[0] & 0x20)
        return 3;
    if (gUnk_0201FCA8[0] & 0x10)
        return 4;
    if (gUnk_0201FCA4[0] & 4)
        return 7;
    if (gUnk_0201FCA4[0] & 8)
        return 7;
    if (gUnk_0201FCA4[0] & 0x200)
        return 7;
    return 0;
}
