"""Shared puzz.link codecs."""
from typing import Dict, List, Tuple

class Number3Codec:
    """
    number3 format codec: packs 3 trits (0/1/2) into one base36 character.

    Each character encodes: a*9 + b*3 + c where a,b,c are trits.
    """

    @staticmethod
    def _int_to_base36(val: int) -> str:
        """Convert integer 0-35 to base36 character."""
        if 0 <= val <= 9:
            return str(val)
        return chr(ord("a") + val - 10)

    def decode(self, body: str, max_iter: int = -1) -> List[int]:
        """Decode number3 format to list of trits (0/1/2).

        Args:
            body: The number3-encoded string
            max_iter: Maximum number of characters to decode (-1 for all)

        Returns:
            List of trits (0/1/2), length = chars_decoded * 3
        """
        number_list = []

        for char in body:
            if max_iter == 0:
                break

            num = int(char, 36)
            number_list.extend([
                (num // 9) % 3,
                (num // 3) % 3,
                (num // 1) % 3
            ])

            max_iter -= 1

        return number_list

    def encode(self, number_list: List[int]) -> str:
        """Encode list of trits to number3 format string.

        Args:
            number_list: List of trits (0/1/2)

        Returns:
            number3-encoded string
        """
        if not number_list:
            return ""

        result: List[str] = []
        i = 0
        while i < len(number_list):
            a = number_list[i] if i < len(number_list) else 0
            b = number_list[i + 1] if i + 1 < len(number_list) else 0
            c = number_list[i + 2] if i + 2 < len(number_list) else 0
            packed = a * 9 + b * 3 + c
            result.append(self._int_to_base36(packed))
            i += 3

        return "".join(result)


class BorderCodec:
    """
    Border format codec: bit-packed base32 encoding.

    Each border is represented as 1 bit (present/absent).
    Every 5 bits are packed into one base32 character.
    """

    _BIT_MASKS = [16, 8, 4, 2, 1]  # 5-bit mask for extraction

    @staticmethod
    def _int_to_base32(val: int) -> str:
        """Convert integer 0-31 to base32 character (0-9, a-v)."""
        if 0 <= val <= 9:
            return str(val)
        elif 10 <= val <= 31:
            return chr(ord('a') + val - 10)
        else:
            raise ValueError(f"Value {val} out of range for base32 (0-31)")

    @staticmethod
    def _base32_to_int(char: str) -> int:
        """Convert base32 character to integer 0-31."""
        return int(char, 32)

    def decode(self, body: str, num_rows: int, num_cols: int) -> Tuple[Dict[int, int], int]:
        """Decode border string to {border_id: 1} dict.

        Args:
            body: The base32-encoded border string
            num_rows: Number of rows in the grid
            num_cols: Number of columns in the grid

        Returns:
            Tuple of (border_dict, consumed_length)
        """
        border_list = {}
        id_counter = 0

        # Calculate border counts
        num_vert_borders = (num_cols - 1) * num_rows
        num_horiz_borders = num_cols * (num_rows - 1)

        # Calculate string length (ceil division by 5)
        pos1 = (num_vert_borders + 4) // 5
        pos2 = pos1 + (num_horiz_borders + 4) // 5

        # Extract relevant portion
        border_str = body[:pos2]

        # Parse vertical borders
        for i in range(pos1):
            if i >= len(border_str):
                break
            val = self._base32_to_int(border_str[i])

            for w in range(5):
                if id_counter < num_vert_borders:
                    if val & self._BIT_MASKS[w]:
                        border_list[id_counter] = 1
                    id_counter += 1

        # Parse horizontal borders
        start_horiz_id = num_vert_borders
        id_counter = start_horiz_id

        for i in range(pos1, pos2):
            if i >= len(border_str):
                break
            val = self._base32_to_int(border_str[i])

            for w in range(5):
                if id_counter < start_horiz_id + num_horiz_borders:
                    if val & self._BIT_MASKS[w]:
                        border_list[id_counter] = 1
                    id_counter += 1

        return border_list, pos2

    def encode(self, border_list: Dict[int, int], num_rows: int, num_cols: int) -> str:
        """Encode border dict to base32 string.

        Args:
            border_list: Dict mapping border ID to 1 (or truthy value)
            num_rows: Number of rows in the grid
            num_cols: Number of columns in the grid

        Returns:
            base32-encoded border string
        """
        num_vert_borders = (num_cols - 1) * num_rows
        num_horiz_borders = num_cols * (num_rows - 1)
        total_borders = num_vert_borders + num_horiz_borders

        # Build bit array
        bits = [0] * total_borders
        for border_id in border_list:
            if 0 <= border_id < total_borders:
                bits[border_id] = 1

        result_chars = []

        # Encode vertical borders
        for i in range(0, num_vert_borders, 5):
            val = 0
            for w in range(5):
                if i + w < num_vert_borders and bits[i + w]:
                    val |= self._BIT_MASKS[w]
            result_chars.append(self._int_to_base32(val))

        # Encode horizontal borders
        for i in range(num_vert_borders, total_borders, 5):
            val = 0
            for w in range(5):
                if i + w < total_borders and bits[i + w]:
                    val |= self._BIT_MASKS[w]
            result_chars.append(self._int_to_base32(val))

        return ''.join(result_chars)
