#include "global.h"

u32 sub_08031534(s32, s32);
u32 sub_08031564(s32, s32);
u32 sub_0803158C(s32, s32);
u32 sub_080315B4(s32, s32);

extern u8 gUnk_02023490[];

u32 sub_080315E4(u8 x, u8 y, u8 dir)
{
    u8 i = 1;
    u8 *base = gUnk_02023490;
    u8 hit;

    for (; i <= 0x0E; i++) {
        switch (dir) {
        case 0:
            hit = sub_08031534((s32)y - *(s16 *)(base + i * 0x20 + 0xE),
                               (s32)x - *(s16 *)(base + i * 0x20 + 0xC));
            break;
        case 1:
            hit = sub_08031564((s32)y - *(s16 *)(base + i * 0x20 + 0xE),
                               (s32)x - *(s16 *)(base + i * 0x20 + 0xC));
            break;
        case 2:
            hit = sub_0803158C((s32)y - *(s16 *)(base + i * 0x20 + 0xE),
                               (s32)x - *(s16 *)(base + i * 0x20 + 0xC));
            break;
        case 3:
            hit = sub_080315B4((s32)y - *(s16 *)(base + i * 0x20 + 0xE),
                               (s32)x - *(s16 *)(base + i * 0x20 + 0xC));
            break;
        }
        if (hit != 0)
            return (s32)(i << 24) >> 24;
    }
    return -1;
}
