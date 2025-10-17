#include "cp_includes.h"
#include "Printable.h"

class Operand:public Printable{
private:
    bool is_reg;
    ll reg_idx, imm;
public:
    string to_string() const override;
};