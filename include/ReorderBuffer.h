#include"cp_includes.h"
#include "ROBEntry.h"
#include"Opcode.h"
#include"Instruction.h"
#include"Tag.h"
class ReorderBuffer{
public:
    ReorderBuffer(int capacity);
    optional<Tag> allocate(Opcode,int,const Instruction&);
    void mark_ready(Tag,ll);
    optional<ROBEntry> try_commit();
    bool has_free_entry();
    bool empty();
private:
    vector<ROBEntry>entries;
    int head,tail,capacity;
};