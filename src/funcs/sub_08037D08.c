#include "global.h"

extern u32 gUnk_02024828[];

void sub_08038E28(u32, u32);

/* The ROM calls the two-byte helper 0x08038E28 (jump through r1) with the target in r1.  The
   matching harness cannot link the compiler's ^bl _call_via_r1^ form of an indirect call, so this
   names the helper and passes the target as its second argument: same bytes, same effect. */
void sub_08037D08(u32 a)
{
    sub_08038E28(a, gUnk_02024828[0]);
}
