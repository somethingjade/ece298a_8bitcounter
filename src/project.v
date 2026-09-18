/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

	reg [7:0] shift;
	reg [7:0] count;
	// ui_in[0] is serial data in
	// ui_in[1] is shift_en
	// ui_in[2] is load
	// ui_in[3] is output_en

	always @(posedge clk or negedge rst_n) begin
		if (!rst_n) begin
			shift <= 0;
			count <= 0;
		end else begin
			if (ui_in[1])
				shift <= {ui_in[0], shift[7:1]};
			if (ui_in[2])
				count <= shift;
			else
				count <= count + 1;
		end
	end

	assign uio_oe = ui_in[3] ? 8'b1 : 8'b0;
	assign uio_out = count;

	// All output pins must be assigned. If not used, assign to 0.
	// assign uo_out  = ui_in + uio_in;  // Example: ou_out is the sum of ui_in and uio_in
	// assign uio_out = 0;
	// assign uio_oe  = 0;
	assign uo_out = 0;

	// List all unused inputs to prevent warnings
	wire _unused = &{ena, uio_in, ui_in[7:4], 1'b0};

endmodule
