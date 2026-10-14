#include "global.h"


extern u8 gUnk_02020B00[];
extern u32 gUnk_08D5109C[];
void sub_08006BE4(u16);
void sub_0803692C(const void *, void *, u32);
void sub_0801DFE4(u8 *dst, u16 a)
{
  int new_var;
  new_var = 0x17;
  dst += 0xC0;
  sub_08006BE4(a);
  if (gUnk_02020B00[new_var] != 0)
  {
    sub_0803692C((const void *) gUnk_08D5109C[gUnk_02020B00[new_var]], dst, 0x20);
  }
}
