import logging
from colorama import init, Fore
from typing import Any, Dict

# ==============================
# Initialize colorama and logger
# ==============================
init(autoreset=True)
logging.basicConfig(
    level=logging.INFO,  # можна змінити на DEBUG для більш докладних логів
    format="%(asctime)s - [%(levelname)s] - %(message)s",
)
logger = logging.getLogger(__name__)


class Trie:
    """
    A simple Trie (prefix tree) implementation.
    Each node is a dictionary:
      - Keys: characters
      - Special key '*' (self.endSymbol) indicates the end of a word
    """

    def __init__(self):
        self.root: Dict[str, Any] = {}
        self.endSymbol = "*"

    def put(self, word: str):
        """
        Insert a word into the trie.
        """
        logger.info(Fore.BLUE + f"Inserting word: {word}")
        current = self.root
        for ch in word:
            if ch not in current:
                current[ch] = {}
                logger.debug(Fore.BLUE + f"[put] Created new node for char '{ch}'")
            else:
                logger.debug(Fore.BLUE + f"[put] Found existing node for char '{ch}'")
            current = current[ch]
        # Mark the end of the word
        current[self.endSymbol] = True
        logger.debug(Fore.BLUE + "[put] Marked end of word here")


class LongestCommonWord(Trie):
    """
    Inherited class from Trie that finds the longest common prefix
    among all strings in a given list.
    """

    def find_longest_common_word(self, strings) -> str:
        """
        Return the longest common prefix among all words in 'strings'.
        If no common prefix, return an empty string.
        Complexity: O(S), where S is the sum of all input strings' lengths.
        """
        logger.info(Fore.CYAN + "Starting find_longest_common_word...")
        # Validate input
        if not isinstance(strings, list):
            logger.error(
                Fore.RED
                + "[LCP] 'strings' must be a list of str. Returning empty prefix."
            )
            return ""

        if not strings:
            logger.info(Fore.CYAN + "[LCP] Empty list of strings => ''")
            return ""

        if len(strings) == 1:
            logger.info(
                Fore.CYAN + f"[LCP] Only one string => returning it: '{strings[0]}'"
            )
            return strings[0]

        # Insert all words into the trie
        logger.info(Fore.CYAN + f"[LCP] Building Trie from {len(strings)} strings...")
        for s in strings:
            if not isinstance(s, str):
                logger.error(
                    Fore.RED
                    + f"[LCP] Invalid element '{s}' in strings: must be str. => ''"
                )
                return ""
            self.put(s)

        # Now traverse the trie from the root and collect the LCP
        prefix = ""
        current = self.root

        while True:
            node_keys = list(current.keys())
            logger.debug(Fore.YELLOW + f"[LCP-Traverse] Current node keys: {node_keys}")

            # Якщо натрапили на endSymbol або кількість дітей != 1 — зупиняємося
            if self.endSymbol in current or len(node_keys) != 1:
                logger.debug(
                    Fore.YELLOW
                    + "[LCP-Traverse] Stopping (found endSymbol or !=1 child)."
                )
                break

            # Беремо єдиного нащадка
            (ch,) = node_keys
            prefix += ch
            logger.debug(Fore.YELLOW + f"[LCP-Traverse] Extending prefix => '{prefix}'")
            current = current[ch]

        logger.info(Fore.GREEN + f"[LCP] Longest common prefix => '{prefix}'")
        return prefix


def run_test(strings, expected):
    """
    Helper function to test the LCP method with logging.
    """
    logger.info(Fore.MAGENTA + f"Test with input: {strings}")
    trie = LongestCommonWord()
    result = trie.find_longest_common_word(strings)
    logger.info(Fore.MAGENTA + f"Result: '{result}', Expected: '{expected}'")
    assert result == expected, f"Expected '{expected}' but got '{result}'"
    logger.info(Fore.GREEN + "Test passed!\n")


def main():
    """
    We have multiple tests:
    1) Non-empty common prefix
    2) No common prefix
    3) Empty array
    4) Invalid data
    """
    logger.info(Fore.CYAN + "=== Starting Tests for LongestCommonWord ===")

    # 1) Non-empty common prefix
    run_test(["flower", "flow", "flight"], "fl")
    run_test(["interspecies", "interstellar", "interstate"], "inters")

    # 2) No common prefix
    run_test(["dog", "racecar", "car"], "")

    # 3) Empty array
    run_test([], "")

    # 4) Invalid data => e.g. not a list or not a list of strings
    logger.info(Fore.MAGENTA + "Test with invalid data (None)...")
    trie = LongestCommonWord()
    res = trie.find_longest_common_word(None)
    logger.info(Fore.MAGENTA + f"Result: '{res}', Expected: ''")
    assert res == "", f"Expected '' but got '{res}'"
    logger.info(Fore.GREEN + "Invalid data test #1 passed!\n")

    logger.info(Fore.MAGENTA + "Test with partially invalid data (list + int)...")
    trie = LongestCommonWord()
    res = trie.find_longest_common_word(["abc", 123, "abd"])
    logger.info(Fore.MAGENTA + f"Result: '{res}', Expected: ''")
    assert res == "", f"Expected '' but got '{res}'"
    logger.info(Fore.GREEN + "Invalid data test #2 passed!\n")

    logger.info(
        Fore.GREEN + "=== All tests for LongestCommonWord passed successfully! ==="
    )


if __name__ == "__main__":
    main()
