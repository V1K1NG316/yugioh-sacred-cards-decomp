#include "global.h"


void sub_080220F8(void);
void sub_08022168(void)
{
  int new_var;
  sub_080220F8();
  new_var = 0x0201FCB0;
  do
  {
 do { } while (0);
  }
  while ((0x40 & (*((volatile u16 *) new_var))) == 0);
}
