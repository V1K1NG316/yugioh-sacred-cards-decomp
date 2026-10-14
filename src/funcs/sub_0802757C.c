#include "global.h"

s32 sub_08034A28(u8, u8);

extern u8 gUnk_02023438[];
extern s8 gUnk_08D4C670[];

u32 sub_0802757C(u8 a)
{
    u32 v = sub_08034A28(gUnk_02023438[0], gUnk_02023438[1]);

    return (u16)(gUnk_08D4C670[a] + v);
}
