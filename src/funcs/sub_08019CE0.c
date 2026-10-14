#include "global.h"


extern u16 gUnk_08D419CC[];
u32 sub_08019CE0(u16 a)
{
  u8 i;
  for (i = 0; i < 4; i++)
  {
    if (a == gUnk_08D419CC[i])
    {
      break;
    }
  }

  return i;
}
