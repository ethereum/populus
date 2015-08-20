contract owned {
        address owner;

        function owned() {
                owner = msg.sender;
        }
}
