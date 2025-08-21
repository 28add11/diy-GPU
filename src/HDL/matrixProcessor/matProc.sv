`default_nettype none

module matrixProcessor #(
	parameter WIDTH = 32
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

	wire wiSource, wiInit;
	wire workItemCountZero;
	wire [3:0] matrixRegValue;
	wire resetMatrixReg, matrixRegIncrument;
	wire load, loadMatrix, loadVector;

	matrixProcessorDatapath #(.WIDTH(WIDTH)) datapath (
		.clk(clk),
		.rst_n(rst_n),
		.start(start),
		.wiSource(wiSource),
		.wiInit(wiInit),
		.resetMatrixReg(resetMatrixReg),
		.matrixRegIncrument(matrixRegIncrument),
		.workItemCount(workItemCount),
		.matrixInAddr(matrixInAddr),
		.dataInAddr(dataInAddr),
		.dataOutAddr(dataOutAddr),
		.dataIn(dataIn),
		.readAddr(readAddr),
		.writeAddr(writeAddr),
		.writeData(writeData),
		.workItemCountZero(workItemCountZero),
		.matrixRegValue(matrixRegValue),
		.load(load),
		.loadMatrix(loadMatrix),
		.loadVector(loadVector)
	);

	matrixProcessorController controller (
		.clk(clk),
		.rst_n(rst_n),
		.start(start),
		.workItemCountZero(workItemCountZero),
		.matrixRegValue(matrixRegValue),
		.matrixRegIncrument(matrixRegIncrument),
		.writeEn(writeEn),
		.wiSource(wiSource),
		.wiInit(wiInit),
		.load(load),
		.loadMatrix(loadMatrix),
		.loadVector(loadVector),
		.resetMatrixReg(resetMatrixReg),
	);

endmodule
