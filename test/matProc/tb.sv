`default_nettype none
`timescale 1ns / 1ps

module tb();

	// FST testbench files now! no more vcd!
	initial begin
		$dumpfile("tb.fst");
		$dumpvars(0, tb);
	end

	parameter WIDTH = 32;

	reg clk;
	reg reset;
	logic start;
	logic [13:0] workItemCount;
	logic [WIDTH - 1:0] matrixInAddr;
	logic [WIDTH - 1:0] dataInAddr;
	logic [WIDTH - 1:0] dataOutAddr;
	logic [WIDTH - 1:0] dataIn;
	logic [WIDTH - 1:0] readAddr;
	logic [WIDTH - 1:0] writeAddr;
	logic [WIDTH - 1:0] writeData;
	logic writeEn;

	matrixProcessor #(
		.WIDTH(WIDTH)
	) mp (
		.clk(clk),
		.rst_n(reset),
		.start(start),
		.workItemCount(workItemCount),
		.matrixInAddr(matrixInAddr),
		.dataInAddr(dataInAddr),
		.dataOutAddr(dataOutAddr),
		.dataIn(dataIn),
		.readAddr(readAddr),
		.writeAddr(writeAddr),
		.writeData(writeData),
		.writeEn(writeEn)
	);


endmodule
