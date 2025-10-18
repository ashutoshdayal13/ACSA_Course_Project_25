#include"cp_includes.h"
#include "Tag.h"
#include "Opcode.h"
#include "Instruction.h"
class ROBEntry{
public:
    Tag id;
    bool busy;
    Opcode type;
    int dest_reg;
    optional<ll>value;
    bool ready;
    Instruction instr;
};