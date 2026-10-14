#include "global.h"

void sub_08031AA8(u8 *dst, u32 *src)
{
    *(u32 *)(dst + 0x10) = src[0];
    *(u32 *)(dst + 0x14) = src[1];
    *(u32 *)(dst + 0x18) = src[2];
}
