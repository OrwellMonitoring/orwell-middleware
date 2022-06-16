#!/bin/bash

python3 -m pytest tests/

if [ $? -ne 0 ]; then
	printf "\n[ERROR] Some tests failed.\n"
	exit 1
fi

printf "\n[OK] All tests passed!\n"


