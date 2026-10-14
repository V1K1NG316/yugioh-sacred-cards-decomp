#include "global.h"


extern u8 gUnk_080C868C[];
extern volatile char gUnk_020214D0[];
u8 sub_0801C0F0(u8 a)
{
  return gUnk_080C868C[a + (5 * gUnk_020214D0[0x7E8])];
}
