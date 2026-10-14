#include "global.h"

extern u8 *gUnk_08D36418;
extern u8 gUnk_02020D90[];

void sub_08018650(void);
void sub_08018608(void);

void sub_08018960(void)
{
    u8 i;

    for (i = 0; i <= 7; i++)
        gUnk_02020D90[i] = 0;
    gUnk_08D36418[0] = 0;
    gUnk_08D36418[1] = 1;
    sub_08018650();
    sub_08018608();
}
