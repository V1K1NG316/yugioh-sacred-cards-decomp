#include "global.h"

u8  sub_08034260(u8 *, u8 *);

extern u8 gUnk_08D4F43C[];
extern u8 gUnk_08D5108C[];
extern u8 gUnk_08D51094[];

u8 sub_08034218(u16 index)
{
    if (sub_08034260(gUnk_08D5108C, gUnk_08D4F43C + index * 8) == 10)
        return 0;

    if (sub_08034260(gUnk_08D51094, gUnk_08D4F43C + index * 8) == 10)
        return 1;

    return 2;
}
