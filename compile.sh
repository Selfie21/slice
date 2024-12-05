rm -rf .build/
mkdir -p .build && cd .build
cmake $SDE/p4studio/ -DCMAKE_INSTALL_PREFIX=$SDE/install -DCMAKE_MODULE_PATH=$SDE/cmake  -DP4_NAME=$1 -DP4_PATH=/data/slice/$1/$1.p4 -DP4_LANG=p4-16 -DTOFINO=1
make $1 && make install
$SDE_INSTALL/bin/bf_kdrv_mod_load $SDE_INSTALL
cd $SDE
./run_switchd.sh -p $1
