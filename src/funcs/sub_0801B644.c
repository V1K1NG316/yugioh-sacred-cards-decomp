#include "global.h"


void sub_0801FD5C(void);
void sub_0801C2A4(void);
extern u8 gUnk_02023040[];
extern u8 gUnk_020215A4[];
extern u8 gUnk_080C82F8[];
void sub_0801B644(u8 a)
{
  int new_var;
  u8 *p;
  *((u32 *) gUnk_02023040) = (u32) gUnk_020215A4;
  new_var = 0x384;
  *((u16 *) (gUnk_02023040 + 8)) = new_var;
  *((u8 *) (gUnk_02023040 + 0xA)) = gUnk_080C82F8[a];
  sub_0801FD5C();
  sub_0801C2A4();
  p = gUnk_020215A4;
  *((u16 *) (p + 0x70E)) = 0x80;
}
