#include "global.h"

extern u16 gUnk_0201FCAC[];

void sub_08018DA8(void);

u32 sub_080223AC(void)
{
    u32 r = 0;
    u16 mask;
    u8 i;
    u16 keys;

    sub_08018DA8();
    mask = 1;
    keys = gUnk_0201FCAC[0];
    if ((keys & 0x3FF) != 0) {
        for (i = 0; i < 10; i++) {
            if ((mask & keys) != 0)
                r = mask;
            mask <<= 1;
        }
    }
    return r;
}
