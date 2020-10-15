# PyCACTUS

A Python-based, functional eQASM simulator without modeling timing behavior.


# Supported Instructions

## Floating-Point (FP) Instructions
### Conversion
```
FCVT.W.S rd, fs
```
Convert the 32-bit FP number in fs into a 32-bit signed integer, and store it in rd.

```
FCVT.S.W fd, rs
```
Convert a 32-bit signed integer in rs into a 32-bit FP number, and store it in fd.

### Load & Store

```
FLW fd, imm(rs)
```
Load a 32-bit FP number from the memory address `imm + rs` and store it to the FP register `fd`.

```
FSW fs, imm(rs)
```
Store `fs` to `imm + rs`.

### Arithmetic
```
FADD.S fd, fs, ft
FSUB.S fd, fs, ft
FMUL.S fd, fs, ft
FDIV.S fd, fs, ft

```
FP addition/subtraction/multiplication/division.


### Comparison
```
FEQ.S rd, fs, ft
FLT.S rd, fs, ft
FLE.S rd, fs, ft
```
Set rd when `fs` is equal to/less than/less equal to `ft`.