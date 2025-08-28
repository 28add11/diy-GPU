`default_nettype none

module matrixProcessorController (
	input wire clk,
	input wire rst_n,

	input wire start,
	input wire workItemCountZero,
	input wire [3:0] matrixRegValue,
	output logic matrixRegIncrument,
	output logic writeEn,
	output logic wiSource,
	output logic wiInit,
	output logic load,
	output logic loadMatrix,
	output logic loadVector,
	output logic resetMatrixReg,
	output logic readAddrSrc,
	output logic enFMA
	);

	typedef enum logic [1:0] {IDLE, LOADMATRIX, LOADVECTOR, PROCESSING} statetype;
	statetype state, nextstate;

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
			end

			LOADMATRIX: begin
				if (matrixRegValue == 4'hF) nextstate = LOADVECTOR;
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
			end

			LOADVECTOR: begin
				if (matrixRegValue == 4'h3) nextstate = PROCESSING; // 4 vectors loaded
				else 					   nextstate = LOADVECTOR;
				wiSource = 0;
				writeEn = 0;
				load = 1;
				loadMatrix = 0;
				loadVector = 1;
				matrixRegIncrument = 1;
				resetMatrixReg = (matrixRegValue == 4'h3); // Reset to zero upon exit because we aren't overflowing
				readAddrSrc = 1;
				enFMA = 0;
			end

			PROCESSING: begin
				if (workItemCountZero) nextstate = IDLE;
				else 				   nextstate = PROCESSING;

				wiSource = (matrixRegValue[1:0] == 4'hF);
				writeEn = (matrixRegValue[1:0] == 4'hF);
				load = 0;
				loadMatrix = 0;
				loadVector = 0;
				matrixRegIncrument = 1;
				resetMatrixReg = 0;
				readAddrSrc = 0;
				enFMA = 1;
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
