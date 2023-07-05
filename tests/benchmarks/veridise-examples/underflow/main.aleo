// The 'underflow.aleo' program.
program underflow.aleo;

function deposit:
    input r0 as u64.private;
    input r1 as u64.private;
    sub r0 r1 into r2;
    output r2 as u64.private;

function deposit_safe:
    input r0 as u64.private;
    input r1 as u64.private;
    // underflow check
    gte r0 r1 into r2;
    assert.eq r2 true;
    sub r0 r1 into r3;
    output r3 as u64.private;