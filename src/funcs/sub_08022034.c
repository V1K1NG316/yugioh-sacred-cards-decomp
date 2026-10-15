#include "global.h"

void sub_08022034(void)
{
  *((volatile u16 *)0x04000208) = 0;
  *((volatile u16 *)0x04000200) &= 0xFFBF;
  *((volatile u16 *)0x04000208) = 1;
}
