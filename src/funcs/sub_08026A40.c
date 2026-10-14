#include "global.h"


s8 sub_08026A40(u32 *p)
{
  u8 i;
  for (i = 5; i > 0; i--)
  {
    u32 q;
    if ((*((u16 *) (*(p--)))) == 0)
    {
      return i - 1;
    }
  }

  return 0;
}
