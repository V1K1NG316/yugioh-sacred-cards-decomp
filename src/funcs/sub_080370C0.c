#include "global.h"

void sub_080370C0(u8 *p)
{
  u8 *a = *((u8 **) (p + 0x2c));
  u8 *b;
  u8 *c;
  if (a == ((void *) 0))
  {
    return;
  }
  b = *((u8 **) (p + 0x34));
  c = *((u8 **) (p + 0x30));
  if (c != ((void *) 0))
  {
    *((u8 **) (c + 0x34)) = b;
  }
  else
  {
    *((u8 **) (a + 0x20)) = b;
  }
  if (b != ((void *) 0))
  {
    *((u8 **) (b + 0x30)) = c;
  }
  b = (void *) 0;
  *((u8 **) (p + 0x2c)) = b;
}
