#include "global.h"

extern u16 gUnk_02000400[];

void sub_080157B8(u8 a)
{
    gUnk_02000400[0x5C1C] = a * 4 + 0x5002;
    gUnk_02000400[0x5C1D] = a * 4 + 0x5003;
    gUnk_02000400[0x5C3C] = a * 4 + 0x5004;
    gUnk_02000400[0x5C3D] = a * 4 + 0x5005;
}
