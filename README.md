# flask-app

### create database

python initdb.py

### how to run

python api.py

### sql to create a new field

ALTER TABLE kifu ADD column is_analyse boolean NOT NULL default 0;
ALTER TABLE kifu ADD column analyse_data char(2500);
ALTER TABLE kifu ADD column moves INTEGER NOT NULL default 0; 

### leela zero

https://github.com/lightvector/leela-analysis
https://github.com/jumpman24/sgf-analyzer
https://github.com/fohristiwhirl/leela_zero_analysis

### gtp reference

http://www.lysator.liu.se/~gunnar/gtp/gtp2-spec-draft2/gtp2-spec.html

#### leela-zero

--gtp -w F:\Tools\go\leela-zero-0.17-cpuonly-win64\networks\86fa6e9897785c5583de41a5cef4132eacb167c85e68e0f0bd063b75ae15ca58.gz --noponder
https://zhuanlan.zhihu.com/p/36299251

#### satago

gtp -model F:\Tools\go\katago\default_model.bin.gz

time_settings 0 5 1

### build leela-zero on linux

```
# Test for OpenCL support & compatibility
sudo apt install clinfo && clinfo

# Clone github repo
git clone https://github.com/leela-zero/leela-zero
cd leela-zero
git submodule update --init --recursive

# Install build depedencies
sudo apt install cmake g++ libboost-dev libboost-program-options-dev libboost-filesystem-dev opencl-headers ocl-icd-libopencl1 ocl-icd-opencl-dev zlib1g-dev

# Use a stand alone build directory to keep source dir clean
mkdir build && cd build

# Compile leelaz and autogtp in build subdirectory with cmake
## build on cpu
cmake -DUSE_CPU_ONLY=1 ..
## build on gpu
cmake ..
cmake --build .

# Optional: test if your build works correctly
./tests
```


### python debug configuation
```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: lza",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}\\lza.py",
            "args" : ["test.sgf"],
            "console": "integratedTerminal"
        }
    ]
}
```

### leela analysis
####
https://github.com/lightvector/leela-analysis
基于python2的leela分析程序，已经试用中，但是leela的版本是0.10的，作者不提供以后的版本支持。
####
https://github.com/jumpman24/sgf-analyzer
在以上版本基础上进行的升级，基于python3的leela分析程序，还未深入研究

####
https://github.com/fohristiwhirl/leela_zero_analysis
> python代码，通过gtp和ai交互，并获得胜率，同时提供胜率的折线图输出

####
https://github.com/sanderland/katrain
