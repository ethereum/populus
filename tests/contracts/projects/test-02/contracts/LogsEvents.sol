contract LogsEvents {
        event SingleIndex(bytes32 indexed key, bytes32 val_a, uint val_b);

        function logSingleIndex(bytes32 key, bytes32 val_a, uint val_b) public {
                SingleIndex(key, val_a, val_b);
        }

        event DoubleIndex(bytes32 indexed key_a, bytes32 indexed key_b, bytes32 val_a, uint val_b);

        function logDoubleIndex(bytes32 key_a, bytes32 key_b, bytes32 val_a, uint val_b) public {
                DoubleIndex(key_a, key_b, val_a, val_b);
        }

        event Anonymous(bytes32 indexed key_a, bytes32 indexed key_b, bytes32 val_a, uint val_b) anonymous;

        function logAnonymous(bytes32 key_a, bytes32 key_b, bytes32 val_a, uint val_b) public {
                Anonymous(key_a, key_b, val_a, val_b);
        }
}
