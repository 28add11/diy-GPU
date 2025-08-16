`default_nettype none

module fuseMultAdd #(
	parameters
) (
	input wire clk,
	input wire rst_n,
	// Arithmetic signals
	input wire [WIDTH - 1:0] a,
	input wire [WIDTH - 1:0] b,
	output wire [WIDTH - 1:0] accumulatorOut,
	input wire [WIDTH - 1:0] seed,
	// Control signals
	input wire updateAccumulator,
	input wire inputGood,
	output wire inReady,
	output wire outGood
);
	
	reg [WIDTH - 1:0] accumulator;

	reg [WIDTH - 1:0] productADD; // Maybe shift before ending up in this reg?? Only change if it doesn't meet timing

	wire [(2 * WIDTH) - 1:0] product;
	assign product = a * b;

	reg outGoodReg;
	assign inReady <= 1;

	always @(posedge clk) begin
		if (~rst_n) begin
			accumulator <= 0;
			outGoodReg <= 0;
		end else begin
			if (updateAccumulator) begin
				accumulator <= seed;
			end else if (inputGood) begin
				accumulator <= accumulator + product;
				outGoodReg <= 1;
			end
		end
	end
	
endmodule
