`default_nettype none
`timescale 1ns / 1ps

module tb();

	// FST testbench files now! no more vcd!
	//initial begin
	//	$dumpfile("tb.fst");
	//	$dumpvars(0, tb);
	//end

	parameter WIDTH = 32;

	reg clk;
	reg reset;
	logic start;
	logic [WIDTH - 1:0] numerator;
	logic [WIDTH - 1:0] denominator;
	logic [WIDTH - 1:0] quotient;
	logic finished;

	divider #(
		.WIDTH(WIDTH)
	) div (
		.clk(clk),
		.rst_n(reset),
		.start(start),
		.numerator(numerator),
		.denominator(denominator),
		.quotient(quotient),
		.finished(finished)
	);


endmodule
