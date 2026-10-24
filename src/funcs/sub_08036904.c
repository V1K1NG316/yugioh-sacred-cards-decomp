/* compiler: agbcc (A37) */
#include "global.h"

extern u8 gUnk_020237D8[];
extern u8 gUnk_08D5119C[];

void sub_08036904(void)
{
    u8 *c = gUnk_020237D8;

    *c = gUnk_08D5119C[*c];
}
