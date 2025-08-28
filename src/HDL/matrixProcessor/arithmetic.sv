`default_nettype none

module fuseMultAdd #(
	parameter WIDTH = 32
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
	input wire en
);
	
	reg [WIDTH - 1:0] accumulator;

	reg [WIDTH - 1:0] productADD; // Maybe shift before ending up in this reg?? Only change if it doesn't meet timing

	wire [(2 * WIDTH) - 1:0] product;
	assign product = a * b;

	wire [WIDTH - 1:0] accumulatorSrc;
	assign accumulatorSrc = (updateAccumulator) ? seed : accumulator;

	always @(posedge clk) begin
		if (~rst_n) begin
			accumulator <= 0;
		end else begin
			if (en) begin
				accumulator <= accumulatorSrc + product;
			end
		end
	end
	
endmodule
