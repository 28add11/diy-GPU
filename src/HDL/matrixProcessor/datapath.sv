`default_nettype none

module matrixProcessorDatapath #(
	parameter WIDTH = 32
) (
	input wire clk,
	input wire rst_n,

	input wire start,
	input wire wiSource,
	input wire wiInit,
	input wire resetMatrixReg,
	input wire matrixRegIncrument,
	input wire load, // Memory address pipelining
	input wire loadMatrix, // Destination selection
	input wire loadVector,

	input wire [13:0] workItemCount, // > 10k, about the number of verts we want to push per frame. Feel free to raise once I get actual performance numbers on this
	input wire [WIDTH - 1:0] matrixInAddr, // Presuming these are registered because of AXI???
	input wire [WIDTH - 1:0] dataInAddr,
	input wire [WIDTH - 1:0] dataOutAddr,
	input wire [WIDTH - 1:0] dataIn,
	output wire [WIDTH - 1:0] readAddr,
	output wire [WIDTH - 1:0] writeAddr,
	output wire [WIDTH - 1:0] writeData,
	output wire workItemCountZero,
	output wire [3:0] matrixRegValue
	);

	reg [13:0] workItemReg;
	reg [3:0] matrixReg;
	wire [13:0] workItemNext;
	wire [3:0] matrixCountNext;

	assign workItemNext = wiInit ? workItemCount : (workItemReg - 1);

	reg [WIDTH - 1:0] loadAddrPipeline;
	reg dataConsumePipeline;

	reg [WIDTH - 1:0] matrixCache [15:0]; // 4x4 matrix cache (Implemented as 1D array because IIRC some tools have compatability issues)
	reg [WIDTH - 1:0] vectorCache [4:0]; // 1x4 vector

	assign readAddr = matrixInAddr + (matrixReg << 2);

	assign workItemCountZero = (workItemReg == 0);
	assign matrixRegValue = matrixReg;

	wire [WIDTH - 1:0] debug;
	assign debug = matrixCache[15];

	always @(posedge clk) begin
		if (~rst_n) begin
			matrixReg <= 0;
			loadAddrPipeline <= 0;

		end else begin

			if (wiSource) begin
				workItemReg <= workItemNext;
			end
				
			if (resetMatrixReg) begin
				matrixReg <= 4'b0;
			end else if (matrixRegIncrument) begin
				matrixReg <= matrixReg + 1;
			end

			if (load) begin
				loadAddrPipeline <= matrixReg;
				dataConsumePipeline <= 1;
			end else begin
				dataConsumePipeline <= 0;
			end

			if (dataConsumePipeline && loadMatrix) begin
				matrixCache[loadAddrPipeline] <= dataIn;
			end
			if (dataConsumePipeline && loadVector) begin
				vectorCache[loadAddrPipeline] <= dataIn;
			end
			
		end
	end

endmodule
