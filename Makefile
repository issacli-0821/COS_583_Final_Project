clean:
	-rm -f example_c_files/*.ll example_c_files/*.s
	-rm -f assembler/output/*.obj assembler/output/*.bin
	-rmdir assembler/output