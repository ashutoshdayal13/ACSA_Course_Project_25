#include"cp_includes.h"
class RegisterFile{
public:
    RegisterFile(int n);
    ll read(int idx);
    void write(int idx,ll val);
    int size();
private:
    vector<ll> regs;
};