#include "cp_includes.h"
#include "Tag.h"
#include "Opcode.h"
#include "Instruction.h"
class RSEntry{
public:
    Tag tag;
    bool busy;
    Opcode op;
    bool Vj_valid; ll Vj;
    bool Vk_valid; ll Vk;
    optional<Tag> Qj,Qk,dest_tag;
    bool issued_to_fu;
    int cyc_rem;
    Instruction instr;
    void clear();
    bool is_ready();  
};