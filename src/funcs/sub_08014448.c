#include "global.h"


extern u8 gUnk_02020C50[];
u16 sub_08014448(u8 idx)
{
  u8 *p = gUnk_02020C50;
  int new_var;
  s32 i = ((*((s8 *) (p + 4))) + idx) - 2;
  if (i < 0)
  {
    return 0;
  }
  if (i > 0x27)
  {
    if (i)
    {
      return 0;
    }
    else
    {
      return 0;
    }
  }
  new_var = 0xA;
  return ((u16 *) (p + new_var))[i];
}
