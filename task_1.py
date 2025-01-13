import logging
from colorama import init, Fore
from typing import Any, Dict

# Initialize colorama and logger
init(autoreset=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
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

    def put(self, word: str, value=None):
        """
        Insert a word into the trie.
        'value' can be any associated data (e.g., index).
        """
        if not isinstance(word, str):
            logger.error(Fore.RED + "put(...) error: 'word' must be a string.")
            return

        current = self.root
        for ch in word:
            if ch not in current:
                current[ch] = {}
            current = current[ch]
        # Позначаємо кінець слова
        current[self.endSymbol] = value

    def get(self, word: str):
        """
        Get the associated value with 'word' if it exists in the trie,
        otherwise return None.
        """
        if not isinstance(word, str):
            logger.error(Fore.RED + "get(...) error: 'word' must be a string.")
            return None

        current = self.root
        for ch in word:
            if ch not in current:
                return None
            current = current[ch]

        # Перевіряємо, чи закінчується слово
        return current.get(self.endSymbol, None)

    def _collect_all_words(self) -> list:
        """
        Collect all words stored in the trie (for demonstration).
        Returns a list of (word, value).
        """
        collected = []

        def _dfs(node, path):
            # Якщо дійшли до кінця слова
            if self.endSymbol in node:
                collected.append((path, node[self.endSymbol]))

            for ch in node:
                if ch == self.endSymbol:
                    continue
                _dfs(node[ch], path + ch)

        _dfs(self.root, "")
        return collected


class Homework(Trie):
    """
    Extended Trie with two additional methods:
      1. count_words_with_suffix(pattern)
      2. has_prefix(prefix)
    """

    def count_words_with_suffix(self, pattern: str) -> int:
        """
        Return how many words in the trie end with the given 'pattern'.
        Case-sensitive. If no words match or pattern is invalid, returns 0.
        """
        if not isinstance(pattern, str):
            logger.error(Fore.RED + "count_words_with_suffix(...) error: 'pattern' must be a string.")
            return 0

        # Збираємо всі слова, потім перевіряємо суфікс
        all_words = self._collect_all_words()  # list of (word, value)
        count = 0
        for (word, _val) in all_words:
            if word.endswith(pattern):
                count += 1
        return count

    def has_prefix(self, prefix: str) -> bool:
        """
        Return True if there's at least one word starting with 'prefix'.
        Case-sensitive. If invalid prefix, return False.
        """
        if not isinstance(prefix, str):
            logger.error(Fore.RED + "has_prefix(...) error: 'prefix' must be a string.")
            return False

        current = self.root
        for ch in prefix:
            if ch not in current:
                return False
            current = current[ch]
        return True


def main():
    logger.info(Fore.CYAN + "=== Starting Trie Homework Demo ===")

    trie = Homework()

    words = ["apple", "application", "banana", "cat"]
    for i, word in enumerate(words):
        trie.put(word, i)

    # Testing count_words_with_suffix
    assert trie.count_words_with_suffix("e") == 1      # "apple"
    assert trie.count_words_with_suffix("ion") == 1    # "application"
    assert trie.count_words_with_suffix("a") == 1      # "banana"
    assert trie.count_words_with_suffix("at") == 1     # "cat"

    # Testing has_prefix
    assert trie.has_prefix("app") is True   # "apple", "application"
    assert trie.has_prefix("bat") is False
    assert trie.has_prefix("ban") is True   # "banana"
    assert trie.has_prefix("ca") is True    # "cat"

    logger.info(Fore.GREEN + "All tests passed successfully!")

    # Optional: let's show all words:
    all_w = trie._collect_all_words()
    logger.info(Fore.MAGENTA + f"Words in trie: {all_w}")


if __name__ == "__main__":
    main()
