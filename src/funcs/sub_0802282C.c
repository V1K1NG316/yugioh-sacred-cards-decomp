#include "global.h"


extern u8 gUnk_02000400[];
void sub_0802282C(void)
{
  int new_var3;
  u16 *new_var;
  u8 *new_var2;
  u8 *p = gUnk_02000400;
  unsigned long z;
  new_var3 = 0xF31A;
  new_var2 = p + 0xF2DA;
  z = 0;
  *((u16 *) new_var2) = 1;
  new_var = (u16 *) (p + new_var3);
  *new_var = z;
}
