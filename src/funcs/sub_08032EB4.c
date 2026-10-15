#include "global.h"

extern u8 gUnk_02023490[];

void sub_08021E50(u16);
void sub_08021ECC(void);
void sub_08032A08(u8, u16, u16, u8 *);
void sub_08032944(u8, u8, u8, u8, u8 *);
void sub_08035AE4(u16);

void sub_08032EB4(u8 *ctx)
{
    gUnk_02023490[0x2A] = 3;
    sub_08021E50(0x5E);
    sub_08032A08(1, 0x4A, 0x28, ctx);
    sub_08035AE4(0x60);
    sub_08021E50(0xD6);
    sub_08032944(1, 3, 0x10, 0, ctx);
    sub_08021ECC();
    sub_08032944(1, 1, 0, 0, ctx);
    sub_08035AE4(0x60);

    gUnk_02023490[0x0A] = 3;
    sub_08021E50(0x5E);
    sub_08032A08(0, 0x4A, 0x28, ctx);
    sub_08035AE4(0x60);
    sub_08021E50(0xD6);
    sub_08032944(0, 3, 8, 0, ctx);
    sub_08021ECC();
    sub_08032944(0, 1, 0, 0, ctx);
    sub_08035AE4(0x60);
}
