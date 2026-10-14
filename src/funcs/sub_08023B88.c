#include "global.h"


extern u8 gUnk_02023140[];
u32 sub_0802355C(void);
u32 sub_08023B88(void)
{
  u32 new_var;
  gUnk_02023140[0x18] = 0x10;
 do { new_var = sub_0802355C(); return new_var; } while (0);
}
