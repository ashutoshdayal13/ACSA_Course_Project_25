#include"cp_includes.h"
class Memory{
public:
    Memory();
    ll load(ull);
    void store(ull,ll);
private:
    map<ull,ll>mem;
};