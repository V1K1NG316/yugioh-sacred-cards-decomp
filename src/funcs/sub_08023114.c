#include "global.h"

u32 sub_08023114(u16 a)
{
  u32 r = 0;

  switch (a - 0x247) {
  case 0:
    r = 1;
    break;
  case 1:
    r = 2;
    break;
  case 2:
    r = 4;
    break;
  case 3:
    r = 8;
    break;
  case 4:
    r = 0x10;
    break;
  }
  return r;
}
