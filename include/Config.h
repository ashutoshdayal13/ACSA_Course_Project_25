#include "cp_includes.h"
#include "FUType.h"
class Config{
public:
    int num_registers, rob_size;
    map<FUType,int> fu_latencies,rs_sizes;
    int issue_width;
    bool use_ROB;
};