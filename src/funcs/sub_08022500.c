#include "global.h"

extern u32 gUnk_08D4BBD8[];

void sub_080225C4(u32, u8 *, u8 *);

void sub_08022500(void)
{
  u8 *p = (u8 *)0x02018400;
  u8 *e;
  u32 n;
  u32 i;

  e = (u8 *)gUnk_08D4BBD8[2];
  n = e[1];
  sub_080225C4(n, e, p);
  for (i = 0; i < n; i++)
    p += 8;
  e = (u8 *)gUnk_08D4BBD8[1];
  n = e[1];
  sub_080225C4(n, e, p);
  for (i = 0; i < n; i++)
    p += 8;
  e = (u8 *)gUnk_08D4BBD8[5];
  n = e[1];
  sub_080225C4(n, e, p);
  *((u32 *)p) |= 0x400;
}
