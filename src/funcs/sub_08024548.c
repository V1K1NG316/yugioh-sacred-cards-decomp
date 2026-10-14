#include "global.h"


extern volatile unsigned char *gUnk_02023260[];
void sub_08024548(u8 a)
{
  int new_var;
  u8 *p;
  new_var = 2;
  gUnk_02023260[a][new_var] |= 8;
}
