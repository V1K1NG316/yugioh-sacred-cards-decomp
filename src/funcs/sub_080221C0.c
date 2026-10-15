#include "global.h"

void sub_080223EC(void);
void sub_080224B8(void);
void sub_0802287C(void);
void sub_08003B58(void *);
void sub_08021E50(u32);
void sub_08003BC4(void);
void sub_080227B8(void);
void sub_08022864(void);
void sub_0802284C(void);
void sub_0803458C(void);
u32 sub_080223AC(void);
void sub_08021F10(u32);
void sub_08022424(void);

s32 sub_080221C0(void)
{
  sub_080223EC();
  sub_080224B8();
  sub_0802287C();
  sub_08003B58((void *)sub_08022864);
  sub_08021E50(1);
  sub_08003BC4();
  while (sub_0803458C(), ((u16)sub_080223AC()) != 1) {
    sub_080227B8();
    sub_08003B58((void *)sub_0802284C);
    sub_08003BC4();
  }
  sub_08021F10(1);
  sub_080227B8();
  sub_08003B58((void *)sub_0802284C);
  sub_08003BC4();
  sub_08021E50(0xD2);
  sub_08022424();
  return 0;
}
