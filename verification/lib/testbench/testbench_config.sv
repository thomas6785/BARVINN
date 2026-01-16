import utils::*;

class tb_config extends BaseObj;

    string firmware;
    string rodata;
    string testname;

    function new(Logger logger);
        super.new(logger);
    endfunction

    function parse_args();

        if ($value$plusargs("firmware=%s", this.firmware)) begin
            logger.print($sformatf("Using %s as firmware", firmware));
        end else begin
            logger.print($sformatf("Expecting a command line argument %s", firmware), "ERROR");
            this.firmware = "/home/tudentstudent/BARVINN_3/conv_text.hex"; // TODO remove this temporary hardcode
        end

        if ($value$plusargs("rodata=%s", this.rodata)) begin
            logger.print($sformatf("Using %s as read only data", rodata));
        end else begin
            logger.print($sformatf("Expecting a command line argument %s", rodata), "ERROR");
            this.rodata = "/home/tudentstudent/BARVINN_3/conv_data.hex"; // TODO remove this temporary hardcode
        end

        if ($value$plusargs("testname=%s", this.testname)) begin
            logger.print($sformatf("Using %s as testname", testname));
        end else begin
            logger.print($sformatf("Expecting a command line argument %s", testname));
        end

    endfunction

endclass
