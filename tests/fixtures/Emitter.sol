pragma solidity ^0.4.0;


contract Emitter {
    event LogAnonymous() anonymous;
    event LogNoArguments();
    event LogSingleArg(uint arg0);
    event LogDoubleArg(uint arg0, uint arg1);
    event LogTripleArg(uint arg0, uint arg1, uint arg2);
    event LogQuadrupleArg(uint arg0, uint arg1, uint arg2, uint arg3);

    // Indexed
    event LogSingleWithIndex(uint indexed arg0);
    event LogDoubleWithIndex(uint arg0, uint indexed arg1);
    event LogTripleWithIndex(uint arg0, uint indexed arg1, uint indexed arg2);
    event LogQuadrupleWithIndex(uint arg0, uint arg1, uint indexed arg2, uint indexed arg3);

    enum WhichEvent {
        LogAnonymous,
        LogNoArguments,
        LogSingleArg,
        LogDoubleArg,
        LogTripleArg,
        LogQuadrupleArg,
        LogSingleWithIndex,
        LogDoubleWithIndex,
        LogTripleWithIndex,
        LogQuadrupleWithIndex
    }

    function logNoArgs(WhichEvent which) public {
        if (which == WhichEvent.LogNoArguments) LogNoArguments();
        else if (which == WhichEvent.LogAnonymous) LogAnonymous();
        else throw;
    }

    function logSingle(WhichEvent which, uint arg0) public {
        if (which == WhichEvent.LogSingleArg) LogSingleArg(arg0);
        else if (which == WhichEvent.LogSingleWithIndex) LogSingleWithIndex(arg0);
        else throw;
    }

    function logDouble(WhichEvent which, uint arg0, uint arg1) public {
        if (which == WhichEvent.LogDoubleArg) LogDoubleArg(arg0, arg1);
        else if (which == WhichEvent.LogDoubleWithIndex) LogDoubleWithIndex(arg0, arg1);
        else throw;
    }

    function logTriple(WhichEvent which, uint arg0, uint arg1, uint arg2) public {
        if (which == WhichEvent.LogTripleArg) LogTripleArg(arg0, arg1, arg2);
        else if (which == WhichEvent.LogTripleWithIndex) LogTripleWithIndex(arg0, arg1, arg2);
        else throw;
    }

    function logQuadruple(WhichEvent which, uint arg0, uint arg1, uint arg2, uint arg3) public {
        if (which == WhichEvent.LogQuadrupleArg) LogQuadrupleArg(arg0, arg1, arg2, arg3);
        else if (which == WhichEvent.LogQuadrupleWithIndex) LogQuadrupleWithIndex(arg0, arg1, arg2, arg3);
        else throw;
    }
}
