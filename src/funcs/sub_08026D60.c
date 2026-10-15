#include "global.h"

void sub_08006BE4(u16);
extern u8 gUnk_02020B00[];
u32 sub_08026D60(u16 *p)
{
  u32 r = 0;
  if ((*p) != 0)
  {
    sub_08006BE4(*p);
    if (gUnk_02020B00[0x1B] != 0)
    {
      if (((*(((u8 *) p) + 4)) & 1) == 0)
      {
        r = 0;
        if (((*(((u8 *) p) + 4)) & 0x10) == r)
        {
          r = 1;
        }
      }
    }
  }
  return r;
}
