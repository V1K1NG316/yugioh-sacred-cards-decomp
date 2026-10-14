#include "global.h"


extern volatile short gUnk_02020D30[];
void sub_08017EFC(u32 *);
struct Unk17ED4
{
  u32 bottom : 16;
  u32 top : 16;
};
void sub_08017ED4(void)
{
  struct Unk17ED4 s;
  s.bottom = gUnk_02020D30[0x16];
  sub_08017EFC((u32 *) (&s));
}
