import logging
import re

logger = logging.getLogger(__name__)

_WORD_RE = re.compile(r"[a-zA-Z]+")
_PATTERN_RE = re.compile(r"[a-zA-Z?*]+")


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

    def _walk(self, chars: str) -> TrieNode | None:
        """ 走樹邏輯 """
        node = self._root
        for char in chars:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def _match(self, node: TrieNode, pattern: str, i: int) -> bool:
        pattern_len = len(pattern)
        # base case: pattern停在完整字上
        if i == pattern_len:
            return node.is_word
        char = pattern[i]

        if char == "*":
            # 跳過 *，node 不動、i+1
            if self._match(node, pattern, i + 1):
                return True
            # 歷遍child，* 保留
            for child in node.children.values():
                if self._match(child, pattern, i):
                    return True
            return False

        if char == "?":
            # single char = any child
            for child in node.children.values():
                if self._match(child, pattern, i + 1):
                    return True
            return False

        # 不是特殊字符
        child = node.children.get(char)
        return self._match(child, pattern, i + 1) if child else False

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

    def contains(self, word: str) -> bool:
        if not isinstance(word, str):
            raise TypeError(f"contains() expects str, got {type(word).__name__}")
        node = self._walk(word)  # 走樹邏輯
        result = node is not None and node.is_word  # check word flag
        logger.debug(f"input={word!r} output={result!r}")
        return result

    def startswith(self, word: str) -> bool:
        if not isinstance(word, str):
            raise TypeError(f"startswith() expects str, got {type(word).__name__}")
        node = self._walk(word)  # 走樹邏輯
        result = node is not None and (node.is_word or bool(node.children))
        logger.debug(f"input={word!r} output={result!r}")
        return result

    def search(self, word: str) -> bool:
        if not isinstance(word, str):
            raise TypeError(f"search() expects str, got {type(word).__name__}")
        if not _PATTERN_RE.fullmatch(word):
            logger.warning(f"invalid pattern={word!r}")
            return False
        result = self._match(self._root, word, 0)
        logger.debug(f"input={word!r} output={result!r}")
        return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(funcName)-10s | %(message)s",
    )
    wd = WordDictionary()
    wd.setup(["cat", "car", "bar"])
    wd.contains("cat")
    wd.contains("ca")
    wd.contains("Cat")
    wd.startswith("ca")
    wd.startswith("cr")
    wd.search("c?t")
    wd.search("*at")
    wd.search("ca*")
    wd.search("cr*")
    wd.search("*")
