from __future__ import annotations

import re
import unicodedata
from collections import deque


class RealtimePhraseSegmenter:
    """Cuts long STT chunks into smaller real-time phrases.

    In video translation mode the segmenter does not cut phrases by word/char limits.
    It waits for final/speech_final from Deepgram and sends the phrase as-is.
    """

    def __init__(
        self,
        *,
        max_words: int = 14,
        max_chars: int = 95,
        min_interim_words: int = 8,
        min_interim_chars: int = 58,
        min_words: int = 2,
        video_translation_mode: bool = False,
    ):
        self.max_words = max_words
        self.max_chars = max_chars
        self.min_interim_words = min_interim_words
        self.min_interim_chars = min_interim_chars
        self.min_words = min_words
        self.video_translation_mode = bool(video_translation_mode)

        self._recent_norms: deque[str] = deque(maxlen=18)

    def configure(self, *, video_translation_mode: bool = False) -> None:
        self.video_translation_mode = bool(video_translation_mode)
        self.reset()

    def reset(self) -> None:
        self._recent_norms.clear()

    def push(self, text: str, *, is_final: bool, speech_final: bool = False) -> list[str]:
        clean = self._clean_text(text)
        if not clean:
            return []

        if self.video_translation_mode:
            return self._push_video_mode(clean, is_final=is_final, speech_final=speech_final)

        force = bool(is_final or speech_final)

        if not force and not self._should_flush_interim(clean):
            return []

        segments = self._split_text(clean, force=force)
        accepted: list[str] = []

        for segment in segments:
            segment = self._clean_text(segment)
            if not self._is_useful(segment):
                continue

            if self._already_emitted(segment):
                continue

            self._recent_norms.append(self._normalize(segment))
            accepted.append(segment)

        return accepted

    def _push_video_mode(self, text: str, *, is_final: bool, speech_final: bool) -> list[str]:
        if not (is_final or speech_final):
            return []

        clean = self._clean_text(text)
        if not self._is_useful(clean):
            return []

        if self._already_emitted(clean):
            return []

        self._recent_norms.append(self._normalize(clean))
        return [clean]

    def _should_flush_interim(self, text: str) -> bool:
        words = self._words(text)

        if len(words) >= self.max_words:
            return True

        if len(text) >= self.max_chars:
            return True

        if len(words) >= self.min_interim_words and self._has_good_boundary(text):
            return True

        if len(text) >= self.min_interim_chars and self._has_good_boundary(text):
            return True

        return False

    def _split_text(self, text: str, *, force: bool) -> list[str]:
        if force:
            return self._split_final_text(text)

        complete, tail = self._complete_boundary_part(text)

        if complete:
            segments = self._split_final_text(complete)
            if segments:
                return segments

        if len(self._words(text)) >= self.max_words or len(text) >= self.max_chars:
            return [self._cut_by_limit(text)]

        if tail and (len(self._words(tail)) >= self.max_words or len(tail) >= self.max_chars):
            return [self._cut_by_limit(tail)]

        return []

    def _split_final_text(self, text: str) -> list[str]:
        parts = self._sentence_parts(text)
        result: list[str] = []
        current = ""

        for part in parts:
            part = self._clean_text(part)
            if not part:
                continue

            candidate = self._clean_text(f"{current} {part}") if current else part

            if self._fits(candidate):
                current = candidate
                continue

            if current:
                result.extend(self._split_oversized(current))

            if self._fits(part):
                current = part
            else:
                result.extend(self._split_oversized(part))
                current = ""

        if current:
            result.extend(self._split_oversized(current))

        return result

    def _split_oversized(self, text: str) -> list[str]:
        words = self._words(text)
        if len(words) <= self.max_words and len(text) <= self.max_chars:
            return [text]

        # Languages such as Japanese and Chinese may not contain spaces.
        # Cut long compact-script phrases by characters instead of returning
        # one huge unsplittable "word".
        if self._has_compact_script(text) and len(words) <= 1:
            return self._split_compact_script_text(text)

        chunks: list[str] = []
        current_words: list[str] = []

        for word in words:
            candidate_words = [*current_words, word]
            candidate = " ".join(candidate_words)

            if current_words and (
                len(candidate_words) > self.max_words or len(candidate) > self.max_chars
            ):
                chunks.append(" ".join(current_words))
                current_words = [word]
            else:
                current_words = candidate_words

        if current_words:
            chunks.append(" ".join(current_words))

        return chunks

    def _split_compact_script_text(self, text: str) -> list[str]:
        clean = self._clean_text(text)
        if not clean:
            return []

        chunks: list[str] = []
        start = 0

        while start < len(clean):
            end = min(start + self.max_chars, len(clean))
            if end < len(clean):
                boundary = self._find_compact_boundary(clean, start, end)
                if boundary > start:
                    end = boundary

            chunk = clean[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end

        return chunks

    def _find_compact_boundary(self, text: str, start: int, end: int) -> int:
        punctuation = "。！？!?、，,；;：:"
        floor = start + max(1, int((end - start) * 0.55))

        for index in range(end - 1, floor - 1, -1):
            if text[index] in punctuation:
                return index + 1

        return end

    def _cut_by_limit(self, text: str) -> str:
        words = self._words(text)
        if not words:
            return ""

        if self._has_compact_script(text) and len(words) <= 1:
            return text[: self.max_chars].strip()

        selected: list[str] = []

        for word in words:
            candidate = " ".join([*selected, word])
            if selected and (
                len(selected) + 1 > self.max_words or len(candidate) > self.max_chars
            ):
                break
            selected.append(word)

        return " ".join(selected)

    def _complete_boundary_part(self, text: str) -> tuple[str, str]:
        matches = list(re.finditer(r"[.!?。！？]\s*", text))
        if not matches:
            if text.rstrip().endswith((".", "!", "?", "。", "！", "？")):
                return text.strip(), ""
            return "", text

        end = matches[-1].end()
        return text[:end].strip(), text[end:].strip()

    def _sentence_parts(self, text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?。！？])\s*", text)
        return [part.strip() for part in parts if part.strip()]

    def _has_good_boundary(self, text: str) -> bool:
        clean = text.strip()
        if clean.endswith((".", "!", "?", "。", "！", "？")):
            return True

        return bool(re.search(r"[,，、]\s*\S+$", clean)) and (
            len(self._words(clean)) >= self.min_interim_words
            or self._has_compact_script(clean)
        )

    def _fits(self, text: str) -> bool:
        return len(self._words(text)) <= self.max_words and len(text) <= self.max_chars

    def _is_useful(self, text: str) -> bool:
        words = self._words(text)

        if self._has_compact_script(text):
            # Japanese/Chinese/Korean can be a valid phrase without spaces.
            return self._compact_script_char_count(text) >= 2

        if len(words) < self.min_words:
            return False

        normalized_words = {self._normalize(word) for word in words if self._normalize(word)}
        if len(words) <= 2 and len(normalized_words) <= 1:
            return False

        return True

    def _already_emitted(self, text: str) -> bool:
        norm = self._normalize(text)
        if not norm:
            return True

        for old in self._recent_norms:
            if norm == old:
                return True

            if len(norm) >= 18 and (norm in old or old in norm):
                return True

            if self._word_overlap(norm, old) >= 0.82:
                return True

        return False

    def _word_overlap(self, left: str, right: str) -> float:
        left_words = set(left.split())
        right_words = set(right.split())

        if len(left_words) < 3 or len(right_words) < 3:
            return 0.0

        return len(left_words & right_words) / max(
            1,
            min(len(left_words), len(right_words)),
        )

    def _clean_text(self, text: str) -> str:
        clean = str(text or "").replace("\n", " ")
        clean = re.sub(r"\s+", " ", clean)
        return clean.strip()

    def _words(self, text: str) -> list[str]:
        # Unicode-aware word extraction. The old ASCII/Cyrillic-only regex
        # silently removed Japanese, Chinese, Korean, Arabic, etc.
        return re.findall(r"[^\W_]+(?:['’][^\W_]+)*", str(text or ""), flags=re.UNICODE)

    def _normalize(self, text: str) -> str:
        # Preserve letters and digits from every Unicode script.
        normalized = unicodedata.normalize("NFKC", str(text or "")).casefold()

        result: list[str] = []
        for char in normalized:
            if char.isalnum() or char in {"'", "’"}:
                result.append(char)
            else:
                result.append(" ")

        return re.sub(r"\s+", " ", "".join(result)).strip()

    def _has_compact_script(self, text: str) -> bool:
        return self._compact_script_char_count(text) > 0

    def _compact_script_char_count(self, text: str) -> int:
        return sum(1 for char in str(text or "") if self._is_compact_script_char(char))

    def _is_compact_script_char(self, char: str) -> bool:
        code = ord(char)
        return (
            0x3040 <= code <= 0x309F  # Hiragana
            or 0x30A0 <= code <= 0x30FF  # Katakana
            or 0x31F0 <= code <= 0x31FF  # Katakana extensions
            or 0x3400 <= code <= 0x4DBF  # CJK extension A
            or 0x4E00 <= code <= 0x9FFF  # CJK unified ideographs
            or 0xAC00 <= code <= 0xD7AF  # Hangul syllables
        )
