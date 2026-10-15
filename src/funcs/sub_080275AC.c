#include "global.h"

s32 sub_08034A5C(u8, u8);
extern u8 gUnk_02023438[];
extern volatile char gUnk_08D4C674[];
u32 sub_080275AC(u8 a)
{
  u32 v = sub_08034A5C(gUnk_02023438[0], gUnk_02023438[1]);
  int new_var;
  new_var = gUnk_08D4C674[a] + v;
  return (u8) new_var;
}
