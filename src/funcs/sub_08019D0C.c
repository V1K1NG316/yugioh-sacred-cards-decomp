#include "global.h"


extern u8 gUnk_02020DA8[];
void sub_08019D0C(u8 a)
{
  u8 v = a;
  ;
  gUnk_02020DA8[0] = (v & 0x3F) | gUnk_02020DA8[0];
}
