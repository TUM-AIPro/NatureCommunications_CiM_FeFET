
######   21 September 2023   ######

The simulation framework that supports the findings of the manuscript "First Demonstration of In-Memory Computing Crossbar using Multi-level Cell FeFET" submitted in Nature Communications is available in this repository.

The Multi-Level-Cell (MLC) FeFET In-Memory-Computing (IMC) framework was developed by Swetaki Chatterjee under the guidance of Dr. Taha Soliman (Robert Bosch GmbH, Germany), Prof. Yogesh Singh Chauhan (Indian Institute of Technology Kanpur, India), and Prof. Hussam Amrouch (Technical University of Munich, Germany). The research work was conducted during the research visit of Swetaki Chatterjee to the University of Stuttgart. 

The framework is made publicly available on a non-commercial basis. Copyright of the framework along with all related data is maintained by the developers, and the framework is distributed under the terms of the Creative Commons Attribution-NonCommercial 4.0 International Public License.

Wherever the framework or any related data obtained from this repository is used, a proper citation for this repository as well as the above paper "First Demonstration of In-Memory Computing Crossbar using Multi-level Cell FeFET" must be provided.  


#####  Key Features  #####

This is the first version of the framework. The key features of this framework are:

1. Simulate in SPICE the MLC FeFET I-V characteristics with or without variability. 

2. Simulate the 2-bit Multiply-Accumulate (MAC) operations for 2-bit input activation and 2-bit weight stored within different number of cells in the array.

####  Using the Framework   #####

To run the MLC FeFET I-V characteristics:

1. Uncomment the commented lines to run with variation.

2. Execute the SPICE setlist id_vg.sp. The SPICE netlist was tested for the spectre tool from Cadence. 


To run the 2-bit MAC operations:

1. run python generator.py <root_output_folder> <number_of_cells> <capacitance>

2. source spectre 

3. run netlists_bucketed.py <root_output_folder>


##### System Requirements #####

Python version 3.0 or later

Cadence Spectre version 18.10.077

Please note the Verilog-A code for the Ferroelectric-FDSOI cannot be shared at the moment due to confidentiality clause. 















