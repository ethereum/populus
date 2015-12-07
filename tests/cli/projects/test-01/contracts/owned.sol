contract owned {
        address owner;

        function Owned() {
                owner = msg.sender;
        }
}
