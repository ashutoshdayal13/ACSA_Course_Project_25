#include "cp_includes.h"
#include "Printable.h"
#include "Operand.h"
#include "Tag.h"
#include "Opcode.h"
class Instruction:public Printable{
public:
    ll pc;
    Opcode op;
    Operand v1,v2;
    ll dest;//arch reg
    ll imm;
    static Instruction parse(const string&);

    string to_string() const override;
};