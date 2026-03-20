#include "conv2d.h"

#define CSR_MVUPRECISION_WPREC ( 0)
#define CSR_MVUPRECISION_IPREC ( 6)
#define CSR_MVUPRECISION_OPREC (12)

#ifdef STREAM
void conv3x3_64_stream(int hart_id, int iofst, int oofst, int wofst, int hart_loop_length, int* final_iaddr, int* final_oaddr, int* final_waddr){
    int input_addr  = CALC_MEM_OFFSET(64, hart_id, iofst);
    int output_addr = CALC_MEM_OFFSET(2 , hart_id, oofst);
    int weight_addr = CALC_MEM_OFFSET(0 , hart_id, wofst);
    SET_CSR(CSR_MVUPRECISION, 
        8  << CSR_MVUPRECISION_WPREC | // set weight precision
        8  << CSR_MVUPRECISION_IPREC | // set input precision
        16 << CSR_MVUPRECISION_OPREC); // set output precision. 27 bits is enough to allow a 3x3 kernel, 64 channels, and 8 bits of precision without overflow i.e. clog2(255*255*3*3*64)
        // but 30 * 30 * 27 bits is actually more than the available memory (barely) so we'll just take 16 MSB's for now

    // Jump schedule for the weights is just to repeatedly iterate 0,1,2,3,4,5,6,7,8 and repeat
    // the idea is to have a 3x3 kernel at those addresses
    // we've multiplied everything by 8 to allow 8 bits of precision
    SET_CSR(CSR_MVUWLENGTH_1,       1-1             );
    SET_CSR(CSR_MVUWLENGTH_2,       1-1             );
    SET_CSR(CSR_MVUWLENGTH_3,     8*8-1             );
    SET_CSR(CSR_MVUWLENGTH_4,       9-1             );
    SET_CSR(CSR_MVUWJUMP_0,        -8*8             );
    SET_CSR(CSR_MVUWJUMP_1,        -8*8             );
    SET_CSR(CSR_MVUWJUMP_2,        -8*8             );
    SET_CSR(CSR_MVUWJUMP_3,        -8*8             );
    SET_CSR(CSR_MVUWJUMP_4,         1*8             );

    SET_CSR(CSR_MVUILENGTH_1, 30-1); // 30 convolutions per row (32-2 because of the image edges)
    SET_CSR(CSR_MVUILENGTH_2, 8*8-1); // iterate over the kernel 64 times to cover all 8x8 zigzag combinations
    SET_CSR(CSR_MVUILENGTH_3, 3-1); // the conv kernel is 3x3
    SET_CSR(CSR_MVUILENGTH_4, 3-1); // the conv kernel is 3x3 (-1 because the AGU expects the length-1)
    
    SET_CSR(CSR_MVUIJUMP_0, -63*8); // new row of patches
    SET_CSR(CSR_MVUIJUMP_1, -65*8); // new patch in this row of patches
    SET_CSR(CSR_MVUIJUMP_2, -66*8); // return to start of this patch (to iterate over it again with a new bit of precision)
    SET_CSR(CSR_MVUIJUMP_3, 30*8); // next row in this patch
    SET_CSR(CSR_MVUIJUMP_4, 1*8); // next pixel

    SET_CSR(CSR_MVUQUANT, 26); // index of the MSB in the output

    SET_CSR(CSR_MVUOMVUSEL, CALC_OMVU_SEL(hart_id));

    // First two 'for' layers:
        // weight should go 9x1
        // input should go 3x3
    // Third 'for' layer:
        // both should go 64 times to allow all 8x8 zigzag combinations to be covered
    // Fourth and fifth 'for' layer:
        // trigger new shacc load
        // weight should reset to 0
        // input should reset accordingly to cover next 3x3 patch
    
    // So weight lengths:
    // 0:   0
    // 1:   0 jumps of 0
    // 2:   64 (-1) jumps of -8
    // 3:    1 (-1) jumps of 1
    // 4:    9 (-1) jumps of 1

    // Inputs:
    // 0:    jump to a new row of 3x3 patches     = -63*prec
    // 1:    jump to next 3x3 patch in row        = -65*prec
    // 2:   64 jumps back to start of 3x3 patch   = -66*prec
    // 3:    3 (-1) jumps to new row of 3x3 patch = +30*prec
    // 4:    3 (-1) jumps of 1

//    for (int i=0; i<4; i++){
        SET_CSR(CSR_MVUWBASEPTR, weight_addr);
        SET_CSR(CSR_MVUOBASEPTR, output_addr);
        SET_CSR(CSR_MVUIBASEPTR, input_addr);
        SET_CSR(CSR_MVUCOMMAND, 0x40000000+30*30*64*9); // mul_mode=1
                                                    // counter = 518400
                                                    // = 30*30*64*9 (input image is 32x32, so we repeat the 3x3 patch 30x30 times. Each time we need to go through 9 weights and 64 zigzag combinations (for 8 bits of precision))
        wait_for_mvu_irq();
//        output_addr += 2;
//        input_addr  += 64;
//    }
    (*final_waddr) = weight_addr;
    (*final_oaddr) = output_addr;
    (*final_iaddr) = input_addr;
}
#endif

void conv3x3_64(int hart_id, int iofst, int oofst, int wofst, int hart_loop_length, int* final_iaddr, int* final_oaddr, int* final_waddr){
    #ifdef STREAM
        conv3x3_64_stream(hart_id, iofst, oofst, wofst, hart_loop_length, final_iaddr, final_oaddr, final_waddr);
    #elif BATCH
        conv3x3_64_batch(hart_id, iofst, oofst, wofst, hart_loop_length, final_iaddr, final_oaddr, final_waddr);
    #endif
}
