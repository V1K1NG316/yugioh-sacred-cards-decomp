#include "global.h"

extern u16 gUnk_08D36678[];

u32 sub_08018D68(u16 a)
{
    u8 i;

    for (i = 0; gUnk_08D36678[i] != 0; i++) {
        if (gUnk_08D36678[i] == a)
            return 1;
    }
    return 0;
}
