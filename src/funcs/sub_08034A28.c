#include "global.h"

extern u8 gUnk_08D510FE[];
s32 sub_08034A28(u8 a, u8 b)
{
  if (!gUnk_08D510FE)
  {
  }
  return *((s16 *) ((gUnk_08D510FE + (a * 2)) + (b * 10)));
}
