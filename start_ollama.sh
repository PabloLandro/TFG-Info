#! /bin/bash

ml udocker
udocker setup --nvidia mycontainer
udocker run --publish=11434:11434 mycontainer ollama serve
