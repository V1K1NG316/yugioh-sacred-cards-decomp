#include "global.h"

u8 sub_08021EB0(u32);
void sub_080379E0(u32);
void sub_080379B4(u32);
void sub_080381CC(u32);

void sub_08021E50(u16 a)
{
  u16 v = a;

  switch ((u8)sub_08021EB0(v) - 1) {
  case 0:
    sub_080379E0(v);
    break;
  case 1:
  case 2:
    sub_080379B4(v);
    break;
  case 3:
    sub_080381CC(0x020249F0);
    break;
  case 4:
    sub_080379E0(v);
    break;
  }
}
