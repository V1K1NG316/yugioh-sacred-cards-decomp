#include "global.h"


extern u8 gUnk_02023140[];
volatile long long sub_0802354C(void);
u32 sub_08023C20(void)
{
  gUnk_02023140[0x18] = 0x11;
  return sub_0802354C();
}
