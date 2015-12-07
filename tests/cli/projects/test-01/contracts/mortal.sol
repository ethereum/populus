import "owned";


contract Mortal is owned {
        function kill() {
                suicide(msg.sender);
        }
}


contract Immortal is owned {
        function kill() returns (bool no){
                return false;
        }
}
