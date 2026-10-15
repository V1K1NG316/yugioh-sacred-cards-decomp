#include "global.h"

extern u8 gUnk_08D4BD30[];
extern u8 gUnk_08D4BD3C[];

u32 sub_08023A04(u32 a, u32 b)
{
  u8 x = (u8)a;
  u8 y = (u8)b;

  if (x == 0xB)
    return 1;
  if (y == 0xB)
    return 1;
  if (gUnk_08D4BD30[x] == y)
    return 0;
  if (gUnk_08D4BD3C[x] == y)
    return 2;
  return 1;
}
