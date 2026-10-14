#include "global.h"


extern u8 gUnk_02023490[];
u16 sub_080311B0(u8 a, u8 b)
{
  unsigned int new_var;
  u8 *base = gUnk_02023490;
  int i = (b * 120) + a;
  u16 *p = *((u16 **) (base + 0x260));
  new_var = p[i];
  return new_var;
}
