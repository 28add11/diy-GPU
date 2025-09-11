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
	input wire readAddrSrc,
	input wire enFMA,
	input wire controllerWriteEn,

	input wire [13:0] workItemCount, // > 10k, about the number of verts we want to push per frame. Feel free to raise once I get actual performance numbers on this
	input wire [WIDTH - 1:0] matrixInAddr, // Presuming these are registered because of AXI???
	input wire [WIDTH - 1:0] dataInAddr,
	input wire [WIDTH - 1:0] dataOutAddr,
	input wire [WIDTH - 1:0] dataIn,
	output wire [WIDTH - 1:0] readAddr,
	output wire [WIDTH - 1:0] writeAddr,
	output wire [WIDTH - 1:0] writeData,
	output wire workItemCountZero,
	output wire [3:0] matrixRegValue,
	output wire writeEn
	);

	reg [13:0] workItemReg;
	reg [3:0] matrixReg;
	wire [13:0] workItemNext;
	wire [3:0] matrixCountNext;

	assign workItemNext = wiInit ? workItemCount : (workItemReg - 1);

	reg [3:0] matrixRegPipeline;
	reg dataConsumePipeline;
	reg loadMatrixPipeline;
	reg loadVectorPipeline;

	reg writeEnPipeline;
	wire updateAccumulator;
	reg updateAccumulatorPipeline;
	assign updateAccumulator = (matrixReg[1:0] == 0);

	reg [WIDTH - 1:0] matrixCache [15:0]; // 4x4 matrix cache (Implemented as 1D array because IIRC some tools have compatability issues)
	reg [WIDTH - 1:0] vectorCache [3:0]; // 1x4 vector
	reg [WIDTH - 1:0] matrixReadReg;
	reg [WIDTH - 1:0] vectorReadReg;

	wire [17:0] vectorReadIndex;
	assign vectorReadIndex = {workItemReg, matrixReg[1:0]};
	wire [17:0] vectorWriteIndex;
	assign vectorWriteIndex = {workItemReg, matrixRegPipeline[3:2]};

	wire [WIDTH - 1:0] writeAddrInternal;
	reg [WIDTH - 1:0] writeAddrPipeline;
	assign readAddr = (readAddrSrc ? (dataInAddr) : matrixInAddr) + (readAddrSrc ? (vectorReadIndex << 2) : (matrixReg << 2));
	assign writeAddrInternal = dataOutAddr + vectorWriteIndex;
	assign writeAddr = writeAddrPipeline;

	assign writeEn = writeEnPipeline;

	assign workItemCountZero = (workItemReg == 0);
	assign matrixRegValue = matrixReg;

	wire [WIDTH - 1:0] debug;
	assign debug = vectorCache[3];

	fuseMultAdd #(.WIDTH(WIDTH)) fma(
		.clk(clk),
		.rst_n(rst_n),
		.a(matrixReadReg),
		.b(vectorReadReg),
		.accumulatorOut(writeData),
		.seed(0),
		.updateAccumulator(updateAccumulatorPipeline),
		.en(enFMA)
	);

	always @(posedge clk) begin
		if (~rst_n) begin
			matrixReg <= 0;
			matrixRegPipeline <= 0;
			writeEnPipeline <= 0;
			updateAccumulatorPipeline <= 0;
			dataConsumePipeline <= 0;
			loadMatrixPipeline <= 0;
			loadVectorPipeline <= 0;

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
				matrixRegPipeline <= matrixReg;
				dataConsumePipeline <= 1;
				loadMatrixPipeline <= loadMatrix;
				loadVectorPipeline <= loadVector;
			end else begin
				dataConsumePipeline <= 0;
			end

			if (dataConsumePipeline && loadMatrixPipeline) begin
				matrixCache[matrixRegPipeline] <= dataIn;
			end
			if (dataConsumePipeline && loadVectorPipeline) begin
				vectorCache[matrixRegPipeline] <= dataIn;
			end
			
			if (controllerWriteEn) begin
				writeAddrPipeline <= writeAddrInternal;
			end

			writeEnPipeline <= controllerWriteEn;
			updateAccumulatorPipeline <= updateAccumulator;

			matrixReadReg <= matrixCache[matrixReg];
			vectorReadReg <= vectorCache[matrixReg[1:0]];
		end
	end

endmodule
