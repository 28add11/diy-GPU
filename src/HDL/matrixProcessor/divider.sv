`default_nettype none

module divider #(
		parameter WIDTH=32
	) (
	input wire clk,
	input wire rst_n,
	input wire start,
	input wire signed [WIDTH - 1:0] numerator,
	input wire signed [WIDTH - 1:0] denominator, 
	output wire signed [WIDTH - 1:0] quotient,
	output wire finished
	);

	parameter WAIT = 1'b0;
	parameter DIVIDE = 1'b1;

	reg signCorrect;
	reg [WIDTH - 1:0] quotientInternal;
	reg [WIDTH - 1:0] dividendSignCorrect;
	reg [WIDTH - 1:0] divisorSignCorrect;
	reg [WIDTH - 1:0] remainder;
	wire [WIDTH - 1:0] nextRemainder;

	assign quotient = (signCorrect ? ~quotientInternal + 1 : quotientInternal);

	reg state;
	// Minimum bit width to store value from 0 to WIDTH
	reg [$clog2(WIDTH) - 1:0] count;

	assign finished = ~state;
	assign nextRemainder = {remainder, dividendSignCorrect[count]};
	
	always @(posedge clk) begin
		if (~rst_n) begin
			state <= WAIT;
		end else begin

		if (start) begin // Initialize everything to starting values
			state <= DIVIDE;
			count <= WIDTH - 1;
			signCorrect <= numerator[31] ^ denominator[31];
			dividendSignCorrect <= (numerator[31] ? ~numerator + 1 : numerator);
			divisorSignCorrect <= (denominator[31] ? ~denominator + 1 : denominator);
			remainder <= 0;
			quotientInternal <= 0;
		end
		if (state == DIVIDE) begin // Simple shift and subtract division algorithm
			// No matter if divisor can fit in remainder, add in the next bit of dividend
			// If it does happen to fit, subtract (this is where we would add a 1 to the quotient but we dont need that)
			if (nextRemainder >= divisorSignCorrect) begin
				remainder <= nextRemainder - divisorSignCorrect;
				quotientInternal[count] <= 1;
			end else begin
				remainder <= nextRemainder;
			end

			// End case
			if (count == 0) begin
				state <= WAIT;
			end

			count <= count - 1;
		end
		end
	end

endmodule