#include "global.h"


extern u32 gUnk_08D36130[];
void sub_08024F2C(u32, u32, u32, u32, u32);
void sub_08017E74(u8 *s)
{
  u8 new_var;
  new_var = s[8];
  if (s[8] != 0xFF)
  {
    sub_08024F2C(gUnk_08D36130[new_var], ((u16 *) s)[0], ((u16 *) s)[1], ((u16 *) s)[2], 0);
  }
}
