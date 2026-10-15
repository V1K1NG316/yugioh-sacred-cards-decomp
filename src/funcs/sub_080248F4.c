#include "global.h"

extern u8 gUnk_02023160[];

void sub_08003BC4(void);
void sub_080285D8(void);
void sub_08024980(u32);
void sub_08024A14(void);
void sub_0802595C(void);
void sub_08024B34(void);
void sub_08035AA0(void);
void sub_08024598(void);
void sub_08024E00(void);

void sub_080248F4(void)
{
  sub_08003BC4();
  sub_080285D8();
  sub_08024980(gUnk_02023160[0xF0]);
  sub_08024A14();
  sub_0802595C();
  sub_08024B34();
  sub_08035AA0();
  sub_08024598();
  sub_08003BC4();
  sub_08024E00();
  *((u16 *)0x04000000) = 0x3600;
  *((u16 *)0x04000050) = 0xD4;
  *((u16 *)0x04000054) = 0xA;
}
