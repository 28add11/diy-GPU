`default_nettype none

module matrixProcessor #(
	parameters
) (
	input wire clk,
	input wire rst_n,

	input wire start,
	input wire [13:0] workItemCount, // > 10k, about the number of verts we want to push per frame. Feel free to raise once I get actual performance numbers on this
	input wire [WIDTH - 1:0] matrixInAddr, // Presuming these are registered because of AXI???
	input wire [WIDTH - 1:0] dataInAddr,
	input wire [WIDTH - 1:0] dataOutAddr,
	input wire [WIDTH - 1:0] dataIn,
	output wire [WIDTH - 1:0] readAddr,
	output wire [WIDTH - 1:0] writeAddr,
	output wire [WIDTH - 1:0] writeData,
	output wire writeEn
	);

	reg [13:0] workItemReg;
	reg [3:0] matrixReg

	reg [WIDTH - 1:0] matrixCache [3:0]; // 4x4 matrix cache (Implemented as 1D array because IIRC some tools have compatability issues)

	typedef enum logic [1:0] {IDLE, LOADMATRIX, PROCESSING} statetype;
	statetype state, nextstate;
	
	assign readAddr = matrixInAddr + matrixReg;

	always_comb begin
		case (state)
			IDLE: begin
				if (start) nextstate = LOADMATRIX;
				else 	   nextstate = IDLE;
			end

			LOADMATRIX: begin
				if (matrixReg == 4'hF) nextstate = PROCESSING;
				else 				   nextstate = LOADMATRIX;
			end

			PROCESSING: begin
				if (workItemReg == 0) nextstate = IDLE;
				else 				  nextstate = PROCESSING;
			end

			default: nextstate = IDLE
		endcase
	end

	always_ff @(posedge clk) begin
		if (~rst_n) begin
			state <= IDLE;

		end else begin
			state <= nextstate;

			if (state == IDLE) begin
				
				if (start) begin
					matrixReg <= 4'b0;
					workItemReg <= workItemCount;
				end

			end else if (state == LOADMATRIX) begin
				matrixReg <= matrixReg + 1;
				matrixCache[matrixReg] <= dataIn;

			end else if (state == PROCESSING) begin

				matrixReg <= matrixReg + 1;

				if (matrixReg == 4'hF) begin
					workItemReg <= workItemReg - 1;
				end

			end
		end
	end

endmodule
