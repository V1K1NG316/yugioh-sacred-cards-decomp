#include "global.h"

void sub_0802510C(u8 *);
void sub_080253F4(u8 *);
void sub_080254CC(u8 *);
void sub_0802568C(u8 *);
void sub_0802572C(u8 *);
void sub_08003BC4(void);
void sub_08024E50(void);

void sub_08025098(u8 *p)
{
  while (*((u8 *)(*((u32 *)(p + 0xC)) + *((u32 *)p))) != 0) {
    switch (p[8]) {
    case 0:
      sub_0802510C(p);
      break;
    case 1:
      sub_080253F4(p);
      break;
    case 2:
      sub_080254CC(p);
      break;
    case 3:
      break;
    case 4:
      sub_0802568C(p);
      break;
    case 5:
      sub_0802572C(p);
      break;
    }
    sub_08003BC4();
    sub_08024E50();
  }
}
