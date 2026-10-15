#include "global.h"

void sub_08031954(u8, u8, u8);
extern u8 gUnk_02023490[];
void sub_080333E4(void)
{
  int new_var3[2];
 new_var3[0] = gUnk_02023490[0x264]; do { } while (0);
  new_var3[1] = 0;
  gUnk_02023490[(long) 0x264] = new_var3[0];
  gUnk_02023490[0x264] = gUnk_02023490[0x264] | 2;
  sub_08031954(0x2b, new_var3[1], new_var3[1]);
}
