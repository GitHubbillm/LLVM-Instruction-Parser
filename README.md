# LLVM Instruction Parser
## Python code that will create a parse tree in memory based on one LLVM instruction.

The purpose of this code is to take one LLVM instruction and parse it, returning a parse tree of nodes that are of type “class Node”. I decided to put it as open in case anyone needs to do something similar. 

The parser relies on [“ply”]( https://www.dabeaz.com/ply/) 3.11. 

There are several caveats about this:

-	I don’t write Python every day. You may look at something and say: “why did he do it that way?” Well, to be honest, because I got it to work.
-	The human readable output from LLVM – sigh – changes every single time a new version comes out. I based this and tested on LLVM 15, and known to need some changes to get to 16, … 
-	It handles _instructions_ not branches. Each LLVM basic block has zero or more instructions followed by a transfer of control, either a branch or a return, for example. We are not concerned with the transfers and they will not parse.
-	I might very well just ignore any pull requests.

There’s a simple test module you can use to play around. 

Hope it is useful to someone.

