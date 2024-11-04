# ============================================================
#
# instruction
#
# Take a parsed LLVM instruction and "genericize" it to what we need to do.
#
# Author:   Bill Mahoney
#
# ============================================================

from __future__ import annotations

import sys
# import os

from llvm_inst_parser import llvm_instruction_parser as parser

############################################################
# All types of possible ValueInstruction (common ones moved to the front).
############################################################

value_instruction_types = [
    "CallInst",           # Call ... a type of ValueInstruction
    "AllocaInst",         # %4 = alloca ... a type of ValueInstruction
    "GetElementPtrInst",
    "ICmpInst",           # Compare integers

    "AddInst", "FAddInst", "SubInst", "FSubInst", "MulInst", "FMulInst", "UDivInst", "SDivInst", "FDivInst",
    "URemInst", "SRemInst", "FRemInst", "ShlInst", "LShrInst", "AShrInst", "AndInst", "OrInst", "XorInst",
    "ExtractElementInst", "InsertElementInst", "ShuffleVectorInst", "ExtractValueInst", "InsertValueInst",
    "LoadInst", "TruncInst", "ZExtInst", "SExtInst", "FPTruncInst", "FPExtInst", "FPToUIInst", "FPToSIInst",
    "UIToFPInst", "SIToFPInst", "PtrToIntInst", "IntToPtrInst", "BitCastInst", "AddrSpaceCastInst",
    "FCmpInst", "PhiInst", "SelectInst", "VAArgInst", "LandingPadInst", "CatchPadInst", "CleanupPadInst",
    "CmpXchgInst", "AtomicRMWInst"
    ]

other_instruction_types = [ "StoreInst", "FenceInst" ]

############################################################
#
# Here's the grammar:
#
# Instruction -> StoreInst
#             -> FenceInst
#             -> LocalIdent = ValueInstruction
#             -> ValueInstruction
#
############################################################

class Instruction:

    ############################################################
    # Constructor
    ############################################################
    def __init__(self, instruction_string: str) -> None:
        # Reset the node numbers for each instruction in case we graph it.
        # For debugging we can look at the graph and print the node
        # serial numbers so we cansee if things are right.
        parser._serial_number = 0
        self.root = parser.inst_parse( instruction_string )
        if self.root is None:
            print( "The instruction did not parse correctly:" )
            print( instruction_string )
            print( "Bill, what did you do wrong now???" )

    ############################################################
    # Tell me if the instruction is a particular type (given in "look_for")
    ############################################################
    def is_instruction_a(self, look_for: str) -> bool:
        if ( self.root.locate_tree_node( look_for ) ):
            return True
        return False

    ############################################################
    # Conversely, tell me the type of the instruction.
    ############################################################
    def instruction_type(self) -> str | None:
        for kind in value_instruction_types:
            if ( self.is_instruction_a( kind ) ):
                return kind
        for kind in other_instruction_types:
            if ( self.is_instruction_a( kind ) ):
                return kind
        return None

    ############################################################
    # If the instruction is a "ValueInstruction" it MIGHT have a left
    # hand side that is assigned to. Two functions here...  The first
    # tells if it has an assignment, the second gets the
    # identifier. Probably don't call the second before you know the
    # answer from the first.
    ############################################################
    def has_lhs(self) -> bool:
        here = self.root
        if ( len( here.children ) >= 3 ):
            if ( here.children[ 1 ].nodetype == "=" ):
                return True
        return False
    
    def get_lhs(self) -> str | None:
        here = self.root
        if ( len( here.children ) >= 3 ):
            if ( here.children[ 0 ].nodetype == "LocalIdent" ):
                # This'll be the string in the terminal node.
                value = here.children[ 0 ].children[ 0 ].nodetype
                assert isinstance(value, str)
                return value
        return None

    ############################################################
    # Get the return type of a function. This is (as usual) dependent
    # on the grammar, so "Type" is in child 5
    #
    # CallInst -> OptTail call FastMathFlags OptCallingConv ReturnAttrs
    #             Type Value '(' Args ')' FuncAttrs OperandBundles
    #             OptCommaSepMetadataAttachmentList
    #
    # Then that particular instance of Type:
    #
    # Type     -> FuncType
    # FuncType -> Type ( Params )
    #
    # So NOTE: What I return here is the root of the sub-tree starting
    # at Type (before the paren's). NOT the type itself.
    ############################################################
    def get_call_return_type(self) -> parser.Node | None:
        call_root = self.root.locate_tree_node( "CallInst" )
        if call_root is None:
            return None
        top_type = call_root.children[ 5 ]
        func_type = top_type.children[ 0 ]
        ret_type = func_type.children[ 0 ]
        assert isinstance(ret_type, parser.Node)
        return ret_type

    ############################################################
    # Get a list of the parameters to a function. Grammar is:
    #
    # Args    -> empty
    #         -> elipsis (...)
    #         -> ArgList
    #         -> ArgList , elipsis
    # ArgList -> Arg
    #         -> ArgList , Arg
    # Arg     -> ConcreteType ParamAttrs Value
    #         -> MetadataType Metadata
    #
    # Note that it is left recursive.
    # NOTE: what we return is a list of roots of trees at "Arg".
    ############################################################
    def get_call_arg_list(self) -> list[parser.Node] | None:
        call_root = self.root.locate_tree_node( "CallInst" )
        if call_root is None:
            return None
        call_root.locate_tree_node( "Args" )
        al = call_root.locate_tree_node( "ArgList" )
        # Args can be empty
        if ( al is None ):
            return None
        else:
            arg_roots = []
            while ( len( al.children ) > 1 ):
                arg_roots.append( al.children[ 2 ] )
                al = al.children[ 0 ]
            arg_roots.append( al.children[ 0 ] )
            # Have to do this in two steps, not sure why.
            arg_roots.reverse()
            return arg_roots

