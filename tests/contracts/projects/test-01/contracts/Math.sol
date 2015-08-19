contract Math {
        function add(int a, int b) public returns (int result){
            result = a + b;
            return result;
        }

        function multiply7(int a) public returns (int result){
            result = a * 7;
            return result;
        }

        function return13() public returns (int result) {
            result = 13;
            return result;
        }
}
