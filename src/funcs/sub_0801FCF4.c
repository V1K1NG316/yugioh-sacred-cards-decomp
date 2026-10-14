#include "global.h"


extern u32 *gUnk_08D41A4C;
void sub_0801FCF4(u32 *out)
{
  u32 *base = gUnk_08D41A4C;
  u32 new_var;
  int new_var2;
  u32 n = base[0x20];
  if (n != 0)
  {
    n--;
    base[0x20] = n;
    new_var2 = (u32) base;
    new_var2 = (n * 4) + new_var2;
    new_var = *((u32 *) new_var2);
    *out = new_var;
  }
}
