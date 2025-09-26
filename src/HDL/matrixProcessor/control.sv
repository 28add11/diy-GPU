`default_nettype none

module matrixProcessorController (
	input wire clk,
	input wire rst_n,

	input wire start,
	input wire workItemCountZero,
	input wire [3:0] matrixRegValue,
	input wire divFinished,
	output logic matrixRegIncrument,
	output logic writeEn,
	output logic pmvcWriteEn,
	output logic wiSource,
	output logic wiInit,
	output logic load,
	output logic loadMatrix,
	output logic loadVector,
	output logic resetMatrixReg,
	output logic readAddrSrc,
	output logic enFMA,
	output logic startDiv
	);

	typedef enum logic [2:0] {IDLE, LOADMATRIX, LOADVECTOR, PROCESSING, STARTDIV, INVERTW, NORMALIZE} statetype;
	statetype state, nextstate;

	wire matrixMax = (matrixRegValue == 4'hF);
	wire vectorMax = (matrixRegValue == 4'h3);
	wire coordsMax = (matrixRegValue == 4'h2); // Ignoring W coordinate

	assign wiInit = (state == IDLE && start);

	always @(*) begin
		if (~rst_n) begin
			wiSource = 0;
			writeEn = 0;
			load = 0;
			loadMatrix = 0;
			loadVector = 0;
			matrixRegIncrument = 0;
			resetMatrixReg = 0;
			readAddrSrc = 0;
			enFMA = 0;
			pmvcWriteEn = 0;
			startDiv = 0;
		end else case (state)
			IDLE: begin
				if (start) nextstate = LOADMATRIX;
				else 	   nextstate = IDLE;

				wiSource = start;
				writeEn = 0;
				load = 0;
				loadMatrix = 0;
				loadVector = 0;
				matrixRegIncrument = 0;
				resetMatrixReg = 0;
				readAddrSrc = 0;
				enFMA = 0;
				pmvcWriteEn = 0;
				startDiv = 0;
			end

			LOADMATRIX: begin
				if (matrixMax) nextstate = LOADVECTOR;
				else 						nextstate = LOADMATRIX;

				wiSource = 0;
				writeEn = 0;
				load = 1;
				loadMatrix = 1;
				loadVector = 0;
				matrixRegIncrument = 1;
				resetMatrixReg = 0; // No need to reset even on out transition because overflow
				readAddrSrc = 0;
				enFMA = 0;
				pmvcWriteEn = 0;
				startDiv = 0;
			end

			LOADVECTOR: begin
				if (vectorMax)  nextstate = PROCESSING; // 4 vectors loaded
				else 			nextstate = LOADVECTOR;
				wiSource = 0;
				writeEn = 0;
				load = 1;
				loadMatrix = 0;
				loadVector = 1;
				matrixRegIncrument = 1;
				resetMatrixReg = vectorMax; // Reset to zero upon exit because we aren't overflowing
				readAddrSrc = 1;
				enFMA = 0;
				pmvcWriteEn = 0;
				startDiv = 0;
			end

			PROCESSING: begin
				if (matrixMax) 	nextstate = STARTDIV;
				else 			nextstate = PROCESSING;

				wiSource = 0;
				writeEn = 0;
				load = 1;
				loadMatrix = 0;
				loadVector = 0;
				matrixRegIncrument = 1;
				resetMatrixReg = 0;
				readAddrSrc = 0;
				enFMA = 1;
				pmvcWriteEn = (matrixRegValue[1:0] == 4'h3);
				startDiv = 0;
			end

			STARTDIV: begin
				nextstate = INVERTW;
				
				wiSource = 0;
				writeEn = 0;
				load = 1;
				loadMatrix = 0;
				loadVector = 0;
				matrixRegIncrument = 0;
				resetMatrixReg = 0;
				readAddrSrc = 0;
				enFMA = 0;
				pmvcWriteEn = 0;
				startDiv = 1;
			end

			INVERTW: begin
				if (divFinished) nextstate = NORMALIZE;
				else 			 nextstate = INVERTW;

				wiSource = 0;
				writeEn = 0;
				load = 0;
				loadMatrix = 0;
				loadVector = 0;
				matrixRegIncrument = 0;
				resetMatrixReg = 0;
				readAddrSrc = 0;
				enFMA = 0;
				pmvcWriteEn = 0;
				startDiv = 0;
			end

			NORMALIZE: begin
				if (workItemCountZero && coordsMax) 	nextstate = IDLE;
				else if (coordsMax)						nextstate = LOADVECTOR;
				else 									nextstate = NORMALIZE;

				wiSource = coordsMax;
				writeEn = 1;
				load = 0;
				loadMatrix = 0;
				loadVector = 0;
				matrixRegIncrument = 1;
				resetMatrixReg = coordsMax;
				readAddrSrc = 0;
				enFMA = 1;
				pmvcWriteEn = 0;
				startDiv = 0;
			end

			default: nextstate = IDLE;
		endcase
	end

	always @(posedge clk) begin
		if (~rst_n) begin
			state <= IDLE;
		end else begin
			state <= nextstate;
		end
	end

endmodule
