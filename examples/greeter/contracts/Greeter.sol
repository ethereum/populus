contract Greeter {
    string public greeting;

    function Greeter() {
        greeting = "Hello";
    }

    function setGreeting(string _greeting) public {
        greeting = _greeting;
    }

    function greet() constant returns (string) {
        return greeting;
    }

    function greet(bytes name) constant returns (bytes) {
        // create a byte array sufficiently large to store our greeting.
        bytes memory namedGreeting = new bytes(
            name.length + 1 + bytes(greeting).length
        );

        // push the greeting onto our return value.
        // greeting.
        for (uint i=0; i < bytes(greeting).length; i++) {
            namedGreeting[i] = bytes(greeting)[i];
        }

        // add a space before pushing the name on.
        namedGreeting[bytes(greeting).length] = ' ';

        // loop over the name and push all of the characters onto the
        // greeting.
        for (i=0; i < name.length; i++) {
            namedGreeting[bytes(greeting).length + 1 + i] = name[i];
        }
        return namedGreeting;
    }
}