############################################################
#
# Let's run some tests. These make no sense because I just copy/pasted
# them out of all sorts of places.
#
############################################################

def tests() -> None:
    testdata = [
        '%buf.i.i = alloca [250 x i8], align 16',
        '%yymsgbuf = alloca [128 x i8], align 16',
        '%yyvsa = alloca [200 x i8*], align 16',
        '%ref.tmp = alloca %"class.std::__cxx11::basic_string", align 8',
        '%0 = getelementptr inbounds [128 x i8], [128 x i8]* %yymsgbuf, i64 0, i64 0',
        'call void @llvm.lifetime.start.p0i8(i64 128, i8* nonnull %0) #13',
        '%1 = bitcast [200 x i16]* %yyssa to i8*',
        '%arraydecay1 = getelementptr inbounds [200 x i16], [200 x i16]* %yyssa, i64 0, i64 0',
        '%2 = bitcast [200 x i8*]* %yyvsa to i8*',
        '%arraydecay2 = getelementptr inbounds [200 x i8*], [200 x i8*]* %yyvsa, i64 0, i64 0',
        '%3 = load i32, i32* @expressionyydebug, align 4, !tbaa !2',
        '%tobool = icmp eq i32 %3, 0',
        '%_IO_read_ptr = getelementptr inbounds %struct._IO_FILE, %struct._IO_FILE* %__fp, i64 0, i32 1',
        '%0 = load i8*, i8** %_IO_read_ptr, align 8, !tbaa !6',
        '%_IO_read_end = getelementptr inbounds %struct._IO_FILE, %struct._IO_FILE* %__fp, i64 0, i32 2',
        '%1 = load i8*, i8** %_IO_read_end, align 8, !tbaa !11',
        '%cmp = icmp ult i8* %0, %1',
        '%call9 = call i32 (%struct._IO_FILE*, i8*, ...) @fprintf(%struct._IO_FILE* %9, i8* getelementptr inbounds ([19 x i8], [19 x i8]* @.str.1, i64 0, i64 0), i32 %yystate.1832) #14'
    ]

    main(testdata)

    # These are from the compiler explorer web site, the "sander" little
    # function, with instructions that are syntactically identical
    # removed.

    testdata = [
        "%3 = alloca i32, align 4",
        # Both the old kind (pre version 15) and the new kind:
        "store i32 %0, i32* %3, align 4",
        "store i32 %0, ptr %3, align 4",
        # Both the old kind (pre version 15) and the new kind:
        "%6 = load i32, i32* %3, align 4",
        "%6 = load i32, ptr %3, align 4",
        "%8 = icmp slt i32 %6, %7",
        "%10 = load i32, i32* %3, align 4",
        "%14 = phi i32 [ %10, %9 ], [ %12, %11 ]",
        "store i32 %14, i32* %5, align 4",
        "%16 = shl i32 %15, 2",
    ]

    main(testdata)

############################################################
# Main test code
############################################################

def main(testdata: list[str]) -> None:
    i = 1
    for i, t in enumerate(testdata):

        inst = Instruction( t )
        tree = inst.root
        tree.graph( "testdata_" + str( i ) + ".dot", True )

        which = inst.instruction_type()
        if ( which is None ):
            print( 'There is a problem here - what kind of instruction is this???' )
            print( inst.root.tree_as_string() )
            sys.exit( 1 )
            
        print( f'    Instruction type is {which}' )
        if ( inst.has_lhs() ):
            print( f'    Assigns to {inst.get_lhs()}'  )

        # Now specific types.
        if ( which == "StoreInst" ):
            r = tree.locate_tree_node( "StoreInst" ) # (Dumb - it is child 0)
            print( '    Type as paren-string: ' + r.children[ 2 ].tree_as_string() )
            print( '    Value to store: ' + r.children[ 3 ].tree_as_string() )

        elif ( which == "AllocaInst" ):
            print( f'    Assigning space to {inst.get_lhs()}' )

        elif ( which == "ICmpInst" ):
            ic = tree.locate_tree_node( "ICmpInst" )
            print( '    Compares ' + ic.children[ 1 ].children[ 0 ].nodetype + ' ' +
                   ic.children[ 3 ].tree_as_string() + 
                   ic.children[ 5 ].tree_as_string() )

        elif ( which == "CallInst" ):
            return_type = inst.get_call_return_type()
            assert isinstance(return_type, parser.Node)
            print( '    Return type subtree: ' +
                   return_type.tree_as_string() )
            # This gives back a list of sub-tree roots.
            args = inst.get_call_arg_list()
            if ( args is None ):
                print( '    There are no parameters...' )
            else:
                print( '    There are ' + str( len( args ) ) + ' parameters to the function...' )
                for a in args:
                    # Arg -> ConcreteType ParamAttrs Value
                    #     -> MetadataType Metadata
                    print( '    Argument node serial number ' + str(a.serial) )
                    if ( len( a.children ) > 2 ):
                        p = a.children[ 2 ].locate_tree_node( "LocalIdent" )
                        if ( p is not None ):
                            child = p.children[ 0 ]
                            assert isinstance(child, parser.Node)
                            print( '    Identifier ' + child.nodetype )
                        p = a.children[ 2 ].locate_tree_node( "Constant" )
                        if ( p != None ):
                            print( '    One of them is a constant' )


if __name__ == "__main__":
    tests()
