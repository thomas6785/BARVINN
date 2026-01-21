`timescale 1ns/1ps

`include "rv32_defines.svh"

import mvu_pkg::*;
import rv32_pkg::*;

module barvinn #(
)(
    pito_soc_ext_interface pito_ext_intf,
    MVU_EXT_INTERFACE      mvu_ext_intf
);
    // Connecting global reset
    assign mvu_ext_intf.rst_n = pito_ext_intf.rst_n;

    // Connet interrupt
    assign pito_ext_intf.mvu_irq = mvu_ext_intf.irq;
    
    // TODO provide data transposer for MVU memory access

    // Bindings:
    APB #(
        .ADDR_WIDTH(pito_pkg::APB_ADDR_WIDTH), 
        .DATA_WIDTH(pito_pkg::APB_DATA_WIDTH)
    ) apb_interface();

    mvutop_wrapper mvu(.mvu_ext_if(mvu_ext_intf),
                       .apb(apb_interface.Slave));
    pito_soc soc(.ext_intf(pito_ext_intf.soc_ext), 
                 .mvu_apb(apb_interface.Master));
endmodule