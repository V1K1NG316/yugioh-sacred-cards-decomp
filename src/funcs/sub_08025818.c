#include "global.h"

void sub_0802460C(void);
void sub_08003BC4(void);
void sub_08024E18(void);
void sub_08025870(u8);
void sub_080258E8(u8);

extern u8 gUnk_02023384[];
extern u8 gUnk_08D4C2A8[];

void sub_08025818(u8 a, u8 b)
{
    gUnk_02023384[0] = b;
    switch (gUnk_08D4C2A8[b + a * 5]) {
    case 0:
        sub_0802460C();
        sub_08003BC4();
        sub_08024E18();
        break;
    case 1:
        sub_08025870(b);
        break;
    case 2:
        sub_080258E8(b);
        break;
    }
}
