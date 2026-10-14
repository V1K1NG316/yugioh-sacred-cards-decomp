#include "global.h"


extern volatile unsigned char gUnk_02020B00[];
extern u8 gUnk_08D4BD60[];
void sub_08006BE4(u16);
s8 sub_08023C64(u16 a)
{
  sub_08006BE4(a);
  return gUnk_08D4BD60[gUnk_02020B00[0x1A]];
}
