#include "global.h"


extern u8 gUnk_02023120[];
void sub_0802355C(void)
{
  u8 v = gUnk_02023120[0x19];
  int new_var;
  if (new_var)
  {
    new_var = 2;
    new_var = v | new_var;
    gUnk_02023120[0x19] = new_var;
  }
  else
  {
    new_var = 2;
    new_var = v | new_var;
    gUnk_02023120[0x19] = new_var;
  }
}
