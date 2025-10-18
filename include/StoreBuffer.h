#include"cp_includes.h"
#include"RSEntry.h"
#include"Instruction.h"
#include"Memory.h"
#include"ReorderBuffer.h"
class StoreBuffer{
public:
    optional<RSEntry*>allocate_store(const Instruction&);
    void on_broadcast(Tag,ll);
    void commit_stores_to_memory(Memory&,ReorderBuffer&);
private:
    vector<RSEntry>entries;
};