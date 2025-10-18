#include"cp_includes.h"
#include"Config.h"
#include"Instruction.h"
#include"ReservationStation.h"
#include"ReservationStationManager.h"
#include"RegisterFile.h"
#include"RegisterStatus.h"
#include "FunctionalUnitManager.h"
#include "CDB.h"
#include"Memory.h"
#include"LoadBuffer.h"
#include"StoreBuffer.h"
class Simulator{
private:
    ull clock;
    Config cfg;
    queue<Instruction>instr_queue;
    ReservationStationManager* rs_manager;
    FunctionalUnitManager* fu_manager;
    RegisterFile* reg_file;
    RegisterStatus* reg_status;
    ReorderBuffer* rob;
    CDB* cdb;
    Memory* memory;
    LoadBuffer* lb;
    StoreBuffer* sb;
public:
    Simulator(const Config&);
    void load_program(vector<Instruction>);
    void run();
    void step();
    bool is_finished();
    void debug_dump_state();
};