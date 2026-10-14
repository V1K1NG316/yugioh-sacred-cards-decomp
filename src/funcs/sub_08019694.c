#include "global.h"


extern u16 gUnk_0201FCAC;
void sub_08018DA8(void);
u32 sub_08019694(void)
{
  u16 g;
  u16 i = 1;
  u32 r = 0;
  u8 j;
  sub_08018DA8();
  i++;
  i--;
  g = gUnk_0201FCAC;
  if ((g & 0x3FF) != 0)
  {
    for (j = 0; j <= 9; j++)
    {
      if ((i & g) != 0)
      {
        r = i;
      }
      i <<= 1;
    }

  }
  return r;
}
