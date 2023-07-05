; ModuleID = 'main.aleo'
source_filename = "./test/toy-examples/adder/main.aleo"

define i64 @deposit(i128 %self.caller, i64 %r0, i64 %r1) {
entry:
  %self.caller1 = alloca i128, align 8
  store i128 %self.caller, i128* %self.caller1, align 4
  %r02 = alloca i64, align 8
  store i64 %r0, i64* %r02, align 4
  %r13 = alloca i64, align 8
  store i64 %r1, i64* %r13, align 4
  br label %body

body:                                             ; preds = %entry
  %load = load i64, i64* %r02, align 4
  %load4 = load i64, i64* %r13, align 4
  %sub = sub i64 %load, %load4
  %r2 = alloca i64, align 8
  store i64 %sub, i64* %r2, align 4
  br label %exit

exit:                                             ; preds = %body
  %load5 = load i64, i64* %r2, align 4
  ret i64 %load5
}

define i64 @deposit_safe(i128 %self.caller, i64 %r0, i64 %r1) {
entry:
  %self.caller1 = alloca i128, align 8
  store i128 %self.caller, i128* %self.caller1, align 4
  %r02 = alloca i64, align 8
  store i64 %r0, i64* %r02, align 4
  %r13 = alloca i64, align 8
  store i64 %r1, i64* %r13, align 4
  br label %body

body:                                             ; preds = %entry
  %load = load i64, i64* %r02, align 4
  %load4 = load i64, i64* %r13, align 4
  %gte = icmp sge i64 %load, %load4
  %r2 = alloca i64, align 8
  %zext = zext i1 %gte to i64
  store i64 %zext, i64* %r2, align 4
  %load5 = load i64, i64* %r2, align 4
  call void @aleo.assert.eq.i64.i1(i64 %load5, i1 true)
  %load6 = load i64, i64* %r02, align 4
  %load7 = load i64, i64* %r13, align 4
  %sub = sub i64 %load6, %load7
  %r3 = alloca i64, align 8
  store i64 %sub, i64* %r3, align 4
  br label %exit

exit:                                             ; preds = %body
  %load8 = load i64, i64* %r3, align 4
  ret i64 %load8
}

declare void @aleo.assert.eq.i64.i1(i64, i1)
