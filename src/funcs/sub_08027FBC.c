#include "global.h"

extern u16 gUnk_0201FCAC[];
u32 sub_08027FBC(void)
{
  if (0x100 & gUnk_0201FCAC[0])
  {
    return 0x100;
  }
  if (2 & gUnk_0201FCAC[0])
  {
    return 2;
  }
  return 0;
}
