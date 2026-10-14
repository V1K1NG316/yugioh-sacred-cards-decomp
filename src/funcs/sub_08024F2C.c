#include "global.h"

typedef struct
{
    u32 unk0;
    u32 unk4;
    u8 unk8;
    u32 unkC;
    u16 unk10;
    u16 unk12;
    u16 unk14;
    u16 unk16;
    u16 unk18;
    u16 unk1A;
    u8 unk1C;
} Unk02024F2C;

void sub_08024944(void);
void sub_08024FE8(Unk02024F2C *);
void sub_08025098(Unk02024F2C *);

void sub_08024F2C(u32 a0, u16 a1, u16 a2, u16 a3, u16 a4)
{
    Unk02024F2C s;
    u8 z = 0;

    s.unk0 = 0;
    s.unk4 = 0;
    s.unk8 = 0;
    s.unkC = a0;
    s.unk10 = 0;
    s.unk1C = z;
    s.unk14 = a1;
    s.unk16 = a2;
    s.unk18 = a3;
    s.unk1A = a4;
    sub_08024FE8(&s);
    sub_08025098(&s);
    sub_08024944();
}
