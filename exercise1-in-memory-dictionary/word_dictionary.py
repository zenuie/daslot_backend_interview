import logging
import re

logger = logging.getLogger(__name__)

_WORD_RE = re.compile(r"[a-zA-Z]+")


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_word: bool = False


def _is_valid_word(word: str) -> bool:
    return _WORD_RE.fullmatch(word) is not None


class WordDictionary:
    def __init__(self):
        self._root = TrieNode()

    # setup / contains / startsWith / search 見下
    def setup(self, words: list[str]) -> None:
        """ 建立基礎樹 """
        if not isinstance(words, list):
            raise TypeError(f"setup() expects a list of str, got {type(words).__name__}")

        new_root = TrieNode()
        for word in words:
            if not isinstance(word, str):  # type check
                raise TypeError(f"setup() word must be str, got {type(word).__name__}: {word!r}")
            if not _is_valid_word(word):
                logger.warning(f"skipped invalid word={word!r}")
                continue
            node = new_root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_word = True
        self._root = new_root  # Calling setup again replaces the previous dictionary contents
        logger.info(f"input={words!r}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(funcName)-10s | %(message)s",
    )
    wd = WordDictionary()
    wd.setup(["cat", "car", "bar"])
