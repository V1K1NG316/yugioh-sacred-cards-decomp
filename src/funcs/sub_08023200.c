/* compiler: agbcc (A37) */
#include "global.h"

extern u8 gUnk_02023120[];
extern u8 gUnk_08D4BD2C[];

void sub_08023200(u8 i)
{
    gUnk_02023120[0x19] |= gUnk_08D4BD2C[i];
}
