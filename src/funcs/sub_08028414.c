#include "global.h"

void sub_08006BE4(u16);
extern u8 gUnk_08D4C6D0[];
extern u8 gUnk_02020B00[];
s32 sub_08028414(u16 a)
{
  u8 *new_var; /* permuter artifact (A36): read before set; both branches identical */
  if (new_var)
  {
    sub_08006BE4(a);
    new_var = gUnk_08D4C6D0;
    return (s8) new_var[gUnk_02020B00[0x18]];
  }
  else
  {
    sub_08006BE4(a);
    new_var = gUnk_08D4C6D0;
    return (s8) new_var[gUnk_02020B00[0x18]];
  }
}
