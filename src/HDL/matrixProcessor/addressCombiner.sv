`default_nettype none

module addrCombiner (
	input wire [3:0] a,
	input wire [13:0] b,
	input wire [WIDTH - 1:0] base,
	output wire [WIDTH - 1:0] address
	);

	wire [17:0] intermediate;
	assign intermediate = {b, a};

	assign address = base + intermediate;

endmodule
